from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employment import EmploymentRecord, EmploymentStatus
from app.models.employer import Employer
from app.models.trainee import Trainee
from app.models.user import User
from app.schemas.employment import EmploymentCreate, EmploymentUpdate, EmploymentResponse
from app.schemas.common import APIResponse
from app.auth.dependencies import get_current_user, role_required

router = APIRouter(prefix="/employment", tags=["Employment"])


@router.post("", response_model=APIResponse)
def add_employment_record(
    payload: EmploymentCreate,
    current_user: User = Depends(role_required("EMPLOYER", "ADMIN")),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/employment
    Stores employment outcome after training. Access: EMPLOYER / ADMIN
    """
    try:
        emp_status = EmploymentStatus(payload.status.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {[s.value for s in EmploymentStatus]}",
        )
    if current_user.role.value == "EMPLOYER":
        employer = db.query(Employer).filter(Employer.employer_id == payload.employer_id, Employer.user_id == current_user.id).first()
        if not employer:
            raise HTTPException(status_code=403, detail="Cannot use another employer's profile")

    record = EmploymentRecord(
        trainee_id=payload.trainee_id,
        employer_id=payload.employer_id,
        job_role=payload.job_role,
        salary=payload.salary,
        status=emp_status,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return APIResponse(
        success=True,
        message="Employment record created successfully",
        data=EmploymentResponse.model_validate(record).model_dump(),
    )


@router.get("/mine", response_model=APIResponse)
def get_my_employment_records(current_user: User = Depends(role_required("EMPLOYER")), db: Session = Depends(get_db)):
    records = (db.query(EmploymentRecord).join(EmploymentRecord.employer)
               .filter_by(user_id=current_user.id).all())
    return APIResponse(success=True, message="Employer employment records retrieved successfully",
                       data=[EmploymentResponse.model_validate(r).model_dump() for r in records])


@router.get("/{trainee_id}", response_model=APIResponse)
def get_employment_history(
    trainee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/employment/{trainee_id}
    Returns complete employment journey for a trainee.
    """
    if current_user.role.value == "TRAINEE":
        trainee = db.query(Trainee).filter(Trainee.trainee_id == trainee_id).first()
        if not trainee or trainee.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Cannot access another trainee's employment history")
    records = (
        db.query(EmploymentRecord)
        .filter(EmploymentRecord.trainee_id == trainee_id)
        .all()
    )

    return APIResponse(
        success=True,
        message="Employment history retrieved successfully",
        data=[EmploymentResponse.model_validate(r).model_dump() for r in records],
    )


@router.put("/{employment_id}", response_model=APIResponse)
def update_employment(
    employment_id: int,
    payload: EmploymentUpdate,
    current_user: User = Depends(role_required("EMPLOYER", "ADMIN")),
    db: Session = Depends(get_db),
):
    """
    PUT /api/v1/employment/{employment_id}
    Updates employment status, salary, or job role.
    """
    record = (
        db.query(EmploymentRecord)
        .filter(EmploymentRecord.employment_id == employment_id)
        .first()
    )
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employment record not found",
        )
    if current_user.role.value == "EMPLOYER" and record.employer.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update another employer's employment record")

    if payload.status is not None:
        try:
            record.status = EmploymentStatus(payload.status.upper())
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid status. Must be one of: {[s.value for s in EmploymentStatus]}",
            )

    if payload.salary is not None:
        record.salary = payload.salary
    if payload.job_role is not None:
        record.job_role = payload.job_role

    db.commit()
    db.refresh(record)

    return APIResponse(
        success=True,
        message="Employment record updated successfully",
        data=EmploymentResponse.model_validate(record).model_dump(),
    )
