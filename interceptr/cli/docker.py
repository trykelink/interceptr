# docker.py — Docker lifecycle management for Interceptr
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import httpx
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

INTERCEPTR_DIR = Path.home() / ".interceptr"
COMPOSE_URL = "https://raw.githubusercontent.com/trykelink/interceptr/main/docker-compose.yml"
COMPOSE_FILE = INTERCEPTR_DIR / "docker-compose.yml"

console = Console()


def is_docker_running() -> bool:
    """Return True if Docker daemon is reachable."""
    result = subprocess.run(
        ["docker", "info"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0


def ensure_docker_running() -> bool:
    """Ensure Docker is running. On Linux, attempt to start it via sudo systemctl.

    Returns True if Docker is running (or was successfully started), False otherwise.
    Prints friendly messages before attempting sudo on Linux.
    """
    if is_docker_running():
        return True

    if sys.platform != "linux":
        return False

    # Check systemctl is available (systemd-based Linux)
    systemctl_check = subprocess.run(
        ["which", "systemctl"], capture_output=True, text=True
    )
    if systemctl_check.returncode != 0:
        return False

    console.print(
        "[yellow]⚠  Docker daemon is not running.[/yellow]\n"
        "   Interceptr needs to start it. This requires your system password.\n"
        "   Your password is used only to start Docker — nothing is stored.\n\n"
        "   Starting Docker..."
    )

    result = subprocess.run(["sudo", "systemctl", "start", "docker"])
    if result.returncode != 0:
        return False

    # Wait up to 10s for Docker to become ready
    for _ in range(10):
        time.sleep(1)
        if is_docker_running():
            console.print("[green]✅ Docker started.[/green]")
            return True

    return False


def is_first_run_docker() -> bool:
    """Return True if the interceptr image has never been pulled/built locally."""
    result = subprocess.run(
        ["docker", "images", "-q", "interceptr-interceptr"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() == ""


def download_compose() -> None:
    """Download docker-compose.yml from GitHub to ~/.interceptr/."""
    INTERCEPTR_DIR.mkdir(parents=True, exist_ok=True)
    console.print("[cyan]⬇  Downloading Interceptr configuration...[/cyan]")
    try:
        response = httpx.get(COMPOSE_URL, follow_redirects=True, timeout=30)
        response.raise_for_status()
        COMPOSE_FILE.write_text(response.text)
    except Exception as exc:
        raise RuntimeError(f"Failed to download configuration: {exc}") from exc


def is_compose_present() -> bool:
    """Return True if docker-compose.yml exists in ~/.interceptr/."""
    return COMPOSE_FILE.exists()


def start_containers() -> None:
    """Run docker compose up -d --pull always against the cached compose file."""
    console.print("[cyan]🐳 Starting Interceptr containers...[/cyan]")
    result = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "up", "-d"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to start containers:\n{result.stderr or result.stdout}"
        )


def stop_containers() -> None:
    """Run docker compose down against the cached compose file."""
    console.print("[cyan]⏹  Stopping Interceptr...[/cyan]")
    result = subprocess.run(
        ["docker", "compose", "-f", str(COMPOSE_FILE), "down"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"Failed to stop containers:\n{result.stderr or result.stdout}"
        )


def copy_policy_if_exists() -> None:
    """Copy policy.yaml into the running container if one exists locally."""
    policy_paths = [
        Path.cwd() / "policy.yaml",
        INTERCEPTR_DIR / "policy.yaml",
    ]

    for policy_path in policy_paths:
        if policy_path.is_file():
            result = subprocess.run(
                ["docker", "cp", str(policy_path), "interceptr-interceptr-1:/app/policy.yaml"],
                capture_output=True,
            )
            if result.returncode == 0:
                try:
                    httpx.post("http://localhost:8000/api/v1/policy/reload", timeout=5)
                except Exception:
                    pass
            return


def wait_for_server(
    timeout: int = 60,
    message: str = "⏳ Waiting for server to be ready...",
) -> bool:
    """Poll /health every 2 seconds until 200 or timeout. Returns True if ready."""
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[cyan]{message}[/cyan]"),
        transient=True,
    ) as progress:
        progress.add_task("wait", total=None)
        elapsed = 0
        while elapsed < timeout:
            try:
                response = httpx.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    return True
            except Exception:
                pass
            time.sleep(2)
            elapsed += 2
    return False
