"""Default configurations."""

# Default Spot Fleet API base URL
# Can be overridden via environment variable SPOT_FLEET_API_BASE_URL
DEFAULT_SPOT_FLEET_API_BASE_URL = "https://206zjclkvi.execute-api.eu-west-1.amazonaws.com/v1"

# Spot Fleet API key (optional).
# If set, it will be sent as the `x-api-key` header on all Spot Fleet API requests.
# Can be provided via environment variable SPOT_FLEET_API_KEY.
DEFAULT_SPOT_FLEET_API_KEY: str | None = None