"""Global system timeline screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from src.ui.widgets.header.global_header import GlobalHeader


class TimelineScreen(Screen[None]):
    """Full system timeline view (placeholder)."""

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        yield Static("Timeline (placeholder)", classes="section_title")
        yield Static("This screen will show a larger planning horizon.", classes="muted")

