"""Workloads list screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Footer
from textual.binding import Binding

from src.ui.widgets.global_widgets.global_header import GlobalHeader


class WorkloadsListScreen(Screen[None]):
    """Unified list for drafts/scheduled/executing/completed workloads."""
    HEADER_TITLE = "Workloads"

    BINDINGS = []

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        yield Footer(show_command_palette=False)
