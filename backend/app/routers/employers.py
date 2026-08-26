from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.employer import Employer
from app.models.user import User
from app.schemas.employer import EmployerCreate, EmployerResponse
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
    )
    db.add(employer)
    db.commit()
    db.refresh(employer)

    return APIResponse(
        success=True,
        message="Employer created successfully",
        data=EmployerResponse.model_validate(employer).model_dump(),
    )


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
