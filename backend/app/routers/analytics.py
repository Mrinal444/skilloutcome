from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, case, and_

from app.database import get_db
from app.models.trainee import Trainee, TraineeSkill
from app.models.skill import Skill
from app.models.training import TrainingProgram, TrainingEnrollment, EnrollmentStatus
from app.models.employment import EmploymentRecord, EmploymentStatus
from app.models.followup import FollowUp, FollowUpType, FollowUpStatus
from app.models.user import User
from app.schemas.analytics import (
    DashboardResponse,
    ProviderAnalytics,
    SkillGapResponse,
    SkillGapItem,
    DistrictAnalytics,
)
from app.schemas.common import APIResponse
from app.auth.dependencies import role_required

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=APIResponse)
def get_dashboard(
    current_user: User = Depends(role_required("ADMIN")),
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/analytics/dashboard
    Provides overall program insights: total trainees, placement rate,
    retention rate, and average salary growth.
    """
    total_trainees = db.query(func.count(Trainee.trainee_id)).scalar() or 0

    # Placement rate: trainees who have at least one EMPLOYED record / total trainees
    employed_trainees = (
        db.query(func.count(func.distinct(EmploymentRecord.trainee_id)))
        .filter(EmploymentRecord.status == EmploymentStatus.EMPLOYED)
        .scalar()
        or 0
    )
    placement_rate = (
        round((employed_trainees / total_trainees) * 100, 1) if total_trainees > 0 else 0
    )

    # Retention rate: trainees with a DAY_180 follow-up showing EMPLOYED / total at DAY_180
    total_180 = (
        db.query(func.count(FollowUp.followup_id))
        .filter(FollowUp.follow_up_type == FollowUpType.DAY_180)
        .scalar()
        or 0
    )
    retained_180 = (
        db.query(func.count(FollowUp.followup_id))
        .filter(
            FollowUp.follow_up_type == FollowUpType.DAY_180,
            FollowUp.status == FollowUpStatus.EMPLOYED,
        )
        .scalar()
        or 0
    )
    retention_rate = (
        round((retained_180 / total_180) * 100, 1) if total_180 > 0 else 0
    )

    # ── Salary growth: single SQL query using MIN/MAX per trainee ──────────────
    # Compare DAY_30 avg salary vs DAY_180 avg salary per trainee, then aggregate
    early_sub = (
        db.query(
            FollowUp.trainee_id,
            func.avg(FollowUp.salary).label("avg_early"),
        )
        .filter(
            FollowUp.follow_up_type == FollowUpType.DAY_30,
            FollowUp.salary.isnot(None),
        )
        .group_by(FollowUp.trainee_id)
        .subquery()
    )

    late_sub = (
        db.query(
            FollowUp.trainee_id,
            func.avg(FollowUp.salary).label("avg_late"),
        )
        .filter(
            FollowUp.follow_up_type == FollowUpType.DAY_180,
            FollowUp.salary.isnot(None),
        )
        .group_by(FollowUp.trainee_id)
        .subquery()
    )

    growth_rows = (
        db.query(early_sub.c.avg_early, late_sub.c.avg_late)
        .join(late_sub, early_sub.c.trainee_id == late_sub.c.trainee_id)
        .filter(early_sub.c.avg_early > 0)
        .all()
    )

    growths = [
        ((late - early) / early) * 100
        for early, late in growth_rows
        if early and early > 0
    ]
    avg_salary_growth = round(sum(growths) / len(growths), 1) if growths else 0

    return APIResponse(
        success=True,
        message="Dashboard analytics retrieved successfully",
        data=DashboardResponse(
            total_trainees=total_trainees,
            placement_rate=placement_rate,
            retention_rate=retention_rate,
            average_salary_growth=avg_salary_growth,
        ).model_dump(),
    )


@router.get("/providers", response_model=APIResponse)
def get_provider_analytics(
    current_user: User = Depends(role_required("ADMIN")),
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/analytics/providers
    Compare training providers by placement rate, completion rate,
    retention, and salary outcomes — fully SQL-aggregated, no per-provider loops.
    """
    # Total + completed enrollments per provider in one query
    enrollment_stats = (
        db.query(
            TrainingProgram.provider,
            func.count(TrainingEnrollment.enrollment_id).label("total_enrollments"),
            func.sum(
                case(
                    (TrainingEnrollment.status == EnrollmentStatus.COMPLETED, 1),
                    else_=0,
                )
            ).label("completed_count"),
        )
        .join(TrainingEnrollment, TrainingEnrollment.program_id == TrainingProgram.program_id)
        .group_by(TrainingProgram.provider)
        .all()
    )

    # Completed trainees per provider → join to employment to get placement & avg salary
    completed_trainee_sub = (
        db.query(
            TrainingProgram.provider,
            TrainingEnrollment.trainee_id,
        )
        .join(TrainingEnrollment, TrainingEnrollment.program_id == TrainingProgram.program_id)
        .filter(TrainingEnrollment.status == EnrollmentStatus.COMPLETED)
        .distinct()
        .subquery()
    )

    employment_stats = (
        db.query(
            completed_trainee_sub.c.provider,
            func.count(func.distinct(
                case(
                    (EmploymentRecord.status == EmploymentStatus.EMPLOYED, EmploymentRecord.trainee_id),
                    else_=None,
                )
            )).label("employed_count"),
            func.avg(EmploymentRecord.salary).label("avg_salary"),
            func.count(func.distinct(completed_trainee_sub.c.trainee_id)).label("total_completed_trainees"),
        )
        .outerjoin(
            EmploymentRecord,
            EmploymentRecord.trainee_id == completed_trainee_sub.c.trainee_id,
        )
        .group_by(completed_trainee_sub.c.provider)
        .all()
    )

    # Build lookup maps
    emp_map = {
        row.provider: row for row in employment_stats
    }

    result = []
    for row in enrollment_stats:
        prov = row.provider
        total = row.total_enrollments or 0
        completed = row.completed_count or 0
        completion_rate = round((completed / total) * 100, 1) if total > 0 else 0

        emp = emp_map.get(prov)
        employed_count = emp.employed_count or 0 if emp else 0
        total_completed = emp.total_completed_trainees or 0 if emp else 0
        avg_salary = round(emp.avg_salary or 0, 0) if emp else 0
        placement_rate = (
            round((employed_count / total_completed) * 100, 1)
            if total_completed > 0
            else 0
        )

        result.append(
            ProviderAnalytics(
                provider=prov,
                total_enrollments=total,
                completion_rate=completion_rate,
                placement_rate=placement_rate,
                average_salary=avg_salary,
            ).model_dump()
        )

    return APIResponse(
        success=True,
        message="Provider analytics retrieved successfully",
        data=result,
    )


@router.get("/skill-gaps", response_model=APIResponse)
def get_skill_gaps(
    current_user: User = Depends(role_required("ADMIN")),
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/analytics/skill-gaps
    Identify skills with fewest trainee coverage — those represent the biggest gaps.
    Uses LEFT JOIN to include skills with zero trainee assignments.
    """
    rows = (
        db.query(
            Skill.skill_name,
            func.count(TraineeSkill.id).label("trainee_count"),
        )
        .outerjoin(TraineeSkill, TraineeSkill.skill_id == Skill.skill_id)
        .group_by(Skill.skill_name)
        .order_by(func.count(TraineeSkill.id).asc())
        .all()
    )

    gaps = [SkillGapItem(skill_name=name, demand_count=cnt or 0) for name, cnt in rows]
    top_gaps = [g.skill_name for g in gaps[:10]]

    return APIResponse(
        success=True,
        message="Skill gap analytics retrieved successfully",
        data=SkillGapResponse(
            top_skill_gaps=top_gaps,
            details=[g.model_dump() for g in gaps],
        ).model_dump(),
    )


@router.get("/districts", response_model=APIResponse)
def get_district_analytics(
    current_user: User = Depends(role_required("ADMIN")),
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/analytics/districts
    Geographic outcome breakdown — single SQL query via GROUP BY + LEFT JOIN.
    No per-district Python loop.
    """
    rows = (
        db.query(
            Trainee.location,
            func.count(Trainee.trainee_id).label("total"),
            func.count(
                case(
                    (EmploymentRecord.status == EmploymentStatus.EMPLOYED, Trainee.trainee_id),
                    else_=None,
                )
            ).label("employed"),
            func.avg(EmploymentRecord.salary).label("avg_salary"),
        )
        .outerjoin(EmploymentRecord, EmploymentRecord.trainee_id == Trainee.trainee_id)
        .filter(Trainee.location.isnot(None))
        .group_by(Trainee.location)
        .order_by(Trainee.location)
        .all()
    )

    result = []
    for location, total, employed, avg_sal in rows:
        placement_rate = round((employed / total) * 100, 1) if total > 0 else 0
        result.append(
            DistrictAnalytics(
                location=location,
                total_trainees=total,
                placement_rate=placement_rate,
                average_salary=round(avg_sal or 0, 0),
            ).model_dump()
        )

    return APIResponse(
        success=True,
        message="District analytics retrieved successfully",
        data=result,
    )
