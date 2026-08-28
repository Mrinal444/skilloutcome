"""Deterministic mappings from application records to ML API payloads."""
from __future__ import annotations

from typing import Any

from app.models.trainee import SkillLevel, Trainee


# The application stores proficiency as the three controlled SkillLevel values,
# while the ML contract accepts a 0--100 numeric proficiency.  This conversion
# is intentionally explicit; absent or unrecognized values are rejected rather
# than synthesized.
SKILL_LEVEL_TO_PROFICIENCY = {
    SkillLevel.BEGINNER.value: 33.0,
    SkillLevel.INTERMEDIATE.value: 66.0,
    SkillLevel.ADVANCED.value: 100.0,
}


class MLFeaturesIncompleteError(ValueError):
    """Raised when the database cannot supply an ML contract field."""

    def __init__(self, missing_fields: list[str]) -> None:
        self.missing_fields = sorted(set(missing_fields))
        super().__init__("Missing ML feature fields: " + ", ".join(self.missing_fields))


def build_skill_gap_payload(trainee: Trainee, target_job_role: str) -> dict[str, Any]:
    """Build a stable /skill-gap request solely from supplied and stored values."""
    missing_fields: list[str] = []
    current_skills: list[dict[str, Any]] = []

    for trainee_skill in trainee.skills:
        skill_name = trainee_skill.skill.skill_name if trainee_skill.skill else None
        level = trainee_skill.level
        level_value = level.value if isinstance(level, SkillLevel) else str(level or "")

        if not skill_name or not skill_name.strip():
            missing_fields.append("skills[].name")
            continue
        if level_value not in SKILL_LEVEL_TO_PROFICIENCY:
            missing_fields.append(f"skills[{skill_name}].level")
            continue
        current_skills.append(
            {
                "name": skill_name.strip(),
                "proficiency": SKILL_LEVEL_TO_PROFICIENCY[level_value],
            }
        )

    if not current_skills:
        missing_fields.append("skills")
    if missing_fields:
        raise MLFeaturesIncompleteError(missing_fields)

    # Sorting makes the outbound request reproducible even when relationship
    # loading order differs by database engine.
    current_skills.sort(key=lambda item: (item["name"].casefold(), item["name"]))
    return {"target_job_role": target_job_role, "current_skills": current_skills}
