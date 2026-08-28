"""Contract checks against the committed dataset in data/processed."""
from pathlib import Path

import pandas as pd
import pytest

from src.modeling.features import ATTRITION_FORBIDDEN_COLUMNS, PLACEMENT_FORBIDDEN_COLUMNS

DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"
pytestmark = pytest.mark.skipif(not (DATA_DIR / "trainees.csv").exists(), reason="Run python -m src.data.prepare_dataset first.")


def test_snapshots_preserve_source_and_leakage_boundaries():
    trainees = pd.read_csv(DATA_DIR / "trainees.csv")
    placement = pd.read_csv(DATA_DIR / "placement_training_snapshot.csv")
    attrition = pd.read_csv(DATA_DIR / "attrition_training_snapshot.csv")
    assert trainees["Trainee_ID"].is_unique
    assert set(placement["Trainee_ID"]).issubset(set(trainees["Trainee_ID"]))
    assert not PLACEMENT_FORBIDDEN_COLUMNS & set(placement.columns)
    assert not ATTRITION_FORBIDDEN_COLUMNS & set(attrition.columns)
    assert 0 < placement["Placement_Target"].mean() < 1
    assert 0 < attrition["Attrition_Target"].mean() < 1


def test_attrition_snapshots_precede_termination():
    attrition = pd.read_csv(DATA_DIR / "attrition_training_snapshot.csv")
    spells = pd.read_csv(DATA_DIR / "employment_spells.csv")
    merged = attrition[["Employment_ID", "Snapshot_Observed_On"]].merge(spells[["Employment_ID", "Start_Date", "End_Date"]], on="Employment_ID", how="left")
    observed = pd.to_datetime(merged["Snapshot_Observed_On"])
    assert (observed >= pd.to_datetime(merged["Start_Date"])).all()
    assert (observed < pd.to_datetime(merged["End_Date"]).fillna(pd.Timestamp.max)).all()


def test_wage_progression_is_published_as_an_outcome_only():
    progression = pd.read_csv(DATA_DIR / "wage_progression_outcomes.csv")
    assert "Wage_Growth_Percent" in progression.columns
    assert progression["Data_Origin"].eq("outcome_metric_not_a_feature").all()
    assert "Wage_Growth_Percent" not in pd.read_csv(DATA_DIR / "attrition_training_snapshot.csv", nrows=1).columns


def test_role_requirement_weights_sum_to_one():
    requirements = pd.read_csv(DATA_DIR / "role_skill_requirements.csv")
    weights = requirements.groupby("Target_Job_Role")["Importance_Weight"].sum()
    assert weights.between(0.999, 1.001).all()
