# main.py — Typer CLI application defining all Interceptr commands
from __future__ import annotations

import subprocess
import time
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from interceptr import __version__
from interceptr.client import InterceptrClient, InterceptrNotRunningError

app = typer.Typer(
    name="interceptr",
    help="AI Agent Security Middleware — inspect, control, and audit every agent action.",
    add_completion=False,
    invoke_without_command=True,
)

console = Console()
client = InterceptrClient()


def _error_panel(message: str) -> None:
    console.print(Panel(f"[red]{message}[/red]", title="[red]Error[/red]", border_style="red"))


def _not_running_panel() -> None:
    console.print(
        Panel(
            "[yellow]The Interceptr server is not running.[/yellow]\n\n"
            "Start it with:\n"
            "  [bold]docker compose up -d[/bold]\n"
            "  or: [bold]uvicorn main:app --reload --port 8000[/bold]",
            title="[red]Server Offline[/red]",
            border_style="red",
        )
    )


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """Show help when called with no subcommand."""
    if ctx.invoked_subcommand is None:
        _show_help()


@app.command("help")
def help_command() -> None:
    """Show all available commands."""
    _show_help()


def _show_help() -> None:
    table = Table(show_header=False, box=box.SIMPLE, padding=(0, 2))
    table.add_column("Command", style="bold cyan", width=12)
    table.add_column("Description")

    table.add_row("start", "Start Interceptr (downloads, starts server, opens dashboard)")
    table.add_row("stop", "Stop the Interceptr server")
    table.add_row("status", "Check if the server is running")
    table.add_row("logs", "Show recent audit logs")
    table.add_row("policy", "Manage your policy config")
    table.add_row("analyze", "Analyze text for prompt injection")
    table.add_row("uninstall", "Remove Interceptr completely")

    panel = Panel(
        table,
        title=f"[bold green]Interceptr v{__version__}[/bold green] — AI Agent Security",
        subtitle="[dim]Built by Kelink (kelink.dev)[/dim]",
        border_style="green",
    )
    console.print(panel)


