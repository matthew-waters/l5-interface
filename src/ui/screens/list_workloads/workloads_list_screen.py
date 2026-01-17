"""Workloads list screen."""

from __future__ import annotations

from datetime import datetime, timezone

from textual import events
from textual.app import ComposeResult
from textual.screen import Screen
from textual.widgets import DataTable, Static

from src.models.workload import Workload, WorkloadStatus
from src.ui.widgets.global_widgets.global_header import GlobalHeader
from src.ui.widgets.global_widgets.navigation_bar import NavigationBar


class WorkloadsListScreen(Screen[None]):
    """Unified list for drafts/scheduled/executing/completed workloads."""
    HEADER_TITLE = "Workloads"

    BINDINGS = [
        ("a", "sort_status", "Sort status"),
        ("s", "sort_start", "Sort start"),
        ("r", "sort_runtime", "Sort runtime"),
        ("c", "sort_carbon", "Sort carbon"),
        ("n", "new_draft", "New draft"),
        ("g", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        yield GlobalHeader()
        yield Static("Workloads", classes="section_title")
        yield Static("Keys: [n] new draft  [g] refresh  [a/s/r/c] sort", classes="muted")
        table = DataTable(id="workloads_table", zebra_stripes=True)
        table.add_columns(
            "ID",
            "NAME",
            "STATUS",
            "NEXT_ACTION",
            "RUNTIME",
            "CARBON",
            "FLEET",
            "REGION",
        )
        yield table
        yield NavigationBar(id="global_nav")

    def on_mount(self) -> None:
        self._sort_mode = "start"
        self.refresh_table()

    def refresh_table(self) -> None:
        table = self.query_one("#workloads_table", DataTable)
        table.clear(columns=False)

        workloads = list(getattr(self.app, "storage").workloads.list())
        workloads = self._sorted(workloads)

        for w in workloads:
            table.add_row(
                w.workload_id[:8],
                w.name,
                w.status.value,
                self._next_action_text(w),
                self._runtime_text(w),
                self._carbon_text(w),
                w.fleet or "-",
                w.region or "-",
                key=w.workload_id,
            )

    def _sorted(self, workloads: list[Workload]) -> list[Workload]:
        now = datetime.now(tz=timezone.utc)

        if self._sort_mode == "status":
            order = {
                WorkloadStatus.DRAFT: 0,
                WorkloadStatus.SCHEDULED: 1,
                WorkloadStatus.RUNNING: 2,
                WorkloadStatus.DONE: 3,
                WorkloadStatus.CANCELLED: 4,
            }
            return sorted(workloads, key=lambda w: (order.get(w.status, 99), w.name.lower()))

        if self._sort_mode == "runtime":
            return sorted(
                workloads,
                key=lambda w: (w.expected_runtime_seconds is None, w.expected_runtime_seconds or 0),
            )

        if self._sort_mode == "carbon":
            return sorted(
                workloads,
                key=lambda w: (w.expected_carbon_intensity is None, w.expected_carbon_intensity or 0.0),
            )

        # default: start time (scheduled first; drafts without time at bottom)
        def start_key(w: Workload) -> tuple[int, datetime]:
            if w.scheduled_start is None:
                return (1, now)
            return (0, w.scheduled_start)

        return sorted(workloads, key=start_key)

    @staticmethod
    def _next_action_text(w: Workload) -> str:
        now = datetime.now(tz=timezone.utc)
        if w.status == WorkloadStatus.DRAFT:
            return "Draft"
        if w.status == WorkloadStatus.SCHEDULED and w.scheduled_start is not None:
            delta = w.scheduled_start - now
            secs = int(delta.total_seconds())
            if secs >= 0:
                mins = secs // 60
                return f"Starts in {mins}m"
            return "Should have started"
        if w.status == WorkloadStatus.RUNNING:
            return "Running"
        if w.status == WorkloadStatus.DONE:
            return "Done"
        if w.status == WorkloadStatus.CANCELLED:
            return "Cancelled"
        return "-"

    @staticmethod
    def _runtime_text(w: Workload) -> str:
        if w.expected_runtime_seconds is None:
            return "-"
        return f"{w.expected_runtime_seconds // 60}m"

    @staticmethod
    def _carbon_text(w: Workload) -> str:
        if w.expected_carbon_intensity is None:
            return "-"
        return f"{w.expected_carbon_intensity:.0f} gCO₂/kWh"

    def action_refresh(self) -> None:
        self.refresh_table()

    def action_sort_status(self) -> None:
        self._sort_mode = "status"
        self.refresh_table()

    def action_sort_start(self) -> None:
        self._sort_mode = "start"
        self.refresh_table()

    def action_sort_runtime(self) -> None:
        self._sort_mode = "runtime"
        self.refresh_table()

    def action_sort_carbon(self) -> None:
        self._sort_mode = "carbon"
        self.refresh_table()

    def action_new_draft(self) -> None:
        getattr(self.app, "storage").workloads.create_draft("New workload")
        self.refresh_table()

    def on_screen_resume(self, event: events.ScreenResume) -> None:
        # Ensure nav highlight is correct immediately when this screen becomes active.
        try:
            self.query_one(NavigationBar).update_active_page()
        except Exception:
            pass
