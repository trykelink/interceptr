# client.py — HTTP client for communicating with the Interceptr API server
from __future__ import annotations

import httpx


class InterceptrNotRunningError(Exception):
    """Raised when the Interceptr server is not reachable."""


class InterceptrClient:
    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url.rstrip("/")

    def _get(self, path: str, **kwargs) -> dict:
        try:
            response = httpx.get(f"{self.base_url}{path}", timeout=5, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise InterceptrNotRunningError(
                "Interceptr server is not running. Start it with: interceptr start"
            )

    def _post(self, path: str, **kwargs) -> dict:
        try:
            response = httpx.post(f"{self.base_url}{path}", timeout=5, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.ConnectError:
            raise InterceptrNotRunningError(
                "Interceptr server is not running. Start it with: interceptr start"
            )

    def health(self) -> dict:
        """GET /health — check server health."""
        return self._get("/health")

    def get_logs(self, limit: int = 50) -> list[dict]:
        """GET /api/v1/audit-logs/ — retrieve recent audit logs."""
        data = self._get("/api/v1/audit-logs/", params={"limit": limit})
        return data.get("logs", [])

    def get_policy(self) -> dict:
        """GET /api/v1/policy/ — get current policy info."""
        return self._get("/api/v1/policy/")

    def reload_policy(self) -> dict:
        """POST /api/v1/policy/reload — reload policy from disk."""
        return self._post("/api/v1/policy/reload")

    def intercept(self, agent: str, tool: str, arguments: dict) -> dict:
        """POST /api/v1/intercept/ — intercept a tool call."""
        return self._post(
            "/api/v1/intercept/",
            json={"agent": agent, "tool": tool, "arguments": arguments},
        )

    def analyze(self, input_text: str, agent: str | None = None) -> dict:
        """POST /api/v1/analyze/ — analyze input text for prompt injection."""
        payload: dict = {"input": input_text}
        if agent is not None:
            payload["agent"] = agent
        return self._post("/api/v1/analyze/", json=payload)

    def is_running(self) -> bool:
        """Return True if the server is reachable, False otherwise."""
        try:
            self.health()
            return True
        except (InterceptrNotRunningError, Exception):
            return False