@app.command("start")
def start() -> None:
    """Start Interceptr and open the interactive dashboard."""
    from interceptr.cli.docker import (
        is_docker_running,
        is_compose_present,
        download_compose,
        start_containers,
        wait_for_server,
    )

    # 1. Check Docker is installed and running
    if not is_docker_running():
        console.print(
            Panel(
                "[red]Docker is not running.[/red]\n\n"
                "Please start Docker Desktop and try again.\n"
                "Download Docker: https://docs.docker.com/get-docker/",
                title="[red]Docker Required[/red]",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    # 2. Download docker-compose.yml if not present
    if not is_compose_present():
        try:
            download_compose()
        except RuntimeError as exc:
            _error_panel(str(exc))
            raise typer.Exit(1)

    # 3. Start containers
    try:
        start_containers()
    except RuntimeError as exc:
        _error_panel(str(exc))
        raise typer.Exit(1)

    # 4. Wait for server to be healthy
    ready = wait_for_server(timeout=60)
    if not ready:
        console.print(
            Panel(
                "[red]Server did not start in time.[/red]\n\n"
                "Check logs with:\n"
                "  [bold]docker compose logs[/bold]",
                title="[red]Startup Timeout[/red]",
                border_style="red",
            )
        )
        raise typer.Exit(1)

    # 5. Open TUI
    from interceptr.cli.tui.app import InterceptrTUI
    InterceptrTUI().run()


@app.command("stop")
def stop() -> None:
    """Stop the Interceptr server and containers."""
    from interceptr.cli.docker import stop_containers, is_compose_present

    if not is_compose_present():
        console.print("[yellow]No Interceptr configuration found — nothing to stop.[/yellow]")
        raise typer.Exit()

    try:
        stop_containers()
        console.print(Panel("[green]✅ Interceptr stopped.[/green]", border_style="green"))
    except RuntimeError as exc:
        _error_panel(str(exc))
        raise typer.Exit(1)


@app.command("status")
def status() -> None:
    """Check if the Interceptr server is running."""
    try:
        data = client.health()
        console.print(
            Panel(
                f"[bold green]● Running[/bold green]\n\n"
                f"Status:  {data.get('status', 'ok')}\n"
                f"Version: {data.get('version', 'unknown')}",
                title="[green]Server Status[/green]",
                border_style="green",
            )
        )
    except InterceptrNotRunningError:
        console.print(
            Panel(
                "[bold red]○ Not running[/bold red]\n\n"
                "Start the server:\n"
                "  [bold]docker compose up -d[/bold]\n"
                "  or: [bold]uvicorn main:app --reload --port 8000[/bold]",
                title="[red]Server Status[/red]",
                border_style="red",
            )
        )
        raise typer.Exit(1)


@app.command("logs")
def logs(
    limit: int = typer.Option(20, "--limit", "-n", help="Number of logs to show"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Poll every 2 seconds"),
) -> None:
    """Show recent audit logs."""
    try:
        _print_logs(limit)
        if follow:
            console.print("[dim]Polling every 2 seconds — Ctrl+C to stop[/dim]")
            while True:
                time.sleep(2)
                console.clear()
                _print_logs(limit)
    except InterceptrNotRunningError:
        _not_running_panel()
        raise typer.Exit(1)
    except KeyboardInterrupt:
        pass


def _print_logs(limit: int) -> None:
    entries = client.get_logs(limit=limit)
    table = Table(
        "Timestamp", "Agent", "Tool", "Status", "Reason",
        box=box.ROUNDED,
        show_lines=False,
    )
    for log in entries:
        status_val = log.get("status", "")
        status_styled = (
            f"[green]{status_val}[/green]"
            if status_val == "ALLOWED"
            else f"[red]{status_val}[/red]"
        )
        ts = log.get("timestamp", "")
        if ts and "T" in ts:
            ts = ts.replace("T", " ").split(".")[0]
        table.add_row(
            ts,
            log.get("agent", ""),
            log.get("tool", ""),
            status_styled,
            log.get("reason") or "",
        )
    console.print(table)


policy_app = typer.Typer(help="Manage your policy configuration.")
app.add_typer(policy_app, name="policy")


@policy_app.callback(invoke_without_command=True)
def policy_default(ctx: typer.Context) -> None:
    if ctx.invoked_subcommand is None:
        policy_show()


@policy_app.command("show")
def policy_show() -> None:
    """Display the current policy."""
    try:
        data = client.get_policy()
        loaded = data.get("loaded", False)
        if not loaded:
            console.print(
                Panel(
                    "[yellow]No policy configured — all tool calls are ALLOWED[/yellow]",
                    title="Policy",
                    border_style="yellow",
                )
            )
            return

        agent = data.get("agent", "*")
        allow = data.get("allow", [])
        deny = data.get("deny", [])
        default = data.get("default", "allow")

        allow_str = "\n".join(f"  [green]✓[/green] {t}" for t in allow) or "  [dim](none)[/dim]"
        deny_str = "\n".join(f"  [red]✗[/red] {t}" for t in deny) or "  [dim](none)[/dim]"

        content = (
            f"[bold]Agent:[/bold]   {agent}\n\n"
            f"[bold]Allow:[/bold]\n{allow_str}\n\n"
            f"[bold]Deny:[/bold]\n{deny_str}\n\n"
            f"[bold]Default:[/bold] {default}"
        )
        console.print(Panel(content, title="[bold]Current Policy[/bold]", border_style="cyan"))
    except InterceptrNotRunningError:
        _not_running_panel()
        raise typer.Exit(1)


@policy_app.command("reload")
def policy_reload() -> None:
    """Reload policy from disk."""
    try:
        data = client.reload_policy()
        console.print(
            Panel(
                f"[green]Policy reloaded successfully.[/green]\n{data.get('message', '')}",
                title="Policy Reload",
                border_style="green",
            )
        )
    except InterceptrNotRunningError:
        _not_running_panel()
        raise typer.Exit(1)


@app.command("analyze")
def analyze(
    text: str = typer.Argument(..., help="Text to analyze for prompt injection"),
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Agent name"),
) -> None:
    """Analyze text for prompt injection patterns."""
    try:
        data = client.analyze(input_text=text, agent=agent)
        recommendation = data.get("recommendation", "allow")
        severity = data.get("severity", "none")
        patterns = data.get("patterns_matched", [])

        if recommendation == "allow":
            color = "green"
            icon = "✓"
            label = "Clean"
        elif severity == "low":
            color = "yellow"
            icon = "!"
            label = "Low severity"
        else:
            color = "red"
            icon = "✗"
            label = "Injection detected"

        patterns_str = ""
        if patterns:
            patterns_str = "\n\n[bold]Patterns matched:[/bold]\n" + "\n".join(
                f"  [{color}]•[/{color}] {p}" for p in patterns
            )

        content = (
            f"[{color}][bold]{icon} {label}[/bold][/{color}]\n\n"
            f"Severity:       {severity}\n"
            f"Recommendation: {recommendation}"
            f"{patterns_str}"
        )
        console.print(Panel(content, title="[bold]Injection Analysis[/bold]", border_style=color))
    except InterceptrNotRunningError:
        _not_running_panel()
        raise typer.Exit(1)


@app.command("uninstall")
def uninstall() -> None:
    """Remove Interceptr from your system."""
    confirmed = typer.confirm(
        "This will remove Interceptr from your system. Continue?",
        default=False,
    )
    if not confirmed:
        console.print("[dim]Uninstall cancelled.[/dim]")
        raise typer.Exit()

    console.print("Uninstalling Interceptr...")
    result = subprocess.run(["pipx", "uninstall", "interceptr"], capture_output=True, text=True)
    if result.returncode == 0:
        console.print(Panel("[green]Interceptr has been uninstalled. Goodbye![/green]", border_style="green"))
    else:
        _error_panel(f"Uninstall failed:\n{result.stderr or result.stdout}")
        raise typer.Exit(1)
