"""Drafts table widget for CreateWorkloadScreen."""

from __future__ import annotations

from datetime import datetime

from textual.app import ComposeResult
from textual.message import Message
from textual.widget import Widget
from textual.widgets import DataTable

from src.models.workload_config import WorkloadConfig
from src.ui.screens.create_workload.components import ids


class DraftsTable(Widget):
    """A drafts list rendered as a DataTable."""

    class DraftSelected(Message):
        """Posted when a draft is selected (Enter on a row)."""

        def __init__(self, config_id: str) -> None:
            super().__init__()
            self.config_id = config_id

    def compose(self) -> ComposeResult:
        yield DataTable(
            id=ids.DRAFTS_DATA_TABLE_ID,
            cursor_type="row",
            zebra_stripes=True,
            cell_padding=4,
        )

    def focus_table(self) -> None:
        try:
            self.query_one(f"#{ids.DRAFTS_DATA_TABLE_ID}", DataTable).focus()
        except Exception:
            pass

    def selected_config_id(self) -> str | None:
        """Return the config_id for the currently highlighted row (if any)."""
        try:
            table = self.query_one(f"#{ids.DRAFTS_DATA_TABLE_ID}", DataTable)
            row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
            return row_key.value if row_key.value else None
        except Exception:
            return None

    @staticmethod
    def _fmt_dt_local(dt: datetime | None) -> str:
        if dt is None:
            return "-"
        try:
            return dt.astimezone().strftime("%Y-%m-%d %H:%M")
        except Exception:
            return str(dt)

    def set_drafts(self, drafts: list[WorkloadConfig]) -> None:
        table = self.query_one(f"#{ids.DRAFTS_DATA_TABLE_ID}", DataTable)
        table.clear(columns=True)
        table.add_columns(
            "Name",
            "Last updated",
            "Interruptible",
            "Delay tolerance",
            "Fleet",
            "Runtime",
        )

        if not drafts:
            table.add_row("No drafts yet.", "", "", "", "", "")
            return

        for d in drafts:
            name = d.name.strip() or "(unnamed)"
            interruptible = (
                "-" if d.interruptible is None else ("Yes" if d.interruptible else "No")
            )
            delay = d.delay_tolerance.label() if d.delay_tolerance is not None else "-"
            fleet = d.fleet_name or (str(d.fleet_id) if d.fleet_id is not None else "-")
            runtime = (
                f"{int(d.runtime_estimate_seconds // 60)} min"
                if d.runtime_estimate_seconds is not None
                else "-"
            )
            table.add_row(
                name,
                self._fmt_dt_local(d.updated_at),
                interruptible,
                delay,
                fleet,
                runtime,
                key=d.config_id,
            )

    def show_error(self, message: str) -> None:
        table = self.query_one(f"#{ids.DRAFTS_DATA_TABLE_ID}", DataTable)
        table.clear(columns=True)
        table.add_columns("Name", "Last updated", "Interruptible", "Delay tolerance", "Fleet", "Runtime")
        table.add_row(f"Error: {message}", "", "", "", "", "")

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        config_id = event.row_key.value
        if not config_id:
            return
        self.post_message(self.DraftSelected(str(config_id)))

