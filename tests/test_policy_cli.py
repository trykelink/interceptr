# test_policy_cli.py — Tests for CLI policy_edit and policy_reload commands
from __future__ import annotations

from unittest.mock import MagicMock, patch, call

import httpx
import pytest
from typer.testing import CliRunner

from interceptr.cli.main import app as cli_app

runner = CliRunner()


# ── policy edit ──────────────────────────────────────────────────────────────


def test_policy_edit_calls_copy_after_tui():
    """copy_policy_if_exists() must be called after PolicyEditorApp().run()."""
    call_order: list[str] = []

    mock_tui = MagicMock()
    mock_tui.return_value.run.side_effect = lambda: call_order.append("tui_run")

    def fake_copy():
        call_order.append("copy_policy")

    with patch("interceptr.cli.tui.policy_editor.PolicyEditorApp", mock_tui), \
         patch("interceptr.cli.docker.copy_policy_if_exists", fake_copy):
        result = runner.invoke(cli_app, ["policy", "edit"])

    assert "tui_run" in call_order
    assert "copy_policy" in call_order
    assert call_order.index("tui_run") < call_order.index("copy_policy")


def test_policy_edit_shows_success_message_after_copy():
    """A green success message is printed when copy_policy_if_exists succeeds."""
    with patch("interceptr.cli.tui.policy_editor.PolicyEditorApp") as mock_tui, \
         patch("interceptr.cli.docker.copy_policy_if_exists"):
        mock_tui.return_value.run.return_value = None
        result = runner.invoke(cli_app, ["policy", "edit"])

    assert result.exit_code == 0
    assert "Policy copied into container" in result.output


def test_policy_edit_shows_warning_when_copy_fails():
    """A yellow warning is printed (not a crash) when copy fails."""
    with patch("interceptr.cli.tui.policy_editor.PolicyEditorApp") as mock_tui, \
         patch("interceptr.cli.docker.copy_policy_if_exists", side_effect=RuntimeError("container not found")):
        mock_tui.return_value.run.return_value = None
        result = runner.invoke(cli_app, ["policy", "edit"])

    assert result.exit_code == 0
    assert "could not sync to container" in result.output
    assert "container not found" in result.output


def test_policy_edit_does_not_crash_when_server_unreachable():
    """copy_policy_if_exists failure must not propagate as an unhandled exception."""
    with patch("interceptr.cli.tui.policy_editor.PolicyEditorApp") as mock_tui, \
         patch("interceptr.cli.docker.copy_policy_if_exists", side_effect=Exception("connection refused")):
        mock_tui.return_value.run.return_value = None
        result = runner.invoke(cli_app, ["policy", "edit"])

    assert result.exit_code == 0


# ── policy reload ─────────────────────────────────────────────────────────────


def _make_422_error() -> httpx.HTTPStatusError:
    request = httpx.Request("POST", "http://localhost:8000/api/v1/policy/reload")
    response = httpx.Response(
        status_code=422,
        json={
            "detail": (
                "No policy.yaml found in the container. "
                "Run 'interceptr policy edit' to create one, then try again."
            )
        },
        request=request,
    )
    return httpx.HTTPStatusError("422", request=request, response=response)


def _make_500_error() -> httpx.HTTPStatusError:
    request = httpx.Request("POST", "http://localhost:8000/api/v1/policy/reload")
    response = httpx.Response(
        status_code=500,
        json={"detail": "Internal server error"},
        request=request,
    )
    return httpx.HTTPStatusError("500", request=request, response=response)


def test_policy_reload_shows_friendly_panel_on_422():
    """422 from server → user-friendly 'No Policy Found' panel."""
    with patch("interceptr.client.InterceptrClient.reload_policy", side_effect=_make_422_error()):
        result = runner.invoke(cli_app, ["policy", "reload"])

    assert result.exit_code == 1
    assert "interceptr policy edit" in result.output


def test_policy_reload_422_panel_mentions_no_policy():
    """422 response output includes 'No policy.yaml' or similar wording."""
    with patch("interceptr.client.InterceptrClient.reload_policy", side_effect=_make_422_error()):
        result = runner.invoke(cli_app, ["policy", "reload"])

    assert "No policy" in result.output or "no policy" in result.output.lower()


def test_policy_reload_other_http_errors_show_generic_error():
    """Non-422 HTTP errors show a generic error message."""
    with patch("interceptr.client.InterceptrClient.reload_policy", side_effect=_make_500_error()):
        result = runner.invoke(cli_app, ["policy", "reload"])

    assert result.exit_code == 1
    assert "500" in result.output or "Reload failed" in result.output


def test_policy_reload_success_prints_success_panel():
    """Successful reload shows the green success panel."""
    with patch("interceptr.client.InterceptrClient.reload_policy", return_value={"status": "reloaded", "message": ""}):
        result = runner.invoke(cli_app, ["policy", "reload"])

    assert result.exit_code == 0
    assert "reloaded" in result.output.lower()
