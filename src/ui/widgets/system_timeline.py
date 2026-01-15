"""Condensed system timeline widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class SystemTimeline(Static):
    """Condensed contextual timeline (placeholder)."""

    def compose(self) -> ComposeResult:
        yield Static("System timeline (next 24h)", classes="section_title")
        with Vertical():
            yield Static("Now +24h", classes="muted")

