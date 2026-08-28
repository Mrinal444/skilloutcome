from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import initialize_database
from app.models import (
    User,
    Trainee,
    TraineeSkill,
    Skill,
    TrainingProgram,
    TrainingEnrollment,
    Employer,
    EmploymentRecord,
    FollowUp,
)
from app.routers import (
    auth,
    trainees,
    skills,
    training,
    employers,
    employment,
    followups,
    analytics,
    ml,
)

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on startup."""
    initialize_database()
    yield


app = FastAPI(
    title="SkillOutcome API",
    description="SIH26135 — Longitudinal skilling-outcomes and impact measurement system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow all origins during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "project": "SkillOutcome",
        "problem_statement": "SIH26135",
    }


# Mount all routers under /api/v1
PREFIX = "/api/v1"
app.include_router(auth.router, prefix=PREFIX)
app.include_router(trainees.router, prefix=PREFIX)
app.include_router(skills.router, prefix=PREFIX)
app.include_router(training.router, prefix=PREFIX)
app.include_router(employers.router, prefix=PREFIX)
app.include_router(employment.router, prefix=PREFIX)
app.include_router(followups.router, prefix=PREFIX)
app.include_router(analytics.router, prefix=PREFIX)
app.include_router(ml.router, prefix=PREFIX)
