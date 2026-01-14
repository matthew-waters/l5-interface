"""System status header widget."""

from __future__ import annotations

from datetime import datetime, timezone

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Static


class StatusHeader(Static):
    """Application identity + profile + data freshness indicator."""

    DEFAULT_CSS = """
    StatusHeader Horizontal {
      height: auto;
    }
    StatusHeader .right {
      width: 1fr;
      content-align: right middle;
    }
    """

    def compose(self) -> ComposeResult:
        now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
        with Horizontal():
            yield Static("L5 Scheduler Interface", classes="section_title")
            yield Static(f"Profile: default | Data updated: {now}", classes="right muted")


