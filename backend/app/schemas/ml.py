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


class MLSkillProfile(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    proficiency: float = Field(..., ge=0, le=100)


class PlacementPredictionRequest(BaseModel):
    education_level: str = Field(..., min_length=1, max_length=100)
    target_job_role: str = Field(..., min_length=1, max_length=100)
    skills: list[MLSkillProfile] = Field(..., min_length=1)
    attendance_percent: float = Field(..., ge=0, le=100)
    assessment_score: float = Field(..., ge=0, le=100)
    training_performance: float | None = Field(None, ge=0, le=100)
    training_duration_weeks: float | None = Field(None, ge=0, le=104)
    previous_experience_years: float | None = Field(None, ge=0, le=60)
    course: str | None = None
    training_provider: str | None = None
    rural_urban: str | None = None
    state: str | None = None
    district: str | None = None
    certification: bool = False
    internship: bool = False


class AttritionPredictionRequest(BaseModel):
    employment_duration_months: float = Field(..., ge=0, le=600)
    salary_lpa: float = Field(..., ge=0, le=1000)
    job_history: int = Field(..., ge=0, le=100)
    engagement_score: float = Field(..., ge=0, le=10)
    attendance_percent: float | None = Field(None, ge=0, le=100)
    assessment_score: float | None = Field(None, ge=0, le=100)
    skill_gap_score: float | None = Field(None, ge=0, le=100)
    demand_score: float | None = Field(None, ge=0, le=100)
    employment_type: str | None = None
    industry: str | None = None
    actual_job_role: str | None = None
    target_job_role: str | None = None
    skills: list[MLSkillProfile] = Field(default_factory=list)
