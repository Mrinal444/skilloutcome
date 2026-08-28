"""Fixtures that build a miniature, schema-valid source dataset and prepare it.

The real 50k-row source is not part of the repository, so the pipeline tests generate
their own deterministic stand-in. It is small enough to prepare in about a second and
still exercises every table, label and validation rule in src/data/prepare_dataset.py.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from src.data.prepare_dataset import prepare_dataset

ROWS = 180
# course -> (target role from COURSE_TO_ROLE, provider, the three assessed skills)
COURSES = {
    "Data Analytics": ("Analytics Guild", ["Python", "SQL", "Power BI"]),
    "Python Programming": ("CodeWorks Institute", ["Python", "Java", "SQL"]),
    "Web Development": ("CodeWorks Institute", ["JavaScript", "React", "SQL"]),
    "Retail Operations": ("RetailPro Academy", ["Sales", "Communication", "Excel"]),
}
LOCATIONS = [("Karnataka", "Bengaluru", "Urban"), ("Odisha", "Cuttack", "Rural")]
JOB_ROLES = ["Data Analyst", "Software Developer", "Web Developer", "Sales Executive"]
EMPLOYMENT_TYPES = ["Full-Time", "Contract", "Apprenticeship"]
INDUSTRIES = ["IT Services", "Retail", "BFSI"]
EDUCATION_LEVELS = ["Secondary", "Diploma", "Graduate", "Post Graduate"]


def _source_frame() -> pd.DataFrame:
    """Deterministic stand-in for the illustrative source CSV."""
    rng = np.random.default_rng(26135)
    courses = list(COURSES)
    rows = []
    for index in range(ROWS):
        course = courses[index % len(courses)]
        provider, skills = COURSES[course]
        state, district, rural_urban = LOCATIONS[index % len(LOCATIONS)]
        proficiency = float(rng.integers(45, 96))
        required = 75.0
        placed = int(index % 10 < 7)
        # Roughly a third of placements end before the retention milestone, so both the
        # placement and the attrition label carry two classes in a fixture this small.
        retained = int(placed and index % 3 != 0)
        rows.append({
            "Trainee_ID": f"SRC-{index:05d}", "Age": int(19 + index % 14), "Gender": ["Female", "Male"][index % 2],
            "State": state, "District": district, "Rural_Urban": rural_urban, "Education_Level": EDUCATION_LEVELS[index % len(EDUCATION_LEVELS)],
            "Course": course, "Training_Provider": provider, "Training_Duration_Weeks": int(8 + index % 9),
            "Attendance_Percent": round(float(rng.uniform(58, 99)), 1), "Assessment_Score": round(float(rng.uniform(40, 97)), 1),
            "Certification": ["Yes", "No"][index % 2], "Internship": ["No", "Yes"][index % 3 == 0],
            "Previous_Experience_Years": float(index % 4), "Skill_1": skills[0], "Skill_2": skills[1], "Skill_3": skills[2],
            "Skill_Proficiency": proficiency, "Required_Proficiency": required,
            "Skill_Demand_Percent": round(float(rng.uniform(40, 95)), 1), "Skill_Gap": round(max(0.0, required - proficiency), 1),
            "Job_Applications": int(rng.integers(0, 25)), "Interview_Count": int(rng.integers(0, 6)),
            "Placement_Status": "Placed" if placed else "Not Placed", "Placement_Probability": round(float(rng.uniform(0, 1)), 3),
            "Employment_Type": EMPLOYMENT_TYPES[index % len(EMPLOYMENT_TYPES)] if placed else "None",
            "Industry": INDUSTRIES[index % len(INDUSTRIES)] if placed else "None",
            "Job_Role": JOB_ROLES[index % len(JOB_ROLES)] if placed else "None",
            "Starting_Salary_LPA": round(float(rng.uniform(1.8, 7.5)), 2) if placed else 0.0,
            "Retained_6_Months": "Yes" if retained else "No", "Retention_Probability": round(float(rng.uniform(0, 1)), 3),
            "Non_Placement_Reason": "None" if placed else "Skill Gap",
            "Placement_Target": placed, "Retention_Target": retained, "Non_Placement_Target": int(not placed),
        })
    return pd.DataFrame(rows)


@pytest.fixture(scope="session")
def prepared(tmp_path_factory: pytest.TempPathFactory) -> dict:
    """Run the real preparation pipeline on the fixture source and return every table."""
    root = tmp_path_factory.mktemp("fixture_dataset")
    source_path = root / "mini_source.csv"
    _source_frame().to_csv(source_path, index=False)
    output_dir = root / "processed"
    report = prepare_dataset(source_path, output_dir, root / "data_quality.json")
    tables = {path.stem: pd.read_csv(path) for path in sorted(output_dir.glob("*.csv"))}
    return {"root": root, "source_path": source_path, "output_dir": output_dir, "report": report, "tables": tables}
