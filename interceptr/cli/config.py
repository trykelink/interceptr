# config.py — Configuration reader for Interceptr CLI
from __future__ import annotations

from pathlib import Path

CONFIG_FILE = Path.home() / ".interceptr" / ".env"


def load_config() -> dict:
    """Read ~/.interceptr/.env and return a dict of all values."""
    if not CONFIG_FILE.exists():
        return {}
    config: dict[str, str] = {}
    for line in CONFIG_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            config[key.strip()] = value.strip()
    return config


def get_detection_mode() -> str:
    """Return 'llm' or 'regex'. Defaults to 'regex' if not set."""
    return load_config().get("INTERCEPTR_DETECTION_MODE", "regex")


def get_llm_provider() -> str | None:
    """Return the configured LLM provider name, or None."""
    return load_config().get("INTERCEPTR_LLM_PROVIDER")


def get_llm_model() -> str | None:
    """Return the configured LLM model name, or None."""
    return load_config().get("INTERCEPTR_LLM_MODEL")
