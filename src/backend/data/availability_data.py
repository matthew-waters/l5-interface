"""Public interface for Spot Fleet availability data."""

from __future__ import annotations

from datetime import datetime

from src.backend.data.fleet.models import InstancePool, InterruptionRate, PlacementScore, RequestGroup, SpotPrice
from src.backend.data.fleet.service import SpotFleetDataService

# Global service instance
_service = SpotFleetDataService()


def get_available_fleets() -> list[RequestGroup]:
    """Get list of all available request groups (fleets).

    Returns:
        List of RequestGroup objects
    """
    return _service.list_available_fleets()


def get_fleet_details(fleet_id: str | int) -> RequestGroup:
    """Get details for a specific fleet.

    Args:
        fleet_id: Request group ID or name

    Returns:
        RequestGroup object
    """
    return _service.get_fleet_details(fleet_id)


def get_fleet_placement_scores(
    fleet_id: str | int,
    *,
    az: str | None = None,
    target_capacity: int | None = None,
) -> list[PlacementScore]:
    """Get latest placement scores for a fleet.

    Args:
        fleet_id: Request group ID or name
        az: Optional availability zone filter
        target_capacity: Optional target capacity filter

    Returns:
        List of PlacementScore objects
    """
    return _service.get_latest_placement_scores(fleet_id, az=az, target_capacity=target_capacity)


def get_fleet_placement_score_history(
    fleet_id: str | int,
    *,
    since: datetime | None = None,
    until: datetime | None = None,
    az: str | None = None,
    target_capacity: int | None = None,
    limit: int = 500,
) -> list[PlacementScore]:
    """Get placement score history for a fleet.

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
    return _service.get_placement_score_history(
        fleet_id,
        since=since,
        until=until,
        az=az,
        target_capacity=target_capacity,
        limit=limit,
    )


def get_pool_interruption_rates(
    pool_id: int,
    *,
    since: datetime | None = None,
    until: datetime | None = None,
    limit: int = 500,
) -> list[InterruptionRate]:
    """Get interruption rate history for a pool.

    Args:
        pool_id: Pool ID
        since: Start time (defaults to 24 hours ago)
        until: End time (defaults to now)
        limit: Maximum number of results

    Returns:
        List of InterruptionRate objects
    """
    return _service.get_pool_interruption_history(pool_id, since=since, until=until, limit=limit)


def get_available_pools(
    *, region: str | None = None, instance_type: str | None = None
) -> list[InstancePool]:
    """Get available instance pools.

    Args:
        region: Optional region filter
        instance_type: Optional instance type filter

    Returns:
        List of InstancePool objects
    """
    return _service.get_available_pools(region=region, instance_type=instance_type)


def get_pool(pool_id: int) -> InstancePool:
    """Get details for a specific instance pool.

    Args:
        pool_id: Pool ID

    Returns:
        InstancePool object
    """
    return _service.get_pool(pool_id)


def get_spot_prices(
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
    return _service.get_spot_prices(
        pool_id=pool_id,
        instance_type=instance_type,
        region=region,
        az=az,
        since=since,
        until=until,
        limit=limit,
    )


def get_latest_spot_price(pool_id: int) -> SpotPrice:
    """Get the latest spot price for a pool.

    Args:
        pool_id: Pool ID

    Returns:
        SpotPrice object
    """
    return _service.get_latest_spot_price(pool_id)