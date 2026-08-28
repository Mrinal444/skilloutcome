"""API contract tests. The API is an internal service boundary: callers must send values
that already exist in the prepared data, and the endpoints have to say so when they do not.
"""
import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient  # noqa: E402

from src.api.main import app  # noqa: E402
from src.modeling.features import feature_contract_fingerprint  # noqa: E402

client = TestClient(app)
SKILLS = [{"name": "Python", "proficiency": 82}, {"name": "SQL", "proficiency": 76}, {"name": "Power BI", "proficiency": 68}]
PLACEMENT_PAYLOAD = {"education_level": "Graduate", "target_job_role": "Data Analyst", "skills": SKILLS, "attendance_percent": 91, "assessment_score": 84, "training_duration_weeks": 12, "course": "Data Analytics", "state": "Karnataka", "district": "Bengaluru", "certification": True, "internship": True}
ATTRITION_PAYLOAD = {"employment_duration_months": 3, "salary_lpa": 4.8, "job_history": 1, "engagement_score": 7.8, "employment_type": "Full-time", "industry": "IT Services", "actual_job_role": "Data Analyst", "target_job_role": "Data Analyst", "skills": SKILLS}


def _model_status() -> dict:
    return client.get("/health").json()["models_match_feature_contract"]


serving_ready = pytest.mark.skipif(not all(_model_status().get(name) for name in ["placement_model", "attrition_model"]), reason="Models are missing or stale; run python -m src.modeling.train.")


def test_health_reports_the_expected_feature_contract():
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert body["normalized_data_available"]
    assert body["expected_feature_contract"] == feature_contract_fingerprint()
    assert set(body["models_match_feature_contract"]) == {"placement_model", "attrition_model"}


def test_reference_roles_expose_the_gap_requirements():
    body = client.get("/reference/roles").json()
    assert "Data Analyst" in body["target_job_roles"]
    requirement = body["requirements"]["Data Analyst"][0]
    assert {"name", "required_proficiency", "importance_weight"} <= set(requirement)


def test_reference_vocabularies_cover_platform_supplied_fields():
    body = client.get("/reference/vocabularies").json()
    for field in ["education_levels", "courses", "training_providers", "target_job_roles", "actual_job_roles", "employment_types", "industries", "states", "districts_by_state", "rural_urban"]:
        assert body[field], field
    assert set(body["districts_by_state"]) <= set(body["states"])


def test_skill_gap_accepts_a_role_or_explicit_requirements():
    by_role = client.post("/skill-gap", json={"target_job_role": "Data Analyst", "current_skills": SKILLS})
    assert by_role.status_code == 200
    assert by_role.json()["target_job_role"] == "Data Analyst"
    assert by_role.json()["recommendations"]
    explicit = client.post("/skill-gap", json={"current_skills": SKILLS, "required_skills": [{"name": "Kubernetes", "required_proficiency": 70, "importance_weight": 1.0}]})
    assert explicit.status_code == 200
    assert explicit.json()["missing_skills"] == ["Kubernetes"]
    assert explicit.json()["skill_coverage_percent"] == 0.0


def test_invalid_requests_are_rejected_before_scoring():
    assert client.post("/skill-gap", json={"current_skills": SKILLS}).status_code == 422
    assert client.post("/predict-placement", json={**PLACEMENT_PAYLOAD, "attendance_percent": 140}).status_code == 422
    assert client.post("/predict-placement", json={**PLACEMENT_PAYLOAD, "skills": []}).status_code == 422
    unknown_role = client.post("/predict-placement", json={**PLACEMENT_PAYLOAD, "target_job_role": "Astronaut"})
    assert unknown_role.status_code in {422, 503}


@serving_ready
def test_prediction_endpoints_return_calibrated_decisions():
    placement = client.post("/predict-placement", json=PLACEMENT_PAYLOAD)
    assert placement.status_code == 200
    body = placement.json()
    assert 0 <= body["placement_probability"] <= 1
    assert body["placement_probability_percent"] == pytest.approx(body["placement_probability"] * 100, abs=0.01)
    assert body["skill_gap_score"] >= 0
    assert body["input_warnings"] == []
    # Support priority must be the inverse of placement probability: low chance of placement,
    # high priority for counselling. Assert the band agrees with the thresholds it reports.
    cuts = body["support_priority_thresholds"]
    assert 0 <= cuts["high"] <= cuts["medium"] <= 1
    expected = "High" if body["placement_probability"] <= cuts["high"] else "Medium" if body["placement_probability"] <= cuts["medium"] else "Low"
    assert body["support_priority"] == expected
    attrition = client.post("/predict-attrition", json=ATTRITION_PAYLOAD)
    assert attrition.status_code == 200
    assert attrition.json()["risk"] in {"Low", "Medium", "High"}
    assert attrition.json()["input_warnings"] == []


@serving_ready
def test_unseen_categories_are_reported_as_input_warnings():
    """Values the models never saw are answered, but flagged for the ingestion layer to fix."""
    response = client.post("/predict-placement", json={**PLACEMENT_PAYLOAD, "course": "Underwater Welding"})
    assert response.status_code == 200
    assert any("course" in warning for warning in response.json()["input_warnings"])
    assert "/reference/vocabularies" in " ".join(response.json()["input_warnings"])
    attrition = client.post("/predict-attrition", json={**ATTRITION_PAYLOAD, "industry": "Deep Sea Mining"})
    assert attrition.status_code == 200
    assert any("industry" in warning for warning in attrition.json()["input_warnings"])


@pytest.mark.skipif(all(_model_status().get(name) for name in ["placement_model", "attrition_model"]), reason="Models match the current feature contract.")
def test_stale_models_are_refused_with_a_retrain_instruction():
    response = client.post("/predict-placement", json=PLACEMENT_PAYLOAD)
    assert response.status_code == 503
    assert "src.modeling.train" in response.json()["detail"] or "training" in response.json()["detail"]
