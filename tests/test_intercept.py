# test_intercept.py — Tests for the tool call interception endpoint
import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_intercept_allowed(client: AsyncClient):
    payload = {
        "agent": "customer-support-agent",
        "tool": "read_customer",
        "arguments": {"id": "123"},
    }
    response = await client.post("/api/v1/intercept/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ALLOWED"
    assert data["reason"] is None


@pytest.mark.anyio
async def test_intercept_creates_audit_log(client: AsyncClient):
    payload = {
        "agent": "finance-agent",
        "tool": "transfer_funds",
        "arguments": {"from": "acc_123", "to": "acc_456", "amount": 1000},
    }
    await client.post("/api/v1/intercept/", json=payload)
    response = await client.get("/api/v1/audit-logs/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    log = data["logs"][0]
    assert log["agent"] == "finance-agent"
    assert log["tool"] == "transfer_funds"
    assert log["arguments"] == {"from": "acc_123", "to": "acc_456", "amount": 1000}
    assert log["status"] == "ALLOWED"


@pytest.mark.anyio
async def test_intercept_returns_log_id(client: AsyncClient):
    payload = {
        "agent": "test-agent",
        "tool": "read_file",
        "arguments": {"path": "/tmp/data"},
    }
    response = await client.post("/api/v1/intercept/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "log_id" in data
    # Verify it's a valid UUID
    uuid.UUID(data["log_id"])


@pytest.mark.anyio
async def test_intercept_with_metadata(client: AsyncClient):
    payload = {
        "agent": "finance-agent",
        "tool": "transfer_funds",
        "arguments": {"from": "acc_123", "to": "acc_456", "amount": 500},
        "metadata": {"environment": "production", "user_id": "user_789"},
    }
    response = await client.post("/api/v1/intercept/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ALLOWED"


@pytest.mark.anyio
async def test_intercept_missing_required_fields(client: AsyncClient):
    payload = {"agent": "test-agent"}  # missing tool and arguments
    response = await client.post("/api/v1/intercept/", json=payload)
    assert response.status_code == 422
