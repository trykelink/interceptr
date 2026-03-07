# logs.py — Live audit logs panel widget for the Interceptr TUI
from __future__ import annotations

from textual.widget import Widget
from rich.table import Table
from rich.text import Text
from rich import box
from rich.console import Console
from rich.segment import Segment

from interceptr.client import InterceptrClient


class LogsWidget(Widget):
    """Scrollable live audit logs table, auto-refreshes every 3 seconds."""

    DEFAULT_CSS = """
    LogsWidget {
        height: 1fr;
        overflow-y: auto;
        background: #1a1a1a;
        color: #cccccc;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self._client = InterceptrClient()
        self._logs: list[dict] = []

    def on_mount(self) -> None:
        self._load_logs()
        self.set_interval(3, self._load_logs)

    def _load_logs(self) -> None:
        try:
            self._logs = self._client.get_logs(limit=20)
        except Exception:
            self._logs = []
        self.refresh()

    def render(self) -> Table:
        table = Table(
            "Time", "Agent", "Tool", "Status", "Reason",
            box=box.SIMPLE,
            show_header=True,
            header_style="bold #a8e63d",
            expand=True,
        )
        for log in self._logs:
            status_val = log.get("status", "")
            if status_val == "ALLOWED":
                status_cell = Text(status_val, style="green")
            else:
                status_cell = Text(status_val, style="red")

            ts = log.get("timestamp", "")
            if ts and "T" in ts:
                ts = ts.replace("T", " ").split(".")[0]

            table.add_row(
                ts,
                log.get("agent", ""),
                log.get("tool", ""),
                status_cell,
                log.get("reason") or "",
            )
        return table
