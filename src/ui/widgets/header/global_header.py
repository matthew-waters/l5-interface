"""Global header widget displayed on all screens."""

from __future__ import annotations

from datetime import datetime, timezone

from textual import work
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.reactive import reactive
from textual.widgets import LoadingIndicator, Static

from src.backend.data.freshness.tracker import get_freshness_tracker


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
    }

    GlobalHeader .freshness_spinner {
        width: 3;
        margin-left: 1;
    }

    GlobalHeader .hidden {
        visibility: hidden;
    }
    
    GlobalHeader .freshness.stale {
        color: $warning;
    }

    GlobalHeader .freshness.ok {
        color: $success;
    }
    """

    current_time: reactive[str] = reactive("")
    refreshing_freshness: reactive[bool] = reactive(False)

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the global header."""
        super().__init__(*args, **kwargs)
        self._freshness_tracker = get_freshness_tracker()
        self._last_screen_title: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the header layout."""
        with Horizontal(classes="global-header"):
            yield Static("Loading…", id="screen_title", classes="app-name")
            with Horizontal(classes="right-section"):
                yield Static("00:00:00", id="time_display", classes="time")
                yield Static("NESO: N/A | WT: N/A | Fleet: N/A", id="freshness_display", classes="freshness")
                yield LoadingIndicator(
                    id="freshness_spinner",
                    classes="freshness_spinner hidden",
                )

    def on_mount(self) -> None:
        """Set up periodic updates when widget is mounted."""
        self.update_time()
        self.update_screen_title()

        self.set_timer(0.1, self._initial_refresh)

        # Keep the header title in sync with navigation.
        self.set_interval(0.25, self.update_screen_title)
        self.set_interval(1.0, self.update_time)
        self.set_interval(5.0, self.update_freshness)  # Update freshness display every 5 seconds
        self.set_interval(60.0, self._refresh_freshness_from_api)  # Check API every 60 seconds

    def update_screen_title(self) -> None:
        """Update the left-hand title to reflect the current screen."""
        try:
            screen = getattr(self.app, "screen", None)
            if screen is None:
                title = "Scheduling System"
            else:
                title = (
                    getattr(screen, "HEADER_TITLE", None)
                    or getattr(screen, "title", None)
                    or screen.__class__.__name__
                )
                title = str(title)

            if title != self._last_screen_title:
                self._last_screen_title = title
                self.query_one("#screen_title", Static).update(title)
        except Exception:
            # Best-effort; never crash header due to navigation/title issues.
            return

    def _initial_refresh(self) -> None:
        """Run the first freshness refresh after the UI has mounted."""
        self._refresh_freshness_from_api()
        self.update_freshness()

    def update_time(self) -> None:
        """Update the displayed time."""
        now = datetime.now(tz=timezone.utc)
        time_str = now.strftime("%H:%M:%S")
        time_widget = self.query_one("#time_display", Static)
        time_widget.update(time_str)

    def _refresh_freshness_from_api(self) -> None:
        """Refresh availability freshness from API (called periodically)."""
        # Kick off a background refresh so the UI remains responsive.
        if self.refreshing_freshness:
            return
        self._set_refreshing(True)
        self._refresh_freshness_worker()

    def _set_refreshing(self, refreshing: bool) -> None:
        self.refreshing_freshness = refreshing
        try:
            spinner = self.query_one("#freshness_spinner", LoadingIndicator)
        except Exception:
            # If the widget isn't fully composed/mounted yet (or mounting was interrupted),
            # avoid crashing the whole app; the next refresh will reconcile state.
            return
        if refreshing:
            spinner.remove_class("hidden")
        else:
            spinner.add_class("hidden")

    @work(thread=True, exclusive=True)
    def _refresh_freshness_worker(self) -> None:
        """Run the API refresh in a worker thread (so spinner can animate)."""
        try:
            # Carbon sources (NESO / WattTime) + Fleet. Each is best-effort.
            self._freshness_tracker.refresh_neso_freshness_from_api()
            self._freshness_tracker.refresh_wt_freshness_from_api()
            self._freshness_tracker.refresh_availability_freshness_from_api()
        finally:
            # Ensure UI updates happen on the main thread.
            call_from_thread = getattr(self, "call_from_thread", None)
            if callable(call_from_thread):
                call_from_thread(self._refresh_freshness_done)
            else:
                self.app.call_from_thread(self._refresh_freshness_done)

    def _refresh_freshness_done(self) -> None:
        self._set_refreshing(False)
        self.update_freshness()

    def update_freshness(self) -> None:
        """Update the data freshness indicators."""
        try:
            neso_freshness = self._freshness_tracker.get_neso_freshness()
            wt_freshness = self._freshness_tracker.get_wt_freshness()
            availability_freshness = self._freshness_tracker.get_availability_freshness()

            neso_age = neso_freshness.format_age()
            wt_age = wt_freshness.format_age()
            availability_age = availability_freshness.format_age()

            # Format: "NESO: 5m ago | WT: 10m ago | Fleet: 2h ago"
            freshness_text = (
                f"NESO: {neso_age} | WT: {wt_age} | Fleet: {availability_age}"
            )

            freshness_widget = self.query_one("#freshness_display", Static)
            freshness_widget.update(freshness_text)

            # Update styling based on staleness
            all_ok = not (
                neso_freshness.is_stale or wt_freshness.is_stale or availability_freshness.is_stale
            )
            if all_ok:
                freshness_widget.remove_class("stale")
                freshness_widget.add_class("ok")
            else:
                freshness_widget.remove_class("ok")
                freshness_widget.add_class("stale")
        except Exception:
            # Fallback if there's an error
            freshness_widget = self.query_one("#freshness_display", Static)
            freshness_widget.update("NESO: N/A | WT: N/A | Fleet: N/A")
            freshness_widget.remove_class("ok")
            freshness_widget.remove_class("stale")