from typing import Optional, List
from pydantic import BaseModel


class TraineeCreate(BaseModel):
    education: Optional[str] = None
    location: Optional[str] = None
    experience: Optional[int] = 0


class TraineeUpdate(BaseModel):
    education: Optional[str] = None
    location: Optional[str] = None
    experience: Optional[int] = None


class TraineeSkillInfo(BaseModel):
    skill_name: str
    level: str

    model_config = {"from_attributes": True}


class TraineeResponse(BaseModel):
    trainee_id: int
    user_id: int
    education: Optional[str] = None
    location: Optional[str] = None
    experience: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    skills: Optional[List[TraineeSkillInfo]] = []

    model_config = {"from_attributes": True}
