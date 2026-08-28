"""End-to-end checks that run the preparation pipeline on the fixture source.

These tests need only pandas and numpy, so they guard the data contract even in an
environment without scikit-learn, XGBoost or the real 50k-row source file.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pandas as pd
import pytest

from src.data import prepare_dataset as prepare_module
from src.modeling import features as features_module
from src.modeling.features import (
    ATTRITION_FORBIDDEN_COLUMNS,
    PLACEMENT_FORBIDDEN_COLUMNS,
    build_placement_frame,
    feature_contract_fingerprint,
    load_role_requirements,
    placement_api_frame,
    skill_gap_analysis,
    skills_to_text,
    training_performance,
)

EXPECTED_TABLES = {
    "attrition_training_snapshot", "employment_spells", "engagement_checkins", "job_demand_snapshots",
    "job_search_events", "placement_training_snapshot", "role_skill_requirements", "salary_history",
    "skill_gap_details", "trainee_skills", "trainees", "training_completions", "wage_progression_outcomes",
}


def test_pipeline_publishes_every_table_with_both_label_classes(prepared: dict) -> None:
    assert set(prepared["tables"]) == EXPECTED_TABLES
    report = prepared["report"]
    assert 0 < report["labels"]["placement_positive_rate"] < 1
    assert 0 < report["labels"]["attrition_positive_rate"] < 1
    assert report["feature_completeness"]["attrition_engagement_missing_rate"] == 0.0
    assert "all tables committed together" in report["checks_passed"]


def test_model_views_hold_no_outcome_columns(prepared: dict) -> None:
    tables = prepared["tables"]
    assert not PLACEMENT_FORBIDDEN_COLUMNS & set(tables["placement_training_snapshot"].columns)
    assert not ATTRITION_FORBIDDEN_COLUMNS & set(tables["attrition_training_snapshot"].columns)
    # Wage growth is a deterministic function of the retention label, so it belongs to the
    # outcome table and must not reappear as a feature.
    assert "Wage_Growth_Percent" in tables["wage_progression_outcomes"].columns
    assert tables["wage_progression_outcomes"]["Data_Origin"].eq("outcome_metric_not_a_feature").all()


def test_attrition_rows_are_observed_before_the_event_they_predict(prepared: dict) -> None:
    attrition = prepared["tables"]["attrition_training_snapshot"]
    spells = prepared["tables"]["employment_spells"]
    merged = attrition.merge(spells[["Employment_ID", "Start_Date", "End_Date"]], on="Employment_ID", how="left")
    observed = pd.to_datetime(merged["Snapshot_Observed_On"])
    assert (observed >= pd.to_datetime(merged["Start_Date"])).all()
    assert (observed < pd.to_datetime(merged["End_Date"]).fillna(pd.Timestamp.max)).all()
    assert (observed <= prepare_module.AS_OF_DATE).all()
    # Each snapshot must sit on one of the declared checkpoints, so the duration feature
    # cannot leak the outcome by being longer for survivors.
    offsets = (observed - pd.to_datetime(merged["Start_Date"])).dt.days.unique()
    assert set(offsets).issubset(set(prepare_module.ATTRITION_CHECKPOINT_DAYS.tolist()))
    assert attrition["Employment_ID"].is_unique


def test_skills_text_is_identical_in_training_and_serving(prepared: dict) -> None:
    skills = prepared["tables"]["trainee_skills"]
    snapshot = prepared["tables"]["placement_training_snapshot"]
    for trainee_id in snapshot["Trainee_ID"].head(25):
        names = skills.loc[skills["Trainee_ID"].eq(trainee_id), "Skill"].tolist()
        stored = snapshot.loc[snapshot["Trainee_ID"].eq(trainee_id), "Skills_Text"].iloc[0]
        assert stored == skills_to_text(names)
    # Serving-side casing and spacing must collapse to the same tokens as training.
    assert skills_to_text(["Power BI", "python", "POWER  bi"]) == "power_bi python"


def _api_payload(snapshot_row: pd.Series, skills: pd.DataFrame) -> dict:
    """Rebuild the API request that a serving layer would send for this trainee."""
    owned = skills.loc[skills["Trainee_ID"].eq(snapshot_row["Trainee_ID"])].groupby("Skill", as_index=False)["Proficiency"].max()
    return {
        "education_level": snapshot_row["Education_Level"], "target_job_role": snapshot_row["Target_Job_Role"],
        "skills": [{"name": row["Skill"], "proficiency": float(row["Proficiency"])} for _, row in owned.iterrows()],
        "attendance_percent": float(snapshot_row["Attendance_Percent"]), "assessment_score": float(snapshot_row["Assessment_Score"]),
        "training_performance": None, "training_duration_weeks": float(snapshot_row["Training_Duration_Weeks"]),
        "previous_experience_years": float(snapshot_row["Previous_Experience_Years"]), "course": snapshot_row["Course"],
        "training_provider": snapshot_row["Training_Provider"], "rural_urban": snapshot_row["Rural_Urban"],
        "certification": snapshot_row["Certification"] == "Yes", "internship": snapshot_row["Internship"] == "Yes",
    }


def test_serving_frame_reproduces_the_training_frame(prepared: dict) -> None:
    """The API must derive exactly the features the model was trained on."""
    snapshot = prepared["tables"]["placement_training_snapshot"]
    skills = prepared["tables"]["trainee_skills"]
    requirements = load_role_requirements(prepared["output_dir"] / "role_skill_requirements.csv")
    for position in range(8):
        row = snapshot.iloc[position]
        payload = _api_payload(row, skills)
        gap = skill_gap_analysis(payload["skills"], requirements[payload["target_job_role"]])
        served = placement_api_frame(payload, gap, float(row["Demand_Score"]))
        trained = build_placement_frame(snapshot.iloc[[position]]).reset_index(drop=True)
        assert list(served.columns) == list(trained.columns)
        for column in served.columns:
            if pd.api.types.is_numeric_dtype(trained[column]):
                assert served[column].iloc[0] == pytest.approx(trained[column].iloc[0], abs=0.05), column
            else:
                assert served[column].iloc[0] == trained[column].iloc[0], column
        assert row["Training_Performance"] == pytest.approx(training_performance(row["Assessment_Score"], row["Attendance_Percent"]))


def test_feature_contract_fingerprint_tracks_the_text_encoding(monkeypatch: pytest.MonkeyPatch) -> None:
    """A tokenisation change must invalidate saved bundles instead of skewing silently."""
    baseline = feature_contract_fingerprint()
    monkeypatch.setattr(features_module, "TEXT_ENCODING_VERSION", features_module.TEXT_ENCODING_VERSION + 1)
    assert feature_contract_fingerprint() != baseline
    monkeypatch.undo()
    assert feature_contract_fingerprint() == baseline


def test_failed_commit_leaves_the_previous_dataset_intact(prepared: dict, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    destination = tmp_path / "processed"
    shutil.copytree(prepared["output_dir"], destination)
    before = {path.name: path.read_bytes() for path in sorted(destination.glob("*.csv"))}
    truncated = {name: frame.head(1) for name, frame in prepared["tables"].items()}
    original_replace = Path.replace
    calls = {"count": 0}

    def flaky_replace(self: Path, target: Path):  # noqa: ANN202 - mirrors Path.replace
        calls["count"] += 1
        if calls["count"] == 7:
            raise OSError("simulated file lock")
        return original_replace(self, target)

    monkeypatch.setattr(Path, "replace", flaky_replace)
    with pytest.raises(RuntimeError, match="restored"):
        prepare_module._write_all(destination, truncated)
    monkeypatch.undo()
    assert {path.name: path.read_bytes() for path in sorted(destination.glob("*.csv"))} == before
    assert not list(destination.glob(".*"))
