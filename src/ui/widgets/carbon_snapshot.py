"""Carbon impact snapshot widget."""

from __future__ import annotations

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static


class CarbonSnapshot(Static):
    """Emissions so far + avoided estimate (placeholder)."""

    def compose(self) -> ComposeResult:
        yield Static("Carbon impact snapshot", classes="section_title")
        with Vertical():
            yield Static("Today: 1.2 kgCO₂e | This week: 5.8 kgCO₂e", classes="muted")
            yield Static("Avoided vs baseline: ~0.9 kgCO₂e", classes="muted")

