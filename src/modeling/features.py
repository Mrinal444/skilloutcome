"""Feature contracts and role-based skill-gap calculations."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
from typing import Any, Iterable

import numpy as np
import pandas as pd

REQUIRED_SOURCE_COLUMNS = {"Trainee_ID", "Age", "Gender", "State", "District", "Rural_Urban", "Education_Level", "Course", "Training_Provider", "Training_Duration_Weeks", "Attendance_Percent", "Assessment_Score", "Certification", "Internship", "Previous_Experience_Years", "Skill_1", "Skill_2", "Skill_3", "Skill_Proficiency", "Required_Proficiency", "Skill_Demand_Percent", "Skill_Gap", "Job_Applications", "Interview_Count", "Placement_Status", "Placement_Probability", "Employment_Type", "Industry", "Job_Role", "Starting_Salary_LPA", "Retained_6_Months", "Retention_Probability", "Non_Placement_Reason", "Placement_Target", "Retention_Target", "Non_Placement_Target"}

# Columns that must never reach a model view because they are outcomes of, or are
# derived after, the event being predicted. Enforced in src/data/prepare_dataset.py.
PLACEMENT_FORBIDDEN_COLUMNS = {"Placement_Status", "Placement_Probability", "Starting_Salary_LPA", "Retained_6_Months", "Retention_Probability", "Retention_Target", "Non_Placement_Reason", "Non_Placement_Target", "Employment_Type", "Industry", "Job_Role"}
ATTRITION_FORBIDDEN_COLUMNS = {"End_Date", "Termination_Observed", "Retained_6_Months", "Retention_Probability", "Retention_Target", "Wage_Growth_Percent", "Placement_Probability"}

PLACEMENT_NUMERIC_FEATURES = ["Training_Duration_Weeks", "Attendance_Percent", "Assessment_Score", "Training_Performance", "Previous_Experience_Years", "Skill_Gap_Score", "Missing_Skill_Count", "Skill_Coverage_Percent", "Demand_Score"]
PLACEMENT_CATEGORICAL_FEATURES = ["Education_Level", "Course", "Training_Provider", "Rural_Urban", "Certification", "Internship", "Target_Job_Role"]
PLACEMENT_TEXT_FEATURE = "Skills_Text"
PLACEMENT_FEATURES = PLACEMENT_NUMERIC_FEATURES + PLACEMENT_CATEGORICAL_FEATURES + [PLACEMENT_TEXT_FEATURE]

ATTRITION_NUMERIC_FEATURES = ["Employment_Duration_Months", "Current_Salary_LPA", "Job_History_Count", "Engagement_Score", "Attendance_Percent", "Assessment_Score", "Skill_Gap_Score", "Demand_Score"]
ATTRITION_CATEGORICAL_FEATURES = ["Employment_Type", "Industry", "Actual_Job_Role", "Target_Job_Role"]
ATTRITION_TEXT_FEATURE = "Skills_Text"
ATTRITION_FEATURES = ATTRITION_NUMERIC_FEATURES + ATTRITION_CATEGORICAL_FEATURES + [ATTRITION_TEXT_FEATURE]

# Bumped whenever Skills_Text tokenisation changes. Training and serving must agree,
# so the version is stored in the model bundle and checked by the API.
TEXT_ENCODING_VERSION = 2


def feature_contract_fingerprint() -> str:
    """Short hash of the feature contract, used to reject stale model bundles."""
    payload = json.dumps({"placement": PLACEMENT_FEATURES, "attrition": ATTRITION_FEATURES, "text_encoding": TEXT_ENCODING_VERSION}, sort_keys=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


def training_performance(assessment_score: float, attendance_percent: float) -> float:
    """Single definition of the blended training-performance feature."""
    return round(0.55 * float(assessment_score) + 0.45 * float(attendance_percent), 2)


def skills_to_text(names: Iterable[Any]) -> str:
    """Canonical Skills_Text used by both the training pipeline and the API.

    Multi-word skills collapse to one token (``Power BI`` -> ``power_bi``) and tokens are
    sorted and de-duplicated, so a trainee's skill set always produces the same string.
    """
    tokens = {normalize_skill(name).replace(" ", "_") for name in names}
    return " ".join(sorted(token for token in tokens if token))


def validate_source_schema(df: pd.DataFrame) -> None:
    missing = sorted(REQUIRED_SOURCE_COLUMNS - set(df.columns))
    if missing:
        raise ValueError(f"Dataset is missing required columns: {', '.join(missing)}")
    if df.empty:
        raise ValueError("Dataset is empty.")


def validate_snapshot(df: pd.DataFrame, required: set[str]) -> None:
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Snapshot is missing columns: {', '.join(missing)}")
    if df.empty:
        raise ValueError("Snapshot is empty.")


def normalize_skill(value: str) -> str:
    text = re.sub(r"[^a-z0-9+#.]", " ", str(value).casefold())
    return re.sub(r"\s+", " ", text).strip()


def load_role_requirements(path: Path) -> dict[str, list[dict[str, Any]]]:
    df = pd.read_csv(path)
    return {role: group[["Skill", "Required_Proficiency", "Importance_Weight"]].rename(columns={"Skill": "name", "Required_Proficiency": "required_proficiency", "Importance_Weight": "importance_weight"}).to_dict("records") for role, group in df.groupby("Target_Job_Role")}


def skill_gap_analysis(current_skills: list[dict[str, Any]], requirements: list[dict[str, Any]]) -> dict[str, Any]:
    current = {normalize_skill(item["name"]): float(item.get("proficiency", 0)) for item in current_skills if normalize_skill(item["name"])}
    missing, matched, below_required, recommendations = [], [], [], []
    weighted_gap = 0.0
    total_weight = sum(float(item.get("importance_weight", 1)) for item in requirements) or 1.0
    for requirement in requirements:
        name = requirement["name"].strip()
        key = normalize_skill(name)
        required = float(requirement.get("required_proficiency", 0))
        weight = float(requirement.get("importance_weight", 1))
        current_level = current.get(key, 0.0)
        deficit = max(0.0, required - current_level)
        weighted_deficit = weight * deficit / required if required else 0.0
        weighted_gap += weighted_deficit
        if key not in current:
            missing.append(name)
        else:
            matched.append(name)
        if deficit > 0:
            below_required.append({"skill": name, "current_proficiency": current_level, "required_proficiency": required, "deficit": round(deficit, 2)})
            recommendations.append({"skill": name, "priority_score": round(100 * weighted_deficit, 2), "reason": "missing" if key not in current else "below required proficiency"})
    recommendations.sort(key=lambda item: item["priority_score"], reverse=True)
    return {"missing_skills": sorted(missing), "matched_skills": sorted(matched), "below_required_proficiency": below_required, "skill_gap_score": round(100 * weighted_gap / total_weight, 2), "skill_coverage_percent": round(100 * len(matched) / len(requirements), 2) if requirements else 0.0, "recommendations": recommendations}


def _numeric_frame(df: pd.DataFrame, numeric: list[str], categorical: list[str], text: str) -> pd.DataFrame:
    result = pd.DataFrame(index=df.index)
    for column in numeric:
        result[column] = pd.to_numeric(df.get(column, pd.Series(np.nan, index=df.index)), errors="coerce")
    for column in categorical:
        result[column] = df.get(column, pd.Series("Unknown", index=df.index)).fillna("Unknown").astype(str)
    result[text] = df.get(text, pd.Series("", index=df.index)).fillna("").astype(str)
    return result[numeric + categorical + [text]]


def build_placement_frame(df: pd.DataFrame) -> pd.DataFrame:
    return _numeric_frame(df, PLACEMENT_NUMERIC_FEATURES, PLACEMENT_CATEGORICAL_FEATURES, PLACEMENT_TEXT_FEATURE)


def build_attrition_frame(df: pd.DataFrame) -> pd.DataFrame:
    return _numeric_frame(df, ATTRITION_NUMERIC_FEATURES, ATTRITION_CATEGORICAL_FEATURES, ATTRITION_TEXT_FEATURE)


def placement_api_frame(payload: dict[str, Any], gap: dict[str, Any], demand_score: float) -> pd.DataFrame:
    skills = payload["skills"]
    performance = payload.get("training_performance")
    if performance is None:
        performance = training_performance(payload["assessment_score"], payload["attendance_percent"])
    return pd.DataFrame([{
        "Training_Duration_Weeks": payload.get("training_duration_weeks"), "Attendance_Percent": payload["attendance_percent"], "Assessment_Score": payload["assessment_score"], "Training_Performance": performance, "Previous_Experience_Years": payload.get("previous_experience_years"), "Skill_Gap_Score": gap["skill_gap_score"], "Missing_Skill_Count": len(gap["missing_skills"]), "Skill_Coverage_Percent": gap["skill_coverage_percent"], "Demand_Score": demand_score,
        "Education_Level": payload["education_level"], "Course": payload.get("course", "Unknown"), "Training_Provider": payload.get("training_provider", "Unknown"), "Rural_Urban": payload.get("rural_urban", "Unknown"), "Certification": "Yes" if payload.get("certification", False) else "No", "Internship": "Yes" if payload.get("internship", False) else "No", "Target_Job_Role": payload["target_job_role"], "Skills_Text": skills_to_text(skill["name"] for skill in skills),
    }])


def attrition_api_frame(payload: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame([{
        "Employment_Duration_Months": payload["employment_duration_months"], "Current_Salary_LPA": payload["salary_lpa"], "Job_History_Count": payload["job_history"], "Engagement_Score": payload["engagement_score"], "Attendance_Percent": payload.get("attendance_percent"), "Assessment_Score": payload.get("assessment_score"), "Skill_Gap_Score": payload.get("skill_gap_score"), "Demand_Score": payload.get("demand_score"), "Employment_Type": payload.get("employment_type", "Unknown"), "Industry": payload.get("industry", "Unknown"), "Actual_Job_Role": payload.get("actual_job_role", "Unknown"), "Target_Job_Role": payload.get("target_job_role", "Unknown"), "Skills_Text": skills_to_text(skill["name"] for skill in payload.get("skills", [])),
    }])
