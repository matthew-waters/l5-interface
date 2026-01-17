"""Global system timeline screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static, Footer
from textual.binding import Binding

from src.ui.widgets.global_widgets.global_header import GlobalHeader


class TimelineScreen(Screen[None]):
    """Full system timeline view (placeholder)."""
    HEADER_TITLE = "Timeline"

    BINDINGS = []

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        yield Footer(show_command_palette=False)