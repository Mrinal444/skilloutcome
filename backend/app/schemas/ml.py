"""Request contracts for backend endpoints backed by the ML service."""
from pydantic import BaseModel, Field, field_validator


class TraineeSkillGapRequest(BaseModel):
    """The only non-persisted input needed for a trainee skill-gap analysis."""

    target_job_role: str = Field(..., min_length=1, max_length=100)

    @field_validator("target_job_role")
    @classmethod
    def target_job_role_must_not_be_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("target_job_role cannot be blank")
        return value
