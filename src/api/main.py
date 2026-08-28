"""Decision-support API for normalized SkillOutcome data."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import joblib
import pandas as pd
import sklearn
import xgboost
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator, model_validator

from src.modeling.features import MODEL_BUNDLE_SCHEMA_VERSION, attrition_api_frame, feature_contract_fingerprint, load_role_requirements, placement_api_frame, skill_gap_analysis

PROJECT_ROOT = Path(__file__).resolve().parents[2]
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data" / "processed"
app = FastAPI(title="SkillOutcome ML API", version="2.1.0", description="Longitudinal skilling-outcome decision support.")


class SkillProfile(BaseModel):
    name: str = Field(..., min_length=1)
    proficiency: float = Field(..., ge=0, le=100)

    @field_validator("name")
    @classmethod
    def nonblank_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Skill name cannot be blank")
        return value


class SkillRequirement(BaseModel):
    name: str = Field(..., min_length=1)
    required_proficiency: float = Field(..., ge=0, le=100)
    importance_weight: float = Field(1.0, gt=0, le=1)


class PlacementRequest(BaseModel):
    education_level: str
    target_job_role: str
    skills: list[SkillProfile] = Field(..., min_length=1)
    attendance_percent: float = Field(..., ge=0, le=100)
    assessment_score: float = Field(..., ge=0, le=100)
    training_performance: float | None = Field(None, ge=0, le=100)
    training_duration_weeks: float | None = Field(None, ge=0, le=104)
    previous_experience_years: float | None = Field(None, ge=0, le=60)
    course: str | None = None
    training_provider: str | None = None
    rural_urban: str | None = None
    state: str | None = None
    district: str | None = None
    certification: bool = False
    internship: bool = False


class PlacementResponse(BaseModel):
    placement_probability: float
    placement_probability_percent: float
    support_priority: str
    support_priority_thresholds: dict
    skill_gap_score: float
    missing_skills: list[str]
    recommendations: list[dict]
    model: str
    input_warnings: list[str] = []


class AttritionRequest(BaseModel):
    employment_duration_months: float = Field(..., ge=0, le=600)
    salary_lpa: float = Field(..., ge=0, le=1000)
    job_history: int = Field(..., ge=0, le=100)
    engagement_score: float = Field(..., ge=0, le=10)
    attendance_percent: float | None = Field(None, ge=0, le=100)
    assessment_score: float | None = Field(None, ge=0, le=100)
    skill_gap_score: float | None = Field(None, ge=0, le=100)
    demand_score: float | None = Field(None, ge=0, le=100)
    employment_type: str | None = None
    industry: str | None = None
    actual_job_role: str | None = None
    target_job_role: str | None = None
    skills: list[SkillProfile] = Field(default_factory=list)


class AttritionResponse(BaseModel):
    risk: str
    attrition_probability: float
    model: str
    input_warnings: list[str] = []


class SkillGapRequest(BaseModel):
    current_skills: list[SkillProfile] = Field(default_factory=list)
    target_job_role: str | None = None
    required_skills: list[SkillRequirement] = Field(default_factory=list)

    @model_validator(mode="after")
    def has_requirement_source(self) -> "SkillGapRequest":
        if not self.target_job_role and not self.required_skills:
            raise ValueError("Provide target_job_role or required_skills")
        return self


class SkillGapResponse(BaseModel):
    target_job_role: str | None
    missing_skills: list[str]
    matched_skills: list[str]
    below_required_proficiency: list[dict]
    skill_gap_score: float
    skill_coverage_percent: float
    recommendations: list[dict]


class StaleModelError(RuntimeError):
    """Raised when a saved model cannot safely serve under the current contract."""


@lru_cache(maxsize=2)
def _load_bundle(model_name: str) -> dict:
    path = MODELS_DIR / f"{model_name}.joblib"
    if not path.exists():
        raise FileNotFoundError(path)
    bundle = joblib.load(path)
    if not isinstance(bundle, dict) or "pipeline" not in bundle:
        raise ValueError(f"Invalid model bundle: {path}")
    metadata = bundle.get("metadata", {})
    if not isinstance(metadata, dict):
        raise ValueError(f"Invalid model metadata: {path}")
    if metadata.get("bundle_schema_version") != MODEL_BUNDLE_SCHEMA_VERSION:
        raise StaleModelError(f"{model_name} uses model-bundle schema {metadata.get('bundle_schema_version', 'unknown')} but this service requires {MODEL_BUNDLE_SCHEMA_VERSION}. Retrain with python -m src.modeling.train.")
    stored = metadata.get("feature_contract_fingerprint")
    if stored != feature_contract_fingerprint():
        raise StaleModelError(f"{model_name} was trained on feature contract {stored or 'unknown'} but the code expects {feature_contract_fingerprint()}. Retrain with python -m src.modeling.train.")
    report = metadata.get("report")
    threshold_key = "support_thresholds" if model_name == "placement_model" else "risk_thresholds"
    if not isinstance(report, dict) or not isinstance(report.get("calibration"), dict) or threshold_key not in report:
        raise StaleModelError(f"{model_name} is missing calibrated probability or threshold metadata. Retrain with python -m src.modeling.train.")
    expected_versions = {"scikit_learn": sklearn.__version__, "xgboost": xgboost.__version__, "pandas": pd.__version__}
    if metadata.get("runtime_versions") != expected_versions:
        raise StaleModelError(f"{model_name} was trained with different package versions. Recreate the pinned environment and retrain with python -m src.modeling.train.")
    return bundle


@lru_cache(maxsize=1)
def _requirements() -> dict:
    return load_role_requirements(DATA_DIR / "role_skill_requirements.csv")


@lru_cache(maxsize=1)
def _demand() -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / "job_demand_snapshots.csv")


@lru_cache(maxsize=1)
def _vocabularies() -> dict:
    """Controlled values observed in the prepared data, for the ingestion layer to bind to."""
    trainees = pd.read_csv(DATA_DIR / "trainees.csv", usecols=["State", "District", "Rural_Urban", "Education_Level"])
    training = pd.read_csv(DATA_DIR / "training_completions.csv", usecols=["Course", "Training_Provider", "Target_Job_Role"])
    employment = pd.read_csv(DATA_DIR / "employment_spells.csv", usecols=["Employment_Type", "Industry", "Actual_Job_Role"])

    def unique(frame: pd.DataFrame, column: str) -> list[str]:
        return sorted(frame[column].dropna().astype(str).unique().tolist())

    return {
        "education_levels": unique(trainees, "Education_Level"), "rural_urban": unique(trainees, "Rural_Urban"),
        "courses": unique(training, "Course"), "training_providers": unique(training, "Training_Provider"),
        "target_job_roles": unique(training, "Target_Job_Role"), "actual_job_roles": unique(employment, "Actual_Job_Role"),
        "employment_types": unique(employment, "Employment_Type"), "industries": unique(employment, "Industry"),
        "states": unique(trainees, "State"),
        "districts_by_state": {state: sorted(group["District"].dropna().astype(str).unique().tolist()) for state, group in trainees.groupby("State")},
    }


def _bundle_or_503(model_name: str) -> dict:
    try:
        return _load_bundle(model_name)
    except StaleModelError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    except (FileNotFoundError, ValueError, OSError) as error:
        raise HTTPException(status_code=503, detail=f"{model_name} is unavailable. Run data preparation and training first.") from error


def _input_warnings(payload: dict, fields: dict[str, str]) -> list[str]:
    """Flag values the models never saw, so the caller can fix its mapping instead of guessing."""
    try:
        vocabularies = _vocabularies()
    except (FileNotFoundError, ValueError, OSError):
        return []
    warnings = []
    for field, vocabulary in fields.items():
        value = payload.get(field)
        if value and str(value) not in vocabularies[vocabulary]:
            warnings.append(f"{field}='{value}' is not in the prepared data ({vocabulary}); the model treats it as unknown. See GET /reference/vocabularies.")
    return warnings


def _support_priority(probability: float, report: dict) -> tuple[str, dict]:
    """Support priority rises as placement probability falls, so the comparisons invert."""
    thresholds = report.get("support_thresholds", {"high": 0.35, "medium": 0.5})
    cuts = {"high": float(thresholds["high"]), "medium": float(thresholds["medium"])}
    priority = "High" if probability <= cuts["high"] else "Medium" if probability <= cuts["medium"] else "Low"
    return priority, cuts


def _requirements_for_role(role: str) -> list[dict]:
    try:
        return _requirements()[role]
    except (FileNotFoundError, KeyError) as error:
        raise HTTPException(status_code=422, detail=f"Unknown target_job_role: {role}") from error


def _demand_for_role(role: str, state: str | None, district: str | None) -> float:
    try:
        demand = _demand()
    except FileNotFoundError as error:
        raise HTTPException(status_code=503, detail="Demand data is unavailable. Run data preparation first.") from error
    selected = demand[demand["Target_Job_Role"].eq(role)]
    if state:
        selected = selected[selected["State"].eq(state)]
    if district:
        selected = selected[selected["District"].eq(district)]
    return float(selected.sort_values("Snapshot_Date").iloc[-1]["Demand_Score"]) if not selected.empty else float(demand[demand["Target_Job_Role"].eq(role)]["Demand_Score"].mean())


@app.get("/")
def root() -> dict:
    return {"status": "ok", "service": "SkillOutcome ML API", "version": "2.1.0", "docs": "/docs"}


@app.get("/health")
def health() -> dict:
    status = {"status": "ok", "placement_model_available": (MODELS_DIR / "placement_model.joblib").exists(), "attrition_model_available": (MODELS_DIR / "attrition_model.joblib").exists(), "normalized_data_available": (DATA_DIR / "role_skill_requirements.csv").exists(), "expected_feature_contract": feature_contract_fingerprint(), "models_match_feature_contract": {}}
    for model_name in ["placement_model", "attrition_model"]:
        try:
            _load_bundle(model_name)
            status["models_match_feature_contract"][model_name] = True
        except StaleModelError:
            status["models_match_feature_contract"][model_name] = False
        except (FileNotFoundError, ValueError, OSError):
            status["models_match_feature_contract"][model_name] = None
    return status


@app.get("/reference/roles")
def reference_roles() -> dict:
    """Target roles the models know, with the skill requirements used for gap scoring."""
    try:
        requirements = _requirements()
    except (FileNotFoundError, ValueError, OSError) as error:
        raise HTTPException(status_code=503, detail="Role requirements are unavailable. Run data preparation first.") from error
    return {"target_job_roles": sorted(requirements), "requirements": requirements}


@app.get("/reference/vocabularies")
def reference_vocabularies() -> dict:
    """Controlled values for platform-supplied fields, so callers never invent categories."""
    try:
        return _vocabularies()
    except (FileNotFoundError, ValueError, OSError) as error:
        raise HTTPException(status_code=503, detail="Reference data is unavailable. Run data preparation first.") from error


@app.post("/predict-placement", response_model=PlacementResponse)
def predict_placement(request: PlacementRequest) -> PlacementResponse:
    bundle = _bundle_or_503("placement_model")
    payload = request.model_dump()
    gap = skill_gap_analysis(payload["skills"], _requirements_for_role(payload["target_job_role"]))
    probability = float(bundle["pipeline"].predict_proba(placement_api_frame(payload, gap, _demand_for_role(payload["target_job_role"], payload.get("state"), payload.get("district"))))[0, 1])
    warnings = _input_warnings(payload, {"education_level": "education_levels", "course": "courses", "training_provider": "training_providers", "rural_urban": "rural_urban", "state": "states"})
    priority, cuts = _support_priority(probability, bundle["metadata"]["report"])
    return PlacementResponse(placement_probability=round(probability, 4), placement_probability_percent=round(probability * 100, 2), support_priority=priority, support_priority_thresholds=cuts, skill_gap_score=gap["skill_gap_score"], missing_skills=gap["missing_skills"], recommendations=gap["recommendations"], model=bundle["metadata"]["report"]["selected_algorithm"], input_warnings=warnings)


@app.post("/predict-attrition", response_model=AttritionResponse)
def predict_attrition(request: AttritionRequest) -> AttritionResponse:
    bundle = _bundle_or_503("attrition_model")
    payload = request.model_dump()
    probability = float(bundle["pipeline"].predict_proba(attrition_api_frame(payload))[0, 1])
    thresholds = bundle["metadata"]["report"].get("risk_thresholds", {"medium": 0.15, "high": 0.30})
    risk = "High" if probability >= thresholds["high"] else "Medium" if probability >= thresholds["medium"] else "Low"
    warnings = _input_warnings(payload, {"employment_type": "employment_types", "industry": "industries", "actual_job_role": "actual_job_roles", "target_job_role": "target_job_roles"})
    return AttritionResponse(risk=risk, attrition_probability=round(probability, 4), model=bundle["metadata"]["report"]["selected_algorithm"], input_warnings=warnings)


@app.post("/skill-gap", response_model=SkillGapResponse)
def skill_gap(request: SkillGapRequest) -> SkillGapResponse:
    requirements = _requirements_for_role(request.target_job_role) if request.target_job_role else [item.model_dump() for item in request.required_skills]
    result = skill_gap_analysis([item.model_dump() for item in request.current_skills], requirements)
    return SkillGapResponse(target_job_role=request.target_job_role, **result)
