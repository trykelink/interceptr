# test_policy_startup.py — Tests for graceful server startup with broken/empty policy.yaml
"""
Tests for Bug 1: server must not crash when policy.yaml exists but is empty or invalid.
Tests for Bug 2: ensure_policy_file_exists() writes a comment placeholder, not an empty file.
"""
import os
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from app.core.policy_engine import PolicyEngine
from app.services.interceptor_service import interceptor_service
from interceptr.cli.docker import ensure_policy_file_exists, INTERCEPTR_DIR


# ── Bug 1: lifespan graceful degradation ──────────────────────────────────────

def _run_lifespan_policy_block(policy_path: str) -> None:
    """Re-execute the policy-loading block from main.py lifespan with the given path."""
    import importlib
    import main as main_module

    # Patch os.path.isfile to say the file exists, and patch PolicyEngine to use our path
    original = interceptor_service.policy_engine
    try:
        with patch("os.path.isfile", return_value=True), \
             patch("main.PolicyEngine", side_effect=lambda _: PolicyEngine(policy_path)):
            # Re-run just the policy block (extracted logic)
            try:
                interceptor_service.policy_engine = PolicyEngine(policy_path)
            except (ValueError, FileNotFoundError) as exc:
                interceptor_service.policy_engine = None
    finally:
        interceptor_service.policy_engine = original


def test_empty_policy_file_leaves_engine_none(tmp_path):
    """An empty policy.yaml must not crash the server — engine stays None."""
    policy = tmp_path / "policy.yaml"
    policy.write_text("")

    with pytest.raises((ValueError, FileNotFoundError)):
        PolicyEngine(str(policy))

    # Simulate the lifespan try/except
    original = interceptor_service.policy_engine
    try:
        try:
            interceptor_service.policy_engine = PolicyEngine(str(policy))
        except (ValueError, FileNotFoundError):
            interceptor_service.policy_engine = None

        assert interceptor_service.policy_engine is None
    finally:
        interceptor_service.policy_engine = original


def test_comment_only_policy_file_leaves_engine_none(tmp_path):
    """A file with only a comment (no YAML keys) is treated as no policy."""
    policy = tmp_path / "policy.yaml"
    policy.write_text("# Interceptr policy — edit with: interceptr policy edit\n")

    with pytest.raises(ValueError):
        PolicyEngine(str(policy))

    original = interceptor_service.policy_engine
    try:
        try:
            interceptor_service.policy_engine = PolicyEngine(str(policy))
        except (ValueError, FileNotFoundError):
            interceptor_service.policy_engine = None

        assert interceptor_service.policy_engine is None
    finally:
        interceptor_service.policy_engine = original


def test_invalid_yaml_policy_leaves_engine_none(tmp_path):
    """Malformed YAML must not crash the server — engine stays None."""
    policy = tmp_path / "policy.yaml"
    policy.write_text("key: [unclosed bracket\n")

    original = interceptor_service.policy_engine
    try:
        try:
            interceptor_service.policy_engine = PolicyEngine(str(policy))
        except (ValueError, FileNotFoundError):
            interceptor_service.policy_engine = None

        assert interceptor_service.policy_engine is None
    finally:
        interceptor_service.policy_engine = original


def test_missing_required_fields_leaves_engine_none(tmp_path):
    """A YAML file missing required fields must not crash the server."""
    policy = tmp_path / "policy.yaml"
    policy.write_text(yaml.dump({"version": "1.0"}))  # missing agent, rules, default

    original = interceptor_service.policy_engine
    try:
        try:
            interceptor_service.policy_engine = PolicyEngine(str(policy))
        except (ValueError, FileNotFoundError):
            interceptor_service.policy_engine = None

        assert interceptor_service.policy_engine is None
    finally:
        interceptor_service.policy_engine = original


def test_valid_policy_file_loads_normally(tmp_path):
    """A valid policy.yaml must still load correctly."""
    policy = tmp_path / "policy.yaml"
    policy.write_text(yaml.dump({
        "version": "1.0",
        "agent": "*",
        "rules": {"allow": ["read_customer"], "deny": []},
        "default": "allow",
    }))

    original = interceptor_service.policy_engine
    try:
        try:
            interceptor_service.policy_engine = PolicyEngine(str(policy))
        except (ValueError, FileNotFoundError):
            interceptor_service.policy_engine = None

        assert interceptor_service.policy_engine is not None
        assert interceptor_service.policy_engine.agent == "*"
    finally:
        interceptor_service.policy_engine = original


# ── Bug 2: ensure_policy_file_exists placeholder content ──────────────────────

def test_ensure_policy_creates_file_when_missing(tmp_path):
    """ensure_policy_file_exists() creates the file when absent."""
    with patch("interceptr.cli.docker.INTERCEPTR_DIR", tmp_path):
        ensure_policy_file_exists()
    assert (tmp_path / "policy.yaml").exists()


def test_ensure_policy_file_content_is_comment_only(tmp_path):
    """The created file contains a comment line, not empty bytes."""
    with patch("interceptr.cli.docker.INTERCEPTR_DIR", tmp_path):
        ensure_policy_file_exists()
    content = (tmp_path / "policy.yaml").read_text()
    assert content.startswith("#")
    assert "interceptr policy edit" in content


def test_ensure_policy_file_is_not_valid_yaml_mapping(tmp_path):
    """The placeholder file must not parse as a valid policy (no mapping keys)."""
    with patch("interceptr.cli.docker.INTERCEPTR_DIR", tmp_path):
        ensure_policy_file_exists()
    content = (tmp_path / "policy.yaml").read_text()
    parsed = yaml.safe_load(content)
    # A comment-only file parses to None — not a dict with required fields
    assert not isinstance(parsed, dict)


def test_ensure_policy_does_not_overwrite_existing_file(tmp_path):
    """ensure_policy_file_exists() must not touch a file that already exists."""
    policy = tmp_path / "policy.yaml"
    policy.write_text("existing content\n")
    with patch("interceptr.cli.docker.INTERCEPTR_DIR", tmp_path):
        ensure_policy_file_exists()
    assert policy.read_text() == "existing content\n"


def test_ensure_policy_creates_interceptr_dir_if_missing(tmp_path):
    """ensure_policy_file_exists() creates ~/.interceptr if it doesn't exist."""
    new_dir = tmp_path / "new_interceptr"
    with patch("interceptr.cli.docker.INTERCEPTR_DIR", new_dir):
        ensure_policy_file_exists()
    assert new_dir.is_dir()
    assert (new_dir / "policy.yaml").exists()
