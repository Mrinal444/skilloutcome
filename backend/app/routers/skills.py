from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.skill import Skill
from app.schemas.skill import SkillCreate, SkillResponse
from app.schemas.common import APIResponse

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("", response_model=APIResponse)
def get_skills(db: Session = Depends(get_db)):
    """
    GET /api/v1/skills
    Returns available skills. Public access.
    """
    skills = db.query(Skill).all()
    return APIResponse(
        success=True,
        message="Skills retrieved successfully",
        data=[SkillResponse.model_validate(s).model_dump() for s in skills],
    )


@router.post("", response_model=APIResponse)
def create_skill(payload: SkillCreate, db: Session = Depends(get_db)):
    """
    POST /api/v1/skills
    Creates a new skill entry.
    """
    existing = db.query(Skill).filter(Skill.skill_name == payload.skill_name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Skill already exists",
        )

    skill = Skill(skill_name=payload.skill_name, category=payload.category)
    db.add(skill)
    db.commit()
    db.refresh(skill)

    return APIResponse(
        success=True,
        message="Skill created successfully",
        data=SkillResponse.model_validate(skill).model_dump(),
    )
