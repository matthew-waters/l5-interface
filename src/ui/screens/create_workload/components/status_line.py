"""Auto-clearing status line widget."""

from __future__ import annotations

from textual.timer import Timer
from textual.widgets import Static


class AutoClearStatus(Static):
    """A one-line status area that clears itself after a short delay."""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._clear_timer: Timer | None = None

    def set_status(self, text: str, *, auto_clear_seconds: float | None = 3.0) -> None:
        self.update(text)

        if self._clear_timer is not None:
            try:
                self._clear_timer.stop()
            except Exception:
                pass
            self._clear_timer = None

        if not text or auto_clear_seconds is None:
            return

        self._clear_timer = self.set_timer(auto_clear_seconds, self.clear_status)

    def clear_status(self) -> None:
        self.update("")

