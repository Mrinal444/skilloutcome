from typing import Optional, List
from pydantic import BaseModel


class SkillCreate(BaseModel):
    skill_name: str
    category: Optional[str] = None


class SkillResponse(BaseModel):
    skill_id: int
    skill_name: str
    category: Optional[str] = None

    model_config = {"from_attributes": True}


class SkillAssignItem(BaseModel):
    name: str
    level: str = "BEGINNER"  # BEGINNER, INTERMEDIATE, ADVANCED


class TraineeSkillAssign(BaseModel):
    skills: List[SkillAssignItem]
