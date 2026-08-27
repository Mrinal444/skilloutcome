from typing import List, Optional
from pydantic import BaseModel


class DashboardResponse(BaseModel):
    total_trainees: int
    placement_rate: float
    retention_rate: float
    average_salary_growth: float


class ProviderAnalytics(BaseModel):
    provider: str
    total_enrollments: int
    completion_rate: float
    placement_rate: float
    average_salary: float


class SkillGapItem(BaseModel):
    skill_name: str
    demand_count: int


class SkillGapResponse(BaseModel):
    top_skill_gaps: List[str]
    details: Optional[List[SkillGapItem]] = []


class DistrictAnalytics(BaseModel):
    location: str
    total_trainees: int
    placement_rate: float
    average_salary: float
