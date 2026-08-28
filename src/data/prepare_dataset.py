"""Build normalized longitudinal SkillOutcome datasets."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.modeling.features import (
    ATTRITION_FORBIDDEN_COLUMNS,
    PLACEMENT_FORBIDDEN_COLUMNS,
    REQUIRED_SOURCE_COLUMNS,
    normalize_skill,
    skills_to_text,
    training_performance,
    validate_source_schema,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "processed"
DEFAULT_REPORT = PROJECT_ROOT / "reports" / "data_quality.json"
AS_OF_DATE = pd.Timestamp("2026-08-27")
# Observation checkpoints (days after employment start) for the attrition risk window.
ATTRITION_CHECKPOINT_DAYS = np.array([30, 60, 90, 120, 150])
ATTRITION_LABEL_DEFINITION = "Termination before the 6-month retention milestone, observed strictly after the snapshot checkpoint."

COURSE_TO_ROLE = {
    "Accounting & GST": "Account Executive", "Advanced Java Development": "Software Developer",
    "Cloud Computing": "Cloud Associate", "Cybersecurity": "Cybersecurity Associate",
    "Data Analytics": "Data Analyst", "Digital Marketing": "Digital Marketing Executive",
    "Electrical Technician": "Technician", "Graphic Design": "Graphic Designer",
    "Healthcare Assistant": "Healthcare Assistant", "Machine Learning": "Data Analyst",
    "Mobile App Development": "Software Developer", "Networking": "Support Engineer",
    "Python Programming": "Software Developer", "Retail Operations": "Sales Executive",
    "Web Development": "Web Developer",
}

ROLE_REQUIREMENTS = {
    "Account Executive": [("Accounting", 80, 0.5), ("Excel", 70, 0.3), ("Communication", 65, 0.2)],
    "Cloud Associate": [("AWS", 80, 0.4), ("Azure", 75, 0.35), ("Linux", 70, 0.25)],
    "Cybersecurity Associate": [("Cybersecurity", 80, 0.5), ("Linux", 70, 0.3), ("Networking", 70, 0.2)],
    "Data Analyst": [("Python", 75, 0.35), ("SQL", 80, 0.4), ("Power BI", 70, 0.25)],
    "Digital Marketing Executive": [("Digital Marketing", 80, 0.5), ("Communication", 70, 0.3), ("Excel", 65, 0.2)],
    "Graphic Designer": [("Communication", 70, 0.4), ("Digital Marketing", 65, 0.35), ("Excel", 60, 0.25)],
    "Healthcare Assistant": [("Healthcare Operations", 80, 0.5), ("Communication", 70, 0.3), ("Excel", 60, 0.2)],
    "Sales Executive": [("Sales", 80, 0.5), ("Communication", 75, 0.35), ("Excel", 60, 0.15)],
    "Software Developer": [("Python", 75, 0.35), ("Java", 75, 0.35), ("SQL", 70, 0.3)],
    "Support Engineer": [("Networking", 80, 0.4), ("Linux", 75, 0.35), ("Communication", 65, 0.25)],
    "Technician": [("AutoCAD", 75, 0.45), ("Networking", 65, 0.3), ("Excel", 60, 0.25)],
    "Web Developer": [("JavaScript", 80, 0.4), ("React", 75, 0.35), ("SQL", 65, 0.25)],
}


def _date_text(values: pd.Series | pd.DatetimeIndex) -> pd.Series:
    return pd.Series(values).dt.strftime("%Y-%m-%d")


def _clear_staging(output_dir: Path) -> None:
    """Remove leftovers from an interrupted run so staging always starts clean."""
    for pattern in (".*.tmp", ".*.bak"):
        for path in output_dir.glob(pattern):
            path.unlink(missing_ok=True)


def _probe_writable(destination: Path) -> None:
    if not destination.exists():
        return
    try:
        with destination.open("r+b"):
            return
    except OSError as error:
        raise PermissionError(f"{destination.name} is locked by another program. Close it (Excel, VS Code preview, sync client) and rerun.") from error


def _commit(output_dir: Path, staged: dict[str, Path]) -> None:
    """Swap every staged table in, or leave the previous dataset untouched.

    Each table is written to a temporary file first, every destination is probed for
    write access, and only then are the files swapped. A failure part-way through is
    rolled back, so the directory never mixes tables from two different runs.
    """
    for name in staged:
        _probe_writable(output_dir / f"{name}.csv")
    backups: dict[str, Path] = {}
    swapped: list[str] = []
    try:
        for name, temporary in staged.items():
            destination = output_dir / f"{name}.csv"
            if destination.exists():
                backup = output_dir / f".{name}.bak"
                destination.replace(backup)
                backups[name] = backup
            temporary.replace(destination)
            swapped.append(name)
    except OSError as error:
        for name in swapped:
            destination = output_dir / f"{name}.csv"
            destination.replace(output_dir / f".{name}.tmp")
            if name in backups:
                backups[name].replace(destination)
        raise RuntimeError(f"Dataset commit failed on '{name}'; the previous tables were restored. Original error: {error}") from error
    finally:
        for backup in backups.values():
            backup.unlink(missing_ok=True)


def _write_all(output_dir: Path, tables: dict[str, pd.DataFrame]) -> None:
    _clear_staging(output_dir)
    staged: dict[str, Path] = {}
    try:
        for name, frame in tables.items():
            temporary = output_dir / f".{name}.tmp"
            frame.to_csv(temporary, index=False)
            staged[name] = temporary
        _commit(output_dir, staged)
    finally:
        _clear_staging(output_dir)


def _validate_tables(tables: dict[str, pd.DataFrame]) -> None:
    trainees = tables["trainees"]
    trainee_ids = set(trainees["Trainee_ID"])
    if not trainees["Trainee_ID"].is_unique:
        raise ValueError("Trainee_ID values must be unique.")
    for name in ["training_completions", "trainee_skills", "skill_gap_details", "job_search_events", "placement_training_snapshot", "employment_spells", "attrition_training_snapshot"]:
        if not set(tables[name]["Trainee_ID"]).issubset(trainee_ids):
            raise ValueError(f"{name} has an unknown Trainee_ID.")
    spells = tables["employment_spells"]
    employment_ids = set(spells["Employment_ID"])
    for name in ["salary_history", "engagement_checkins", "attrition_training_snapshot", "wage_progression_outcomes"]:
        if not set(tables[name]["Employment_ID"]).issubset(employment_ids):
            raise ValueError(f"{name} has an unknown Employment_ID.")
    weights = tables["role_skill_requirements"].groupby("Target_Job_Role")["Importance_Weight"].sum()
    if not np.allclose(weights.to_numpy(), 1.0):
        raise ValueError("Role requirement weights must sum to 1.")
    gaps = tables["skill_gap_details"]
    if (gaps[["Proficiency_Deficit", "Weighted_Deficit"]] < 0).any().any():
        raise ValueError("Skill deficits must be non-negative.")
    if PLACEMENT_FORBIDDEN_COLUMNS & set(tables["placement_training_snapshot"].columns):
        raise ValueError("Placement snapshot contains outcome leakage.")
    attrition = tables["attrition_training_snapshot"]
    if ATTRITION_FORBIDDEN_COLUMNS & set(attrition.columns):
        raise ValueError("Attrition snapshot contains outcome leakage.")
    _validate_attrition_timing(attrition, spells)


def _validate_attrition_timing(attrition: pd.DataFrame, spells: pd.DataFrame) -> None:
    """Every attrition feature row must be observed strictly before the event it predicts."""
    checked = attrition[["Employment_ID", "Snapshot_Observed_On", "Employment_Duration_Months"]].merge(spells[["Employment_ID", "Start_Date", "End_Date"]], on="Employment_ID", how="left")
    observed = pd.to_datetime(checked["Snapshot_Observed_On"])
    start = pd.to_datetime(checked["Start_Date"])
    end = pd.to_datetime(checked["End_Date"])
    if (observed < start).any():
        raise ValueError("Attrition snapshots must be observed on or after the employment start date.")
    if (observed >= end.fillna(pd.Timestamp.max)).any():
        raise ValueError("Attrition snapshots must be observed strictly before the termination date.")
    if (observed > AS_OF_DATE).any():
        raise ValueError("Attrition snapshots must not be observed after the as-of date.")
    if (checked["Employment_Duration_Months"] < 0).any():
        raise ValueError("Employment duration must be non-negative.")
    if (checked["Employment_Duration_Months"] > ATTRITION_CHECKPOINT_DAYS.max() / 30.44 + 0.05).any():
        raise ValueError("Attrition snapshots must sit on a defined observation checkpoint.")
    if not 0 < float(attrition["Attrition_Target"].mean()) < 1:
        raise ValueError("Attrition label must contain both classes.")



def _role_requirements() -> pd.DataFrame:
    return pd.DataFrame(
        [(role, normalize_skill(skill), proficiency, weight, "2024-01-01", "synthetic_derived") for role, requirements in ROLE_REQUIREMENTS.items() for skill, proficiency, weight in requirements],
        columns=["Target_Job_Role", "Skill", "Required_Proficiency", "Importance_Weight", "Effective_From", "Data_Origin"],
    )


def _build_skill_table(source: pd.DataFrame, completion_dates: pd.Series) -> pd.DataFrame:
    records = []
    offsets = [4, -3, 1]
    for position, skill_column in enumerate(["Skill_1", "Skill_2", "Skill_3"]):
        part = source[["Trainee_ID", skill_column, "Skill_Proficiency"]].rename(columns={skill_column: "Skill"}).copy()
        part["Skill"] = part["Skill"].map(normalize_skill)
        part["Proficiency"] = (part["Skill_Proficiency"] + offsets[position]).clip(0, 100).round(1)
        part["Assessment_Date"] = _date_text(completion_dates - pd.to_timedelta(7 * (position + 1), unit="D"))
        part["Evidence_Source"] = "legacy_skill_assessment"
        records.append(part[["Trainee_ID", "Skill", "Proficiency", "Assessment_Date", "Evidence_Source"]])
    skills = pd.concat(records, ignore_index=True)
    return skills.groupby(["Trainee_ID", "Skill", "Assessment_Date", "Evidence_Source"], as_index=False)["Proficiency"].max()


def _skill_gap_details(skills: pd.DataFrame, trainee_roles: pd.DataFrame, requirements: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    current = skills.groupby(["Trainee_ID", "Skill"], as_index=False)["Proficiency"].max()
    detail = trainee_roles[["Trainee_ID", "Target_Job_Role"]].merge(requirements, on="Target_Job_Role", how="left").merge(current, on=["Trainee_ID", "Skill"], how="left")
    detail["Current_Proficiency"] = detail["Proficiency"].fillna(0.0)
    detail["Missing_Skill"] = detail["Proficiency"].isna()
    detail["Proficiency_Deficit"] = (detail["Required_Proficiency"] - detail["Current_Proficiency"]).clip(lower=0).round(2)
    detail["Weighted_Deficit"] = (detail["Importance_Weight"] * detail["Proficiency_Deficit"] / detail["Required_Proficiency"]).round(4)
    summary = detail.groupby("Trainee_ID", as_index=False).agg(
        Skill_Gap_Score=("Weighted_Deficit", lambda values: round(100 * values.sum(), 2)),
        Missing_Skill_Count=("Missing_Skill", "sum"),
        Skill_Coverage_Percent=("Missing_Skill", lambda values: round(100 * (1 - values.mean()), 2)),
    )
    detail = detail.drop(columns=["Proficiency"]).sort_values(["Trainee_ID", "Weighted_Deficit"], ascending=[True, False])
    return detail, summary


def _demand_snapshots(trainees: pd.DataFrame) -> pd.DataFrame:
    months = pd.date_range(pd.to_datetime(trainees["Completion_Date"].min()).replace(day=1), AS_OF_DATE.replace(day=1), freq="MS")
    locations = trainees[["State", "District"]].drop_duplicates().reset_index(drop=True)
    rows = []
    for role_index, role in enumerate(sorted(ROLE_REQUIREMENTS)):
        for location_index, location in locations.iterrows():
            for month_index, month in enumerate(months):
                active_postings = 18 + (role_index * 7 + location_index * 3 + month_index * 5) % 65
                candidate_count = 25 + (role_index * 5 + location_index * 11 + month_index * 2) % 90
                demand_score = round(100 * active_postings / (active_postings + candidate_count), 2)
                rows.append((role, location["State"], location["District"], month.strftime("%Y-%m-%d"), active_postings, candidate_count, demand_score, "synthetic_derived"))
    return pd.DataFrame(rows, columns=["Target_Job_Role", "State", "District", "Snapshot_Date", "Active_Postings", "Candidate_Count", "Demand_Score", "Data_Origin"])


def _employment_tables(source: pd.DataFrame, trainees: pd.DataFrame, gap_summary: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    placed = source[source["Placement_Target"].eq(1)].copy()
    placed = placed.merge(trainees[["Trainee_ID", "Completion_Date"]], on="Trainee_ID").merge(gap_summary, on="Trainee_ID")
    start = pd.to_datetime(placed["Completion_Date"]) + pd.to_timedelta(14 + (placed.index.to_numpy() % 70), unit="D")
    retained = placed["Retention_Target"].eq(1)
    end = pd.Series(pd.NaT, index=placed.index, dtype="datetime64[ns]")
    end.loc[~retained] = start.loc[~retained] + pd.to_timedelta(30 + (placed.index.to_numpy()[~retained] % 145), unit="D")
    spells = pd.DataFrame({
        "Employment_ID": [f"EMP-{i:06d}" for i in range(1, len(placed) + 1)], "Trainee_ID": placed["Trainee_ID"].to_numpy(),
        "Actual_Job_Role": placed["Job_Role"].to_numpy(), "Industry": placed["Industry"].to_numpy(), "Employment_Type": placed["Employment_Type"].to_numpy(),
        "Start_Date": _date_text(start), "End_Date": _date_text(end), "Termination_Observed": (~retained).to_numpy(), "Data_Origin": "synthetic_derived",
    })
    starts = pd.to_numeric(placed["Starting_Salary_LPA"], errors="coerce").clip(lower=0.1)
    raises = (1.5 + 0.025 * placed["Assessment_Score"] + 0.015 * (100 - placed["Skill_Gap_Score"])).clip(1.5, 6.0)
    salary_start = pd.DataFrame({"Employment_ID": spells["Employment_ID"], "Effective_Date": spells["Start_Date"], "Salary_LPA": starts.round(2), "Data_Origin": "synthetic_derived"})
    six_month = retained & (start + pd.Timedelta(days=183) <= AS_OF_DATE)
    salary_later = pd.DataFrame({"Employment_ID": spells.loc[six_month, "Employment_ID"], "Effective_Date": _date_text(start.loc[six_month] + pd.Timedelta(days=183)), "Salary_LPA": (starts.loc[six_month] * (1 + raises.loc[six_month] / 100)).round(2), "Data_Origin": "synthetic_derived"})
    salaries = pd.concat([salary_start, salary_later], ignore_index=True).sort_values(["Employment_ID", "Effective_Date"])
    engagement_rows = []
    spell_start = pd.to_datetime(spells["Start_Date"])
    spell_end = pd.to_datetime(spells["End_Date"])
    base_score = 3.0 + placed["Assessment_Score"].to_numpy() / 40 + placed["Attendance_Percent"].to_numpy() / 100 + ((np.arange(len(spells)) % 7) - 3) * 0.08
    # A day-15 onboarding check-in means every attrition checkpoint has at least one prior observation.
    for day in [15, 30, 91, 183]:
        month = day / 30.44
        checkin = spell_start + pd.Timedelta(days=day)
        active = (checkin <= AS_OF_DATE) & (spell_end.isna() | (checkin < spell_end))
        score = np.clip(base_score - 0.1 * month + ((np.arange(len(spells)) + day) % 5) * 0.1, 1, 10)
        engagement_rows.append(pd.DataFrame({"Employment_ID": spells.loc[active, "Employment_ID"], "Checkin_Date": _date_text(checkin.loc[active]), "Engagement_Score": np.round(score[active], 2), "Data_Origin": "synthetic_derived"}))
    engagement = pd.concat(engagement_rows, ignore_index=True)
    return spells, salaries, engagement


def _as_of_value(events: pd.DataFrame, observation: pd.DataFrame, date_column: str, value_column: str) -> pd.DataFrame:
    """Latest event value per employment observed on or before the snapshot date."""
    merged = events.merge(observation, on="Employment_ID", how="inner")
    merged = merged[pd.to_datetime(merged[date_column]) <= pd.to_datetime(merged["Snapshot_Observed_On"])]
    merged = merged.sort_values(["Employment_ID", date_column])
    return merged.groupby("Employment_ID", as_index=False).last()[["Employment_ID", value_column]]


def _wage_progression(spells: pd.DataFrame, salaries: pd.DataFrame) -> pd.DataFrame:
    """Wage progression is a programme outcome metric, deliberately kept out of the model views."""
    ordered = salaries.sort_values(["Employment_ID", "Effective_Date"])
    aggregated = ordered.groupby("Employment_ID", as_index=False).agg(
        First_Salary_LPA=("Salary_LPA", "first"), Latest_Salary_LPA=("Salary_LPA", "last"),
        First_Effective_Date=("Effective_Date", "first"), Latest_Effective_Date=("Effective_Date", "last"),
        Salary_Records=("Salary_LPA", "size"),
    )
    aggregated["Wage_Growth_Percent"] = np.where(aggregated["First_Salary_LPA"] > 0, (aggregated["Latest_Salary_LPA"] / aggregated["First_Salary_LPA"] - 1) * 100, np.nan).round(2)
    aggregated["Observed_Months"] = ((pd.to_datetime(aggregated["Latest_Effective_Date"]) - pd.to_datetime(aggregated["First_Effective_Date"])).dt.days / 30.44).round(2)
    progression = spells[["Employment_ID", "Trainee_ID"]].merge(aggregated, on="Employment_ID", how="left")
    progression["Data_Origin"] = "outcome_metric_not_a_feature"
    return progression


def prepare_dataset(input_path: Path, output_dir: Path = DEFAULT_OUTPUT, report_path: Path = DEFAULT_REPORT) -> dict:
    """Regenerate normalized tables from the illustrative source."""
    source = pd.read_csv(input_path)
    validate_source_schema(source)
    source = source.copy().reset_index(drop=True)
    source["Trainee_ID"] = [f"TRN-SIH26135-{i:06d}" for i in range(1, len(source) + 1)]
    if not source["Trainee_ID"].is_unique:
        raise ValueError("Generated Trainee_ID values are not unique.")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    completion = pd.Timestamp("2024-01-01") + pd.to_timedelta((source.index.to_numpy() * 13) % 720, unit="D")
    target_roles = source["Course"].map(COURSE_TO_ROLE)
    trainees = source[["Trainee_ID", "Age", "Gender", "State", "District", "Rural_Urban", "Education_Level"]].copy()
    trainees["Data_Origin"] = "illustrative_source"
    training = source[["Trainee_ID", "Course", "Training_Provider", "Training_Duration_Weeks", "Attendance_Percent", "Assessment_Score", "Certification", "Internship", "Previous_Experience_Years"]].copy()
    training["Target_Job_Role"] = target_roles
    training["Completion_Date"] = _date_text(completion)
    training["Training_Start_Date"] = _date_text(completion - pd.to_timedelta(source["Training_Duration_Weeks"] * 7, unit="D"))
    training["Training_Performance"] = [training_performance(score, attendance) for score, attendance in zip(training["Assessment_Score"], training["Attendance_Percent"])]
    training["Data_Origin"] = "illustrative_source_plus_derived"
    trainee_roles = training[["Trainee_ID", "Target_Job_Role"]]
    requirements = _role_requirements()
    skills = _build_skill_table(source, pd.Series(completion))
    gaps, gap_summary = _skill_gap_details(skills, trainee_roles, requirements)
    demand = _demand_snapshots(pd.concat([trainees[["Trainee_ID", "State", "District"]], training[["Completion_Date"]]], axis=1))
    snapshot_month = pd.to_datetime(training["Completion_Date"]).dt.to_period("M").dt.to_timestamp().dt.strftime("%Y-%m-%d")
    placement = training.merge(trainees[["Trainee_ID", "State", "District", "Education_Level", "Rural_Urban"]], on="Trainee_ID").merge(gap_summary, on="Trainee_ID")
    placement["Snapshot_Date"] = snapshot_month
    placement = placement.merge(demand[["Target_Job_Role", "State", "District", "Snapshot_Date", "Demand_Score"]], on=["Target_Job_Role", "State", "District", "Snapshot_Date"], how="left")
    skills_text = skills.groupby("Trainee_ID")["Skill"].agg(skills_to_text).rename("Skills_Text")
    placement = placement.merge(skills_text, on="Trainee_ID").merge(source[["Trainee_ID", "Placement_Target"]], on="Trainee_ID")
    placement["Data_Origin"] = "derived_training_snapshot"

    search = pd.DataFrame({"Trainee_ID": source["Trainee_ID"], "Event_Date": _date_text(completion + pd.to_timedelta(7, unit="D")), "Application_Count": source["Job_Applications"], "Interview_Count": source["Interview_Count"], "Data_Origin": "illustrative_source"})
    spells, salaries, engagement = _employment_tables(source, training, gap_summary)
    wage_progression = _wage_progression(spells, salaries)
    attrition = spells.merge(training, on="Trainee_ID").merge(gap_summary, on="Trainee_ID").merge(trainees[["Trainee_ID", "State", "District"]], on="Trainee_ID")
    start_dates = pd.to_datetime(attrition["Start_Date"])
    end_dates = pd.to_datetime(attrition["End_Date"])
    # Fixed risk-window design. Each spell is observed at one checkpoint 1-5 months in, and the
    # label is termination before the 6-month retention milestone, strictly after that checkpoint.
    # A checkpoint that is independent of the outcome keeps Employment_Duration_Months from
    # secretly encoding the label, and spells that already ended are excluded because there is
    # nothing left to predict for them.
    observed = start_dates + pd.to_timedelta(ATTRITION_CHECKPOINT_DAYS[np.arange(len(attrition)) % len(ATTRITION_CHECKPOINT_DAYS)], unit="D")
    observable = (end_dates.isna() | (end_dates > observed)) & (observed <= AS_OF_DATE)
    attrition = attrition.loc[observable].reset_index(drop=True)
    start_dates, observed = start_dates.loc[observable].reset_index(drop=True), observed.loc[observable].reset_index(drop=True)
    attrition["Snapshot_Observed_On"] = _date_text(observed)
    attrition["Snapshot_Date"] = observed.dt.to_period("M").dt.to_timestamp().dt.strftime("%Y-%m-%d")
    attrition["Employment_Duration_Months"] = ((observed - start_dates).dt.days / 30.44).round(2)
    observation = attrition[["Employment_ID", "Snapshot_Observed_On"]]
    attrition = attrition.merge(_as_of_value(salaries, observation, "Effective_Date", "Salary_LPA"), on="Employment_ID", how="left").rename(columns={"Salary_LPA": "Current_Salary_LPA"})
    attrition = attrition.merge(_as_of_value(engagement, observation, "Checkin_Date", "Engagement_Score"), on="Employment_ID", how="left")
    attrition["Job_History_Count"] = np.floor(attrition["Previous_Experience_Years"]).astype(int)
    attrition["Attrition_Target"] = attrition["Termination_Observed"].astype(int)
    attrition["Data_Origin"] = "synthetic_longitudinal_derivation"
    attrition = attrition.merge(demand[["Target_Job_Role", "State", "District", "Snapshot_Date", "Demand_Score"]], on=["Target_Job_Role", "State", "District", "Snapshot_Date"], how="left")
    attrition = attrition.merge(skills_text, on="Trainee_ID", how="left")
    attrition = attrition[["Trainee_ID", "Employment_ID", "Snapshot_Date", "Snapshot_Observed_On", "Employment_Duration_Months", "Current_Salary_LPA", "Job_History_Count", "Engagement_Score", "Attendance_Percent", "Assessment_Score", "Skill_Gap_Score", "Demand_Score", "Employment_Type", "Industry", "Actual_Job_Role", "Target_Job_Role", "Skills_Text", "Attrition_Target", "Data_Origin"]]

    tables = {"trainees": trainees, "training_completions": training, "trainee_skills": skills, "role_skill_requirements": requirements, "skill_gap_details": gaps, "job_demand_snapshots": demand, "job_search_events": search, "employment_spells": spells, "salary_history": salaries, "engagement_checkins": engagement, "wage_progression_outcomes": wage_progression, "placement_training_snapshot": placement, "attrition_training_snapshot": attrition}
    _validate_tables(tables)
    _write_all(output_dir, tables)
    report = {
        "source": str(input_path), "output_dir": str(output_dir), "as_of_date": AS_OF_DATE.strftime("%Y-%m-%d"), "synthetic_derivation": True,
        "rows": {name: int(len(frame)) for name, frame in tables.items()},
        "unique_trainee_ids": int(trainees["Trainee_ID"].nunique()), "required_source_columns": len(REQUIRED_SOURCE_COLUMNS),
        "labels": {"placement_positive_rate": round(float(placement["Placement_Target"].mean()), 4), "attrition_positive_rate": round(float(attrition["Attrition_Target"].mean()), 4), "attrition_label_definition": ATTRITION_LABEL_DEFINITION, "attrition_checkpoint_days": ATTRITION_CHECKPOINT_DAYS.tolist(), "employment_spells_outside_risk_window": int(len(spells) - len(attrition))},
        "snapshot_windows": {"placement": [placement["Snapshot_Date"].min(), placement["Snapshot_Date"].max()], "attrition": [attrition["Snapshot_Observed_On"].min(), attrition["Snapshot_Observed_On"].max()]},
        "feature_completeness": {"attrition_engagement_missing_rate": round(float(attrition["Engagement_Score"].isna().mean()), 4), "attrition_demand_missing_rate": round(float(attrition["Demand_Score"].isna().mean()), 4), "placement_demand_missing_rate": round(float(placement["Demand_Score"].isna().mean()), 4)},
        "checks_passed": ["unique trainee ids", "referential integrity on Trainee_ID and Employment_ID", "role weights sum to 1", "non-negative skill deficits", "no outcome columns in model views", "attrition snapshots observed strictly before termination", "all tables committed together"],
        "note": "Dates, role requirements, demand, employment, salary, and engagement events are deterministic derivations because the source does not contain longitudinal records. Wage progression is published as an outcome table, never as a model feature.",
    }
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Regenerate normalized SkillOutcome data.")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    print(json.dumps(prepare_dataset(args.input, args.output_dir, args.report), indent=2))


if __name__ == "__main__":
    main()
