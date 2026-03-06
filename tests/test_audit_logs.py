# test_audit_logs.py — Tests for the audit log API endpoints
import pytest
from httpx import AsyncClient


@pytest.mark.anyio
async def test_create_audit_log_allowed(client: AsyncClient):
    payload = {
        "agent": "test-agent",
        "tool": "read_file",
        "arguments": {"path": "/etc/passwd"},
        "status": "ALLOWED",
    }
    response = await client.post("/api/v1/audit-logs/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["agent"] == "test-agent"
    assert data["tool"] == "read_file"
    assert data["status"] == "ALLOWED"
    assert data["reason"] is None
    assert "id" in data
    assert "timestamp" in data


@pytest.mark.anyio
async def test_create_audit_log_blocked(client: AsyncClient):
    payload = {
        "agent": "test-agent",
        "tool": "delete_file",
        "arguments": {"path": "/important/file"},
        "status": "BLOCKED",
        "reason": "Policy violation: destructive operation",
    }
    response = await client.post("/api/v1/audit-logs/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "BLOCKED"
    assert data["reason"] == "Policy violation: destructive operation"


@pytest.mark.anyio
async def test_get_logs_empty(client: AsyncClient):
    response = await client.get("/api/v1/audit-logs/")
    assert response.status_code == 200
    data = response.json()
    assert data["logs"] == []
    assert data["total"] == 0


@pytest.mark.anyio
async def test_get_logs_returns_created(client: AsyncClient):
    payload = {
        "agent": "agent-x",
        "tool": "write_file",
        "arguments": {"path": "/tmp/test", "content": "hello"},
        "status": "ALLOWED",
    }
    await client.post("/api/v1/audit-logs/", json=payload)
    response = await client.get("/api/v1/audit-logs/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["logs"]) == 1
    assert data["logs"][0]["agent"] == "agent-x"
    assert data["logs"][0]["tool"] == "write_file"
