"""Execution overview screen."""

from __future__ import annotations

from textual import events
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from src.ui.widgets.global_widgets.global_header import GlobalHeader
from src.ui.widgets.global_widgets.navigation_bar import NavigationBar


class ExecutionOverviewScreen(Screen[None]):
    """Execution overview for a selected workload (placeholder)."""
    HEADER_TITLE = "Execution"

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        yield Static("Execution overview (placeholder)", classes="section_title")
        yield Static("This screen will show logs, interruptions, and plan details.", classes="muted")
        yield NavigationBar(id="global_nav")
