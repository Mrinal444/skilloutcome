"""Mocked integration coverage for the backend-to-ML service boundary."""
from __future__ import annotations

import asyncio
import json
from types import SimpleNamespace

import httpx
import pytest
from fastapi.testclient import TestClient

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.main import app
from app.models.trainee import SkillLevel, Trainee
from app.services.ml_client import MLServiceClient, MLServiceError, get_ml_client


class _Query:
    def __init__(self, trainee: object | None) -> None:
        self.trainee = trainee

    def options(self, *_: object) -> "_Query":
        return self

    def filter(self, *_: object) -> "_Query":
        return self

    def first(self) -> object | None:
        return self.trainee


class _Database:
    def __init__(self, trainee: object | None) -> None:
        self.trainee = trainee

    def query(self, _: object) -> _Query:
        return _Query(self.trainee)


def _trainee(*, user_id: int = 7, skills: list[object] | None = None) -> object:
    return SimpleNamespace(trainee_id=11, user_id=user_id, skills=skills or [])


def _skill(name: str, level: SkillLevel) -> object:
    return SimpleNamespace(skill=SimpleNamespace(skill_name=name), level=level)


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


@pytest.mark.parametrize(
    ("ml_status", "expected_status", "expected_code"),
    [
        (503, 503, "ML_MODEL_UNAVAILABLE"),
        (422, 422, "ML_INPUT_INVALID"),
        (500, 502, "ML_SERVICE_ERROR"),
    ],
)
def test_ml_client_maps_ml_service_failures(
    ml_status: int, expected_status: int, expected_code: str
) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(ml_status, request=request, json={"detail": "mocked"})

    client = MLServiceClient(base_url="http://ml.test", transport=httpx.MockTransport(handler))
    with pytest.raises(MLServiceError) as raised:
        asyncio.run(client.skill_gap({"target_job_role": "Data Analyst", "current_skills": []}))

    assert raised.value.status_code == expected_status
    assert raised.value.error_code == expected_code


def test_ml_client_maps_network_errors_to_service_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused", request=request)

    client = MLServiceClient(base_url="http://ml.test", transport=httpx.MockTransport(handler))
    with pytest.raises(MLServiceError) as raised:
        asyncio.run(client.health())

    assert raised.value.status_code == 503
    assert raised.value.error_code == "ML_SERVICE_UNAVAILABLE"


def test_skill_gap_route_maps_persisted_skills_and_returns_envelope() -> None:
    observed_payload: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/skill-gap"
        observed_payload.update(json.loads(request.content))
        return httpx.Response(
            200,
            request=request,
            json={
                "target_job_role": "Data Analyst",
                "missing_skills": ["SQL"],
                "matched_skills": ["Python"],
                "below_required_proficiency": [],
                "skill_gap_score": 45.0,
                "skill_coverage_percent": 50.0,
                "recommendations": [],
            },
        )

    trainee = _trainee(skills=[_skill("Python", SkillLevel.INTERMEDIATE), _skill("Excel", SkillLevel.ADVANCED)])
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=7, role=SimpleNamespace(value="TRAINEE"))
    app.dependency_overrides[get_ml_client] = lambda: MLServiceClient(
        base_url="http://ml.test", transport=httpx.MockTransport(handler)
    )
    app.dependency_overrides[get_db] = lambda: _Database(trainee)
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/trainees/11/ml/skill-gap",
            headers={"Authorization": "Bearer mocked"},
            json={"target_job_role": "Data Analyst"},
        )

    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["skill_gap_score"] == 45.0
    assert observed_payload == {
        "target_job_role": "Data Analyst",
        "current_skills": [
            {"name": "Excel", "proficiency": 100.0},
            {"name": "Python", "proficiency": 66.0},
        ],
    }


def test_skill_gap_route_rejects_missing_persisted_features() -> None:
    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=7, role=SimpleNamespace(value="TRAINEE"))
    app.dependency_overrides[get_db] = lambda: _Database(_trainee())
    with TestClient(app) as client:
        response = client.post(
            "/api/v1/trainees/11/ml/skill-gap",
            headers={"Authorization": "Bearer mocked"},
            json={"target_job_role": "Data Analyst"},
        )
    assert response.status_code == 422
    assert response.json() == {
        "success": False,
        "message": "Required ML feature values are incomplete.",
        "data": {"missing_fields": ["skills"]},
        "error_code": "ML_FEATURES_INCOMPLETE",
    }


def test_ml_health_route_uses_backend_envelope_and_mocked_client() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/health"
        return httpx.Response(200, request=request, json={"status": "ok"})

    app.dependency_overrides[get_current_user] = lambda: SimpleNamespace(id=1, role=SimpleNamespace(value="ADMIN"))
    app.dependency_overrides[get_ml_client] = lambda: MLServiceClient(
        base_url="http://ml.test", transport=httpx.MockTransport(handler)
    )
    with TestClient(app) as client:
        response = client.get("/api/v1/ml/health", headers={"Authorization": "Bearer mocked"})

    assert response.status_code == 200
    assert response.json() == {
        "success": True,
        "message": "ML service health retrieved successfully",
        "data": {"status": "ok"},
        "error_code": None,
    }
