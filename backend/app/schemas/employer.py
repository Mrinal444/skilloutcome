from typing import Optional
from pydantic import BaseModel


class EmployerCreate(BaseModel):
    company_name: str
    industry: Optional[str] = None
    location: Optional[str] = None


class EmployerResponse(BaseModel):
    employer_id: int
    company_name: str
    industry: Optional[str] = None
    location: Optional[str] = None
    verification_status: bool = False

    model_config = {"from_attributes": True}
