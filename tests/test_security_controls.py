# test_security_controls.py — Security-focused integration tests for headers, limits, and input hardening.
import pytest
from httpx import AsyncClient


async def _exercise_limit(
    client: AsyncClient,
    method: str,
    path: str,
    limit: int,
    json_payload: dict | None = None,
) -> tuple[list[int], int]:
    statuses: list[int] = []
    for _ in range(limit):
        response = await client.request(method, path, json=json_payload)
        statuses.append(response.status_code)
    over_limit_response = await client.request(method, path, json=json_payload)
    return statuses, over_limit_response.status_code


@pytest.mark.anyio
async def test_analyze_rate_limit_enforced(client: AsyncClient) -> None:
    statuses, over_limit_status = await _exercise_limit(
        client,
        "POST",
        "/api/v1/analyze/",
        10,
        {"input": "check this payload"},
    )
    assert all(status == 200 for status in statuses)
    assert over_limit_status == 429


@pytest.mark.anyio
async def test_intercept_rate_limit_enforced(client: AsyncClient) -> None:
    statuses, over_limit_status = await _exercise_limit(
        client,
        "POST",
        "/api/v1/intercept/",
        60,
        {"agent": "security-test-agent", "tool": "read_customer", "arguments": {}},
    )
    assert all(status == 200 for status in statuses)
    assert over_limit_status == 429


@pytest.mark.anyio
async def test_policy_reload_rate_limit_enforced(client: AsyncClient) -> None:
    statuses, over_limit_status = await _exercise_limit(
        client,
        "POST",
        "/api/v1/policy/reload",
        5,
    )
    assert all(status in {200, 422} for status in statuses)
    assert over_limit_status == 429


@pytest.mark.anyio
async def test_audit_logs_rate_limit_enforced(client: AsyncClient) -> None:
    statuses, over_limit_status = await _exercise_limit(
        client,
        "GET",
        "/api/v1/audit-logs/",
        30,
    )
    assert all(status == 200 for status in statuses)
    assert over_limit_status == 429


@pytest.mark.anyio
async def test_rate_limit_headers_present(client: AsyncClient) -> None:
    response = await client.post("/api/v1/analyze/", json={"input": "normal input"})
    assert response.status_code == 200
    assert response.headers.get("X-RateLimit-Limit") is not None
    assert response.headers.get("X-RateLimit-Remaining") is not None


@pytest.mark.anyio
async def test_security_headers_present_on_success_and_error(client: AsyncClient) -> None:
    success_response = await client.get("/health")
    assert success_response.status_code == 200

    error_response = await client.post("/api/v1/analyze/", json={"agent": "missing-input"})
    assert error_response.status_code == 422

    for response in (success_response, error_response):
        assert response.headers["X-Content-Type-Options"] == "nosniff"
        assert response.headers["X-Frame-Options"] == "DENY"
        assert response.headers["X-XSS-Protection"] == "1; mode=block"
        assert response.headers["Strict-Transport-Security"] == "max-age=31536000; includeSubDomains"
        assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
        assert response.headers["Content-Security-Policy"] == "default-src 'none'"
        assert response.headers["Cache-Control"] == "no-store"
        assert response.headers["Permissions-Policy"] == "geolocation=(), microphone=(), camera=()"


@pytest.mark.anyio
async def test_oversized_analyze_payload_rejected(client: AsyncClient) -> None:
    response = await client.post("/api/v1/analyze/", json={"input": "A" * 10_001})
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid request payload"


@pytest.mark.anyio
async def test_oversized_intercept_metadata_rejected(client: AsyncClient) -> None:
    payload = {
        "agent": "security-test-agent",
        "tool": "read_customer",
        "arguments": {},
        "metadata": {"blob": "A" * 4_100},
    }
    response = await client.post("/api/v1/intercept/", json=payload)
    assert response.status_code == 422


@pytest.mark.anyio
async def test_audit_logs_are_append_only_endpoints(client: AsyncClient) -> None:
    delete_response = await client.delete("/api/v1/audit-logs/")
    put_response = await client.put("/api/v1/audit-logs/", json={})
    assert delete_response.status_code == 405
    assert put_response.status_code == 405
