"""High-level service layer for Spot Fleet data."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from src.backend.data.data_freshness import get_freshness_tracker
from src.backend.data.fleet.api_client import SpotFleetAPIClient
from src.backend.data.fleet.models import (
    InstancePool,
    InterruptionRate,
    PlacementScore,
    RequestGroup,
    SpotPrice,
)


class SpotFleetDataService:
    """High-level service for accessing Spot Fleet data with freshness tracking."""

    def __init__(self, api_client: SpotFleetAPIClient | None = None) -> None:
        """Initialize the service.

        Args:
            api_client: Optional API client instance. Creates new one if not provided.
        """
        self._client = api_client or SpotFleetAPIClient()
        self._freshness_tracker = get_freshness_tracker()

    def _update_freshness(self) -> None:
        """Update the availability data freshness timestamp."""
        self._freshness_tracker.update_availability_freshness()

    def list_available_fleets(self) -> list[RequestGroup]:
        """List all available request groups (fleets).

        Returns:
            List of RequestGroup objects
        """
        fleets = self._client.get_request_groups()
        self._update_freshness()
        return fleets

    def get_fleet_details(self, fleet_id: str | int) -> RequestGroup:
        """Get full details for a specific fleet.

        Args:
            fleet_id: Request group ID or name

        Returns:
            RequestGroup object
        """
        fleet = self._client.get_request_group(fleet_id)
        self._update_freshness()
        return fleet

    def get_latest_placement_scores(
        self,
        fleet_id: str | int,
        *,
        az: str | None = None,
        target_capacity: int | None = None,
    ) -> list[PlacementScore]:
        """Get latest placement scores for a fleet (for scheduling decisions).

        Args:
            fleet_id: Request group ID or name
            az: Optional availability zone filter
            target_capacity: Optional target capacity filter

        Returns:
            List of PlacementScore objects (one per unique AZ/capacity pair)
        """
        scores = self._client.get_latest_placement_scores(
            fleet_id, az=az, target_capacity=target_capacity
        )
        self._update_freshness()
        return scores

    def get_placement_score_history(
        self,
        fleet_id: str | int,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        az: str | None = None,
        target_capacity: int | None = None,
        limit: int = 500,
    ) -> list[PlacementScore]:
        """Get placement score history for charts/timelines.

        Args:
            fleet_id: Request group ID or name
            since: Start time (defaults to 24 hours ago)
            until: End time (defaults to now)
            az: Optional availability zone filter
            target_capacity: Optional target capacity filter
            limit: Maximum number of results

        Returns:
            List of PlacementScore objects
        """
        if until is None:
            until = datetime.now(tz=timezone.utc)
        if since is None:
            since = until - timedelta(hours=24)

        scores = self._client.get_placement_scores(
            fleet_id,
            since=since.isoformat(),
            until=until.isoformat(),
            az=az,
            target_capacity=target_capacity,
            limit=limit,
        )
        self._update_freshness()
        return scores

    def get_pool_interruption_history(
        self,
        pool_id: int,
        *,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 500,
    ) -> list[InterruptionRate]:
        """Get interruption rate history for risk analysis.

        Args:
            pool_id: Pool ID
            since: Start time (defaults to 24 hours ago)
            until: End time (defaults to now)
            limit: Maximum number of results

        Returns:
            List of InterruptionRate objects
        """
        if until is None:
            until = datetime.now(tz=timezone.utc)
        if since is None:
            since = until - timedelta(hours=24)

        rates = self._client.get_pool_interruption_rates(
            pool_id,
            since=since.isoformat(),
            until=until.isoformat(),
            limit=limit,
        )
        self._update_freshness()
        return rates

    def get_available_pools(
        self, *, region: str | None = None, instance_type: str | None = None
    ) -> list[InstancePool]:
        """Get available instance pools (for hardware selection).

        Args:
            region: Optional region filter
            instance_type: Optional instance type filter

        Returns:
            List of InstancePool objects
        """
        pools = self._client.get_pools()
        self._update_freshness()

        # Apply filters if provided
        if region:
            pools = [p for p in pools if p.region == region]
        if instance_type:
            pools = [p for p in pools if p.instance_type == instance_type]

        return pools

    def get_pool(self, pool_id: int) -> InstancePool:
        """Get details for a specific instance pool.

        Args:
            pool_id: Pool ID

        Returns:
            InstancePool object
        """
        pool = self._client.get_pool(pool_id)
        self._update_freshness()
        return pool

    def get_spot_prices(
        self,
        *,
        pool_id: int | None = None,
        instance_type: str | None = None,
        region: str | None = None,
        az: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
        limit: int = 500,
    ) -> list[SpotPrice]:
        """Get spot price history.

        Args:
            pool_id: Optional pool ID filter
            instance_type: Optional instance type filter
            region: Optional region filter
            az: Optional availability zone filter
            since: Start time
            until: End time
            limit: Maximum number of results

        Returns:
            List of SpotPrice objects
        """
        params: dict[str, Any] = {"limit": limit}
        if pool_id is not None:
            params["pool_id"] = pool_id
        if instance_type:
            params["instance_type"] = instance_type
        if region:
            params["region"] = region
        if az:
            params["az"] = az
        if since:
            params["since"] = since.isoformat()
        if until:
            params["until"] = until.isoformat()

        prices = self._client.get_spot_prices(**params)
        self._update_freshness()
        return prices

    def get_latest_spot_price(self, pool_id: int) -> SpotPrice:
        """Get the latest spot price for a pool.

        Args:
            pool_id: Pool ID

        Returns:
            SpotPrice object
        """
        price = self._client.get_latest_spot_price(pool_id)
        self._update_freshness()
        return price
