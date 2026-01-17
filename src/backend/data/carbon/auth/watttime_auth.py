"""WattTime auth helpers (placeholder).

Implementation will depend on the WattTime auth flow you use (client id/secret, username/password, etc.).
"""

from __future__ import annotations

import requests

from src.storage.config_store import CredentialsConfig


def get_watttime_token(credentials: CredentialsConfig) -> str:
    """Return a WattTime bearer token.

    Uses WattTime username/password Basic Auth against `https://api.watttime.org/login`.
    """

    username = (credentials.watttime_username or "").strip()
    password = credentials.watttime_password or ""

    if not username or not password:
        raise ValueError("Missing WattTime username/password in credentials.")

    login_url = "https://api.watttime.org/login"
    resp = requests.get(login_url, auth=(username, password), timeout=30)
    resp.raise_for_status()

    data = resp.json()
    token = data.get("token")
    if not token:
        raise ValueError("WattTime login response missing token.")
    return str(token)

