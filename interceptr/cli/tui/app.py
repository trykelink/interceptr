# app.py — Textual TUI application for Interceptr interactive dashboard
from __future__ import annotations

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Footer, Header, Static
from textual.containers import Horizontal, Vertical

from interceptr.client import InterceptrClient
from interceptr.cli.config import get_detection_mode, get_llm_provider
from interceptr.cli.tui.logs import LogsWidget
from interceptr.cli.tui.policy import PolicyWidget

CSS = """
Screen {
    background: #1a1a1a;
}

Header {
    background: #1a1a1a;
    color: #a8e63d;
}

Footer {
    background: #111111;
    color: #888888;
}

#status-bar {
    height: 3;
    background: #222222;
    border: solid #a8e63d;
    padding: 0 2;
    color: #a8e63d;
    content-align: left middle;
}

#main-area {
    height: 1fr;
}

#logs-pane {
    width: 60%;
    border: solid #333333;
    padding: 0 1;
}

#policy-pane {
    width: 40%;
    border: solid #333333;
    padding: 0 1;
}
"""


class InterceptrTUI(App):
    TITLE = "Interceptr"
    SUB_TITLE = "AI Agent Security Middleware"
    CSS = CSS
    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("r", "reload_policy", "Reload Policy"),
        Binding("l", "focus_logs", "Logs"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._client = InterceptrClient()
        mode = get_detection_mode()
        provider = get_llm_provider()
        if mode == "llm" and provider:
            self._detection_label = f"Detection: {provider.capitalize()} + regex"
        else:
            self._detection_label = "Detection: regex"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static(self._status_text(), id="status-bar")
        with Horizontal(id="main-area"):
            with Vertical(id="logs-pane"):
                yield LogsWidget()
            with Vertical(id="policy-pane"):
                yield PolicyWidget()
        yield Footer()

    def _status_text(self) -> str:
        try:
            data = self._client.health()
            return f"● Running  |  status: {data.get('status', 'ok')}  |  {self._detection_label}"
        except Exception:
            return f"⚠ Connection lost — server unreachable  |  {self._detection_label}"

    def on_mount(self) -> None:
        self.set_interval(3, self._refresh_status)

    def _refresh_status(self) -> None:
        bar = self.query_one("#status-bar", Static)
        bar.update(self._status_text())

    def action_reload_policy(self) -> None:
        try:
            self._client.reload_policy()
            policy_widget = self.query_one(PolicyWidget)
            policy_widget.refresh_data()
        except Exception:
            pass

    def action_focus_logs(self) -> None:
        self.query_one(LogsWidget).focus()
