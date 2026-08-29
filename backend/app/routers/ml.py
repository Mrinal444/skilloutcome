"""Backend-owned endpoints that safely proxy selected ML capabilities."""
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, joinedload

from app.auth.dependencies import get_current_user, role_required
from app.database import get_db
from app.mappers.ml import MLFeaturesIncompleteError, build_skill_gap_payload
from app.models.trainee import Trainee, TraineeSkill
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.ml import (
    AttritionPredictionRequest,
    PlacementPredictionRequest,
    TraineeSkillGapRequest,
)
from app.services.ml_client import MLServiceClient, MLServiceError, get_ml_client

router = APIRouter(tags=["ML"])


def _failure_response(status_code: int, error_code: str, message: str, data: Any = None) -> JSONResponse:
    """Keep proxied ML failures in the application's standard response envelope."""
    response = APIResponse(success=False, message=message, data=data, error_code=error_code)
    return JSONResponse(status_code=status_code, content=response.model_dump())


@router.get("/ml/health", response_model=APIResponse)
async def ml_health(
    _: User = Depends(role_required("ADMIN")),
    client: MLServiceClient = Depends(get_ml_client),
):
    """Expose ML readiness to an authenticated administrator through the backend."""
    try:
        ml_status = await client.health()
    except MLServiceError as error:
        return _failure_response(error.status_code, error.error_code, error.message)
    return APIResponse(success=True, message="ML service health retrieved successfully", data=ml_status)


@router.post("/trainees/{trainee_id}/ml/skill-gap", response_model=APIResponse)
async def trainee_skill_gap(
    trainee_id: int,
    payload: TraineeSkillGapRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    client: MLServiceClient = Depends(get_ml_client),
):
    """Analyze a trainee's persisted skills against a caller-selected target role."""
    if current_user.role.value not in {"ADMIN", "TRAINEE"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only trainees and administrators can request skill-gap analysis",
        )

    trainee = (
        db.query(Trainee)
        .options(joinedload(Trainee.skills).joinedload(TraineeSkill.skill))
        .filter(Trainee.trainee_id == trainee_id)
        .first()
    )
    if not trainee:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trainee not found")
    if current_user.role.value == "TRAINEE" and trainee.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access another trainee's ML analysis",
        )

    try:
        ml_payload = build_skill_gap_payload(trainee, payload.target_job_role)
    except MLFeaturesIncompleteError as error:
        return _failure_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "ML_FEATURES_INCOMPLETE",
            "Required ML feature values are incomplete.",
            {"missing_fields": error.missing_fields},
        )

    try:
        result = await client.skill_gap(ml_payload)
    except MLServiceError as error:
        return _failure_response(error.status_code, error.error_code, error.message)
    return APIResponse(success=True, message="Skill-gap analysis completed successfully", data=result)


@router.post("/ml/predict-placement", response_model=APIResponse)
async def predict_placement(
    payload: PlacementPredictionRequest,
    _: User = Depends(role_required("ADMIN", "TRAINEE")),
    client: MLServiceClient = Depends(get_ml_client),
):
    """Proxy placement prediction through the authenticated application API."""
    try:
        result = await client.predict_placement(payload.model_dump())
    except MLServiceError as error:
        return _failure_response(error.status_code, error.error_code, error.message)
    return APIResponse(success=True, message="Placement prediction completed successfully", data=result)


@router.post("/ml/predict-attrition", response_model=APIResponse)
async def predict_attrition(
    payload: AttritionPredictionRequest,
    _: User = Depends(role_required("ADMIN", "EMPLOYER")),
    client: MLServiceClient = Depends(get_ml_client),
):
    """Proxy attrition prediction through the authenticated application API."""
    try:
        result = await client.predict_attrition(payload.model_dump())
    except MLServiceError as error:
        return _failure_response(error.status_code, error.error_code, error.message)
    return APIResponse(success=True, message="Attrition prediction completed successfully", data=result)
