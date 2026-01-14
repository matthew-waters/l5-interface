"""Workload display widgets."""

from __future__ import annotations

from datetime import datetime, timezone

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Static

from src.models.workload import WorkloadStatus


class UpcomingWorkloads(Static):
    """Shows the next 3–5 scheduled workloads (placeholder)."""

    def compose(self) -> ComposeResult:
        yield Static("Upcoming workloads", classes="section_title")
        self._items = Vertical()
        yield self._items

    def on_mount(self) -> None:
        self.refresh_workloads()

    def refresh_workloads(self) -> None:
        self._items.remove_children()
        workloads = list(getattr(self.app, "storage").workloads.list())
        now = datetime.now(tz=timezone.utc)

        upcoming = [
            w
            for w in workloads
            if w.status in (WorkloadStatus.SCHEDULED, WorkloadStatus.RUNNING)
        ]

        # Sort: running first, then next scheduled start
        def key(w):
            running = 0 if w.status == WorkloadStatus.RUNNING else 1
            start = w.scheduled_start or now
            return (running, start)

        upcoming = sorted(upcoming, key=key)[:5]

        if not upcoming:
            self._items.mount(Static("No scheduled workloads.", classes="muted"))
            return

        for w in upcoming:
            start_txt = "-"
            if w.scheduled_start is not None:
                secs = int((w.scheduled_start - now).total_seconds())
                start_txt = f"starts in {max(secs, 0)//60}m"
            carbon_txt = (
                f"{w.expected_carbon_intensity:.0f} gCO₂/kWh"
                if w.expected_carbon_intensity is not None
                else "-"
            )
            self._items.mount(
                Static(f"• {w.name} | {w.status.value} | {start_txt} | {carbon_txt}", classes="muted")
            )

