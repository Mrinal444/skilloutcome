from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class TrainingProgramCreate(BaseModel):
    name: str
    provider: str = ""
    duration: Optional[str] = None
    category: Optional[str] = None


class TrainingProgramResponse(BaseModel):
    program_id: int
    name: str
    provider: str
    duration: Optional[str] = None
    category: Optional[str] = None

    model_config = {"from_attributes": True}


class EnrollmentCreate(BaseModel):
    trainee_id: int
    program_id: int


class EnrollmentUpdate(BaseModel):
    status: str  # ONGOING, COMPLETED, DROPPED
    score: Optional[float] = None
    completion_date: Optional[datetime] = None


class EnrollmentResponse(BaseModel):
    enrollment_id: int
    trainee_id: int
    program_id: int
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    status: str
    score: Optional[float] = None

    model_config = {"from_attributes": True}
