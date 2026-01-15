"""Global header widget displayed on all screens."""

from __future__ import annotations

from datetime import datetime, timezone

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import Static

from src.backend.data.data_freshness import get_freshness_tracker


class GlobalHeader(Static):
    """Global header with app name, time, and data freshness indicators."""

    DEFAULT_CSS = """
    GlobalHeader {
        dock: top;
        height: 3;
        padding: 0 1;
        background: $surface;
        border-bottom: wide $primary;
    }
    
    GlobalHeader Horizontal {
        height: 100%;
        align: center middle;
    }
    
    GlobalHeader .app-name {
        width: 1fr;
        content-align: left middle;
        text-style: bold;
    }
    
    GlobalHeader .right-section {
        width: 1fr;
        content-align: right middle;
        align: right middle;
    }
    
    GlobalHeader .time {
        margin-right: 2;
        width: auto;
    }
    
    GlobalHeader .freshness {
        margin-left: 1;
        width: auto;
        text-wrap: nowrap;
    }
    
    GlobalHeader .freshness.stale {
        color: $warning;
    }
    """

    current_time: reactive[str] = reactive("")

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the global header."""
        super().__init__(*args, **kwargs)
        self._freshness_tracker = get_freshness_tracker()

    def compose(self) -> ComposeResult:
        """Compose the header layout."""
        with Horizontal():
            yield Static("Scheduling System", classes="app-name")
            with Horizontal(classes="right-section"):
                yield Static("00:00:00", id="time_display", classes="time")
                yield Static("Carbon: Never | Fleet: Never", id="freshness_display", classes="freshness")

    def on_mount(self) -> None:
        """Set up periodic updates when widget is mounted."""
        self.update_time()

        self._freshness_tracker.refresh_availability_freshness_from_api()
        self.update_freshness()
        
        self.set_interval(1.0, self.update_time)
        self.set_interval(5.0, self.update_freshness)  # Update freshness display every 5 seconds
        self.set_interval(30.0, self._refresh_freshness_from_api)  # Check API every 30 seconds

    def update_time(self) -> None:
        """Update the displayed time."""
        now = datetime.now(tz=timezone.utc)
        time_str = now.strftime("%H:%M:%S")
        time_widget = self.query_one("#time_display", Static)
        time_widget.update(time_str)

    def _refresh_freshness_from_api(self) -> None:
        """Refresh availability freshness from API (called periodically)."""
        self._freshness_tracker.refresh_availability_freshness_from_api()

    def update_freshness(self) -> None:
        """Update the data freshness indicators."""
        try:
            carbon_freshness = self._freshness_tracker.get_carbon_freshness()
            availability_freshness = self._freshness_tracker.get_availability_freshness()

            carbon_age = carbon_freshness.format_age()
            availability_age = availability_freshness.format_age()

            # Format: "Carbon: 5m ago | Fleet: 2h ago"
            freshness_text = (
                f"Carbon: {carbon_age} | Fleet: {availability_age}"
            )

            freshness_widget = self.query_one("#freshness_display", Static)
            freshness_widget.update(freshness_text)

            # Update styling based on staleness
            if carbon_freshness.is_stale or availability_freshness.is_stale:
                freshness_widget.add_class("stale")
            else:
                freshness_widget.remove_class("stale")
        except Exception:
            # Fallback if there's an error
            freshness_widget = self.query_one("#freshness_display", Static)
            freshness_widget.update("Carbon: Never | Fleet: Never")
