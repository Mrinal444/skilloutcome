from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employer import Employer
from app.models.user import User
from app.schemas.employer import EmployerCreate, EmployerUpdate, EmployerResponse, EmployerVerificationUpdate
from app.schemas.common import APIResponse
from app.auth.dependencies import get_current_user, role_required

router = APIRouter(prefix="/employers", tags=["Employers"])


@router.post("", response_model=APIResponse)
def create_employer(
    payload: EmployerCreate,
    current_user: User = Depends(role_required("EMPLOYER", "ADMIN")),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/employers
    Creates employer profile. Access: EMPLOYER / ADMIN
    """
    employer = Employer(
        company_name=payload.company_name,
        industry=payload.industry,
        location=payload.location,
        user_id=current_user.id if current_user.role.value == "EMPLOYER" else None,
    )
    db.add(employer)
    db.commit()
    db.refresh(employer)

    return APIResponse(
        success=True,
        message="Employer created successfully",
        data=EmployerResponse.model_validate(employer).model_dump(),
    )


@router.get("/me", response_model=APIResponse)
def get_my_employer(current_user: User = Depends(role_required("EMPLOYER")), db: Session = Depends(get_db)):
    employer = db.query(Employer).filter(Employer.user_id == current_user.id).first()
    if not employer:
        return APIResponse(
            success=True,
            message="Employer profile not found",
            data=None,
        )
    return APIResponse(success=True, message="Employer profile retrieved successfully",
                       data=EmployerResponse.model_validate(employer).model_dump())


@router.get("", response_model=APIResponse)
def get_employers(current_user: User = Depends(role_required("ADMIN")), db: Session = Depends(get_db)):
    employers = db.query(Employer).order_by(Employer.company_name).all()
    return APIResponse(success=True, message="Employers retrieved successfully",
                       data=[EmployerResponse.model_validate(item).model_dump() for item in employers])


@router.patch("/{employer_id}/verification", response_model=APIResponse)
def update_employer_verification(
    employer_id: int,
    payload: EmployerVerificationUpdate,
    current_user: User = Depends(role_required("ADMIN")),
    db: Session = Depends(get_db),
):
    employer = db.query(Employer).filter(Employer.employer_id == employer_id).first()
    if not employer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer not found")
    employer.verification_status = payload.verification_status
    db.commit()
    db.refresh(employer)
    return APIResponse(success=True, message="Employer verification updated successfully",
                       data=EmployerResponse.model_validate(employer).model_dump())


@router.get("/{employer_id}", response_model=APIResponse)
def get_employer(
    employer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/employers/{employer_id}
    Returns employer details.
    """
    employer = (
        db.query(Employer).filter(Employer.employer_id == employer_id).first()
    )
    if not employer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Employer not found",
        )

    return APIResponse(
        success=True,
        message="Employer retrieved successfully",
        data=EmployerResponse.model_validate(employer).model_dump(),
    )


@router.put("/{employer_id}", response_model=APIResponse)
def update_employer(
    employer_id: int,
    payload: EmployerUpdate,
    current_user: User = Depends(role_required("EMPLOYER", "ADMIN")),
    db: Session = Depends(get_db),
):
    employer = db.query(Employer).filter(Employer.employer_id == employer_id).first()
    if not employer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employer not found")
    if current_user.role.value == "EMPLOYER" and employer.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot update another employer's profile")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(employer, key, value)
    db.commit()
    db.refresh(employer)
    return APIResponse(success=True, message="Employer updated successfully",
                       data=EmployerResponse.model_validate(employer).model_dump())
