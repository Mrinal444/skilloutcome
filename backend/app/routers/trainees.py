from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models.trainee import Trainee, TraineeSkill, SkillLevel
from app.models.skill import Skill
from app.models.user import User
from app.schemas.trainee import TraineeCreate, TraineeUpdate, TraineeResponse, TraineeSkillInfo
from app.schemas.skill import TraineeSkillAssign
from app.schemas.common import APIResponse
from app.auth.dependencies import get_current_user, role_required

router = APIRouter(prefix="/trainees", tags=["Trainees"])


def _build_trainee_response(trainee: Trainee) -> dict:
    """Build a rich trainee response dict including user info and skills."""
    skills = []
    for ts in trainee.skills:
        skills.append(TraineeSkillInfo(
            skill_name=ts.skill.skill_name if ts.skill else "Unknown",
            level=ts.level.value if ts.level else "BEGINNER",
        ))
    return {
        "trainee_id": trainee.trainee_id,
        "user_id": trainee.user_id,
        "education": trainee.education,
        "location": trainee.location,
        "experience": trainee.experience,
        "user_name": trainee.user.name if trainee.user else None,
        "user_email": trainee.user.email if trainee.user else None,
        "skills": [s.model_dump() for s in skills],
    }


@router.post("", response_model=APIResponse)
def create_trainee(
    payload: TraineeCreate,
    current_user: User = Depends(role_required("TRAINEE", "ADMIN")),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/trainees
    Creates trainee profile after registration. Access: TRAINEE / ADMIN
    """
    # Check if trainee profile already exists for this user
    existing = db.query(Trainee).filter(Trainee.user_id == current_user.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trainee profile already exists for this user",
        )

    trainee = Trainee(
        user_id=current_user.id,
        education=payload.education,
        location=payload.location,
        experience=payload.experience,
    )
    db.add(trainee)
    db.commit()
    db.refresh(trainee)

    return APIResponse(
        success=True,
        message="Trainee profile created successfully",
        data=_build_trainee_response(trainee),
    )


@router.get("", response_model=APIResponse)
def get_all_trainees(
    current_user: User = Depends(role_required("ADMIN", "EMPLOYER")),
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/trainees
    Returns list of trainees. Access: ADMIN
    """
    trainees = (
        db.query(Trainee)
        .options(joinedload(Trainee.user), joinedload(Trainee.skills).joinedload(TraineeSkill.skill))
        .all()
    )
    return APIResponse(
        success=True,
        message="Trainees retrieved successfully",
        data=[_build_trainee_response(t) for t in trainees],
    )


@router.get("/me", response_model=APIResponse)
def get_my_trainee(current_user: User = Depends(role_required("TRAINEE")), db: Session = Depends(get_db)):
    trainee = (db.query(Trainee)
               .options(joinedload(Trainee.user), joinedload(Trainee.skills).joinedload(TraineeSkill.skill))
               .filter(Trainee.user_id == current_user.id).first())
    if not trainee:
        raise HTTPException(status_code=404, detail="Trainee profile not found")
    return APIResponse(success=True, message="Trainee profile retrieved successfully", data=_build_trainee_response(trainee))


@router.get("/{trainee_id}", response_model=APIResponse)
def get_trainee(
    trainee_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    GET /api/v1/trainees/{trainee_id}
    Returns complete trainee information including skills, training, employment.
    """
    trainee = (
        db.query(Trainee)
        .options(joinedload(Trainee.user), joinedload(Trainee.skills).joinedload(TraineeSkill.skill))
        .filter(Trainee.trainee_id == trainee_id)
        .first()
    )
    if not trainee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainee not found",
        )
    if current_user.role.value == "TRAINEE" and trainee.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Cannot access another trainee's profile")

    return APIResponse(
        success=True,
        message="Trainee retrieved successfully",
        data=_build_trainee_response(trainee),
    )


@router.put("/{trainee_id}", response_model=APIResponse)
def update_trainee(
    trainee_id: int,
    payload: TraineeUpdate,
    current_user: User = Depends(role_required("TRAINEE", "ADMIN")),
    db: Session = Depends(get_db),
):
    """
    PUT /api/v1/trainees/{trainee_id}
    Updates trainee information.
    """
    trainee = db.query(Trainee).filter(Trainee.trainee_id == trainee_id).first()
    if not trainee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainee not found",
        )
    # Only allow trainee to update own profile (admins can update any)
    if current_user.role.value != "ADMIN" and trainee.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot update another trainee's profile",
        )

    update_data = payload.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(trainee, key, value)

    db.commit()
    db.refresh(trainee)

    return APIResponse(
        success=True,
        message="Trainee updated successfully",
        data=_build_trainee_response(trainee),
    )


@router.post("/{trainee_id}/skills", response_model=APIResponse)
def assign_skills(
    trainee_id: int,
    payload: TraineeSkillAssign,
    current_user: User = Depends(role_required("TRAINEE", "ADMIN")),
    db: Session = Depends(get_db),
):
    """
    POST /api/v1/trainees/{trainee_id}/skills
    Assigns skills to trainee. Creates skills if they don't exist.
    """
    trainee = db.query(Trainee).filter(Trainee.trainee_id == trainee_id).first()
    if not trainee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trainee not found",
        )
    if current_user.role.value == "TRAINEE" and trainee.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot modify another trainee's skills")

    added_skills = []
    for skill_item in payload.skills:
        # Find or create the skill
        skill = db.query(Skill).filter(Skill.skill_name == skill_item.name).first()
        if not skill:
            skill = Skill(skill_name=skill_item.name, category="General")
            db.add(skill)
            db.flush()

        # Check if already assigned
        existing = (
            db.query(TraineeSkill)
            .filter(
                TraineeSkill.trainee_id == trainee_id,
                TraineeSkill.skill_id == skill.skill_id,
            )
            .first()
        )
        if existing:
            # Update the level
            try:
                existing.level = SkillLevel(skill_item.level.upper())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid skill level")
        else:
            try:
                level = SkillLevel(skill_item.level.upper())
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid skill level")

            ts = TraineeSkill(
                trainee_id=trainee_id,
                skill_id=skill.skill_id,
                level=level,
            )
            db.add(ts)

        added_skills.append({"name": skill_item.name, "level": skill_item.level})

    db.commit()

    return APIResponse(
        success=True,
        message="Skills assigned successfully",
        data=added_skills,
    )
