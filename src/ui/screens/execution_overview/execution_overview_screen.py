"""Execution overview screen."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import Static

from src.ui.widgets.header.global_header import GlobalHeader


class ExecutionOverviewScreen(Screen[None]):
    """Execution overview for a selected workload (placeholder)."""
    HEADER_TITLE = "Execution"

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        yield Static("Execution overview (placeholder)", classes="section_title")
        yield Static("This screen will show logs, interruptions, and plan details.", classes="muted")

