from app.schemas.common import APIResponse
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.schemas.trainee import TraineeCreate, TraineeUpdate, TraineeResponse
from app.schemas.skill import SkillCreate, SkillResponse, TraineeSkillAssign
from app.schemas.training import (
    TrainingProgramCreate,
    TrainingProgramResponse,
    EnrollmentCreate,
    EnrollmentUpdate,
    EnrollmentResponse,
)
from app.schemas.employer import EmployerCreate, EmployerResponse
from app.schemas.employment import (
    EmploymentCreate,
    EmploymentUpdate,
    EmploymentResponse,
)
from app.schemas.followup import FollowUpCreate, FollowUpResponse
from app.schemas.analytics import (
    DashboardResponse,
    ProviderAnalytics,
    SkillGapResponse,
    DistrictAnalytics,
)
