"""App-wide Textual messages/events."""

from __future__ import annotations

from textual.message import Message


class CredentialsChanged(Message):
    """Posted when credentials/config values are updated by the user."""

