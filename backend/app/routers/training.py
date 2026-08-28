from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.training import TrainingProgram, TrainingEnrollment, EnrollmentStatus
from app.models.user import User
from app.models.trainee import Trainee
from app.schemas.training import (
    TrainingProgramCreate,
    TrainingProgramResponse,
    EnrollmentCreate,
    EnrollmentUpdate,
    EnrollmentResponse,
)
from app.schemas.common import APIResponse
from app.auth.dependencies import get_current_user, role_required

router = APIRouter(prefix="/training", tags=["Training"])


# ── Training Programs ──────────────────────────────────────────────


@router.post("", response_model=APIResponse)
def create_training_program(
    payload: TrainingProgramCreate,
    current_user: User = Depends(role_required("PROVIDER", "ADMIN")),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/training
    Training providers can add courses. Access: PROVIDER / ADMIN
    """
    program = TrainingProgram(
        name=payload.name,
        provider=payload.provider or current_user.name,
        duration=payload.duration,
        category=payload.category,
        provider_user_id=current_user.id if current_user.role.value == "PROVIDER" else None,
    )
    db.add(program)
    db.commit()
    db.refresh(program)

    return APIResponse(
        success=True,
        message="Training program created successfully",
        data=TrainingProgramResponse.model_validate(program).model_dump(),
    )


@router.get("", response_model=APIResponse)
def get_training_programs(db: Session = Depends(get_db)):
    """
    GET /api/v1/training
    Returns available training programs. Public access.
    """
    programs = db.query(TrainingProgram).all()
    return APIResponse(
        success=True,
        message="Training programs retrieved successfully",
        data=[TrainingProgramResponse.model_validate(p).model_dump() for p in programs],
    )


@router.get("/mine", response_model=APIResponse)
def get_my_training_programs(current_user: User = Depends(role_required("PROVIDER")), db: Session = Depends(get_db)):
    programs = db.query(TrainingProgram).filter(TrainingProgram.provider_user_id == current_user.id).all()
    return APIResponse(success=True, message="Provider programmes retrieved successfully",
                       data=[TrainingProgramResponse.model_validate(p).model_dump() for p in programs])


@router.get("/mine/enrollments", response_model=APIResponse)
def get_my_provider_enrollments(current_user: User = Depends(role_required("PROVIDER")), db: Session = Depends(get_db)):
    enrollments = (db.query(TrainingEnrollment).join(TrainingProgram)
                   .filter(TrainingProgram.provider_user_id == current_user.id).all())
    return APIResponse(success=True, message="Provider enrollments retrieved successfully",
                       data=[EnrollmentResponse.model_validate(e).model_dump() for e in enrollments])


@router.get("/{program_id}", response_model=APIResponse)
def get_training_program(program_id: int, db: Session = Depends(get_db)):
    """
    GET /api/v1/training/{program_id}
    Returns training program details.
    """
    program = (
        db.query(TrainingProgram)
        .filter(TrainingProgram.program_id == program_id)
        .first()
    )
    if not program:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Training program not found",
        )

    return APIResponse(
        success=True,
        message="Training program retrieved successfully",
        data=TrainingProgramResponse.model_validate(program).model_dump(),
    )


# ── Enrollment ─────────────────────────────────────────────────────


@router.post("/enroll", response_model=APIResponse)
def enroll_trainee(
    payload: EnrollmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/training/enroll
    Enrolls trainee into a training program.
    """
    if current_user.role.value == "TRAINEE":
        trainee = db.query(Trainee).filter(Trainee.trainee_id == payload.trainee_id, Trainee.user_id == current_user.id).first()
        if not trainee:
            raise HTTPException(status_code=403, detail="Cannot enroll another trainee")
    if not db.query(TrainingProgram).filter(TrainingProgram.program_id == payload.program_id).first():
        raise HTTPException(status_code=404, detail="Training program not found")
    if db.query(TrainingEnrollment).filter_by(trainee_id=payload.trainee_id, program_id=payload.program_id).first():
        raise HTTPException(status_code=400, detail="Already enrolled in this programme")
    enrollment = TrainingEnrollment(
        trainee_id=payload.trainee_id,
        program_id=payload.program_id,
        status=EnrollmentStatus.ONGOING,
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)

    return APIResponse(
        success=True,
        message="Enrollment successful",
        data=EnrollmentResponse.model_validate(enrollment).model_dump(),
    )


@router.get("/enrollments/{trainee_id}", response_model=APIResponse)
def get_training_enrollments(trainee_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    trainee = db.query(Trainee).filter(Trainee.trainee_id == trainee_id).first()
    if not trainee:
        raise HTTPException(status_code=404, detail="Trainee not found")
    if current_user.role.value == "TRAINEE" and trainee.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access another trainee's enrollments")
    enrollments = db.query(TrainingEnrollment).filter(TrainingEnrollment.trainee_id == trainee_id).all()
    return APIResponse(success=True, message="Training enrollments retrieved successfully",
                       data=[EnrollmentResponse.model_validate(item).model_dump() for item in enrollments])


@router.put("/enrollment/{enrollment_id}", response_model=APIResponse)
def update_enrollment(
    enrollment_id: int,
    payload: EnrollmentUpdate,
    current_user: User = Depends(role_required("PROVIDER", "ADMIN")),
    db: Session = Depends(get_db),
):
    """
    PUT /api/v1/training/enrollment/{id}
    Updates completion status (ONGOING, COMPLETED, DROPPED).
    """
    enrollment = (
        db.query(TrainingEnrollment)
        .filter(TrainingEnrollment.enrollment_id == enrollment_id)
        .first()
    )
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enrollment not found",
        )
    if current_user.role.value == "PROVIDER" and enrollment.program.provider_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot update another provider's enrollment")

    try:
        enrollment.status = EnrollmentStatus(payload.status.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {[s.value for s in EnrollmentStatus]}",
        )

    if payload.score is not None:
        enrollment.score = payload.score
    if payload.completion_date is not None:
        enrollment.completion_date = payload.completion_date
    elif enrollment.status == EnrollmentStatus.COMPLETED and not enrollment.completion_date:
        enrollment.completion_date = datetime.now(timezone.utc)

    db.commit()
    db.refresh(enrollment)

    return APIResponse(
        success=True,
        message="Enrollment updated successfully",
        data=EnrollmentResponse.model_validate(enrollment).model_dump(),
    )
