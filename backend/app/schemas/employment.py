from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class EmploymentCreate(BaseModel):
    trainee_id: int
    employer_id: int
    job_role: str
    salary: float
    status: str = "EMPLOYED"


class EmploymentUpdate(BaseModel):
    job_role: Optional[str] = None
    salary: Optional[float] = None
    status: Optional[str] = None  # EMPLOYED, RESIGNED, TERMINATED


class EmploymentResponse(BaseModel):
    employment_id: int
    trainee_id: int
    employer_id: int
    job_role: str
    salary: float
    joining_date: Optional[datetime] = None
    status: str

    model_config = {"from_attributes": True}
