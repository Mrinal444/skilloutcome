from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class FollowUpCreate(BaseModel):
    trainee_id: int
    follow_up_type: str  # DAY_30, DAY_90, DAY_180
    status: str  # EMPLOYED, UNEMPLOYED, SELF_EMPLOYED, FURTHER_TRAINING
    salary: Optional[float] = None
    feedback: Optional[str] = None


class FollowUpResponse(BaseModel):
    followup_id: int
    trainee_id: int
    follow_up_type: str
    status: str
    salary: Optional[float] = None
    feedback: Optional[str] = None
    created_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
