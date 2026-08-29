"""Async client for the separately deployed SkillOutcome ML service."""
from __future__ import annotations

from typing import Any

import httpx

from app.config import settings


class MLServiceError(RuntimeError):
    """A normalized ML-service failure suitable for the public API envelope."""

    def __init__(self, status_code: int, error_code: str, message: str) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.error_code = error_code
        self.message = message


class MLServiceClient:
    """Make bounded, internal HTTP calls to the ML service."""

    def __init__(
        self,
        *,
        base_url: str | None = None,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self._base_url = (base_url or settings.ML_SERVICE_URL).rstrip("/")
        self._transport = transport
        self._timeout = httpx.Timeout(
            connect=settings.ML_CONNECT_TIMEOUT_SECONDS,
            read=settings.ML_READ_TIMEOUT_SECONDS,
            write=settings.ML_WRITE_TIMEOUT_SECONDS,
            pool=settings.ML_POOL_TIMEOUT_SECONDS,
        )

    async def health(self) -> dict[str, Any]:
        return await self._request("GET", "/health")

    async def skill_gap(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/skill-gap", json=payload)

    async def predict_placement(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/predict-placement", json=payload)

    async def predict_attrition(self, payload: dict[str, Any]) -> dict[str, Any]:
        return await self._request("POST", "/predict-attrition", json=payload)

    async def _request(
        self, method: str, path: str, *, json: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        try:
            async with httpx.AsyncClient(
                base_url=self._base_url,
                timeout=self._timeout,
                transport=self._transport,
            ) as client:
                response = await client.request(method, path, json=json)
        except httpx.RequestError as error:
            raise MLServiceError(
                503,
                "ML_SERVICE_UNAVAILABLE",
                "The ML service is unavailable. Please try again shortly.",
            ) from error

        if response.status_code == 503:
            raise MLServiceError(
                503,
                "ML_MODEL_UNAVAILABLE",
                "The ML model is currently unavailable.",
            )
        if response.status_code == 422:
            raise MLServiceError(
                422,
                "ML_INPUT_INVALID",
                "The ML service rejected the supplied input.",
            )
        if response.status_code >= 500:
            raise MLServiceError(
                502,
                "ML_SERVICE_ERROR",
                "The ML service returned an unexpected error.",
            )
        if response.status_code >= 400:
            raise MLServiceError(
                502,
                "ML_SERVICE_ERROR",
                "The ML service returned an unexpected response.",
            )

        try:
            body = response.json()
        except ValueError as error:
            raise MLServiceError(
                502,
                "ML_SERVICE_ERROR",
                "The ML service returned an invalid response.",
            ) from error
        if not isinstance(body, dict):
            raise MLServiceError(
                502,
                "ML_SERVICE_ERROR",
                "The ML service returned an invalid response.",
            )
        return body


def get_ml_client() -> MLServiceClient:
    """FastAPI dependency, replaceable in tests without network access."""
    return MLServiceClient()
