from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.followup import FollowUp, FollowUpType, FollowUpStatus
from app.models.trainee import Trainee
from app.models.user import User
from app.schemas.followup import FollowUpCreate, FollowUpResponse
from app.schemas.common import APIResponse
from app.auth.dependencies import role_required

router = APIRouter(prefix="/followups", tags=["Follow-ups"])


@router.post("", response_model=APIResponse)
def add_followup(
    payload: FollowUpCreate,
    current_user: User = Depends(role_required("ADMIN")),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/followups
    Tracks long-term outcomes at 30/90/180-day intervals. Access: ADMIN
    """
    try:
        fu_type = FollowUpType(payload.follow_up_type.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid follow_up_type. Must be one of: {[t.value for t in FollowUpType]}",
        )

    try:
        fu_status = FollowUpStatus(payload.status.upper())
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {[s.value for s in FollowUpStatus]}",
        )

    followup = FollowUp(
        trainee_id=payload.trainee_id,
        follow_up_type=fu_type,
        status=fu_status,
        salary=payload.salary,
        feedback=payload.feedback,
    )
    db.add(followup)
    db.commit()
    db.refresh(followup)

    return APIResponse(
        success=True,
        message="Follow-up record created successfully",
        data=FollowUpResponse.model_validate(followup).model_dump(),
    )


@router.get("/{trainee_id}", response_model=APIResponse)
def get_followup_history(
    trainee_id: int,
    current_user: User = Depends(role_required("ADMIN", "TRAINEE")),
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/followups/{trainee_id}
    Returns follow-up history for a trainee.
    """
    followups = (
        db.query(FollowUp)
        .filter(FollowUp.trainee_id == trainee_id)
        .order_by(FollowUp.created_at)
        .all()
    )
    if current_user.role.value == "TRAINEE":
        trainee = db.query(Trainee).filter(Trainee.trainee_id == trainee_id, Trainee.user_id == current_user.id).first()
        if not trainee:
            raise HTTPException(status_code=403, detail="Cannot access another trainee's follow-ups")

    return APIResponse(
        success=True,
        message="Follow-up history retrieved successfully",
        data=[FollowUpResponse.model_validate(f).model_dump() for f in followups],
    )
