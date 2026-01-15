"""Low-level HTTP client for Spot Fleet API."""

from __future__ import annotations

import json
from typing import Any

import requests

from src.backend.data.fleet.models import (
    InstancePool,
    InterruptionRate,
    PlacementScore,
    RequestGroup,
    SpotPrice,
)
from src.config.settings import get_spot_fleet_api_base_url


class SpotFleetAPIClient:
    """HTTP client for Spot Fleet API."""

    def __init__(self, base_url: str | None = None) -> None:
        """Initialize the API client.

        Args:
            base_url: Base URL for the API. If None, uses value from config.
        """
        self.base_url = (base_url or get_spot_fleet_api_base_url()).rstrip("/")

    def _get(self, endpoint: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Make a GET request to the API.

        Args:
            endpoint: API endpoint path (e.g., "/request-groups")
            params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            requests.RequestException: If the request fails
        """
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_request_groups(self) -> list[RequestGroup]:
        """List all request groups.

        Returns:
            List of RequestGroup objects
        """
        data = self._get("/request-groups")
        return [RequestGroup.from_dict(item) for item in data]

    def get_request_group(self, id_or_name: str | int) -> RequestGroup:
        """Get a single request group by ID or name.

        Args:
            id_or_name: Request group ID (int) or name (str)

        Returns:
            RequestGroup object
        """
        data = self._get(f"/request-groups/{id_or_name}")
        return RequestGroup.from_dict(data)

    def get_placement_scores(
        self,
        request_group_id: str | int,
        *,
        since: str | None = None,
        until: str | None = None,
        az: str | None = None,
        target_capacity: int | None = None,
        order: str = "desc",
        limit: int = 500,
    ) -> list[PlacementScore]:
        """Get placement score history for a request group.

        Args:
            request_group_id: Request group ID or name
            since: ISO8601 timestamp (lower bound)
            until: ISO8601 timestamp (upper bound)
            az: Availability zone filter
            target_capacity: Target capacity filter
            order: Sort order ("asc" or "desc")
            limit: Maximum number of results

        Returns:
            List of PlacementScore objects
        """
        params: dict[str, Any] = {"order": order, "limit": limit}
        if since:
            params["since"] = since
        if until:
            params["until"] = until
        if az:
            params["az"] = az
        if target_capacity is not None:
            params["target_capacity"] = target_capacity

        data = self._get(
            f"/request-groups/{request_group_id}/placement-scores", params=params
        )
        return [PlacementScore.from_dict(item) for item in data]

    def get_latest_placement_scores(
        self,
        request_group_id: str | int,
        *,
        az: str | None = None,
        target_capacity: int | None = None,
    ) -> list[PlacementScore]:
        """Get latest placement scores for a request group.

        Args:
            request_group_id: Request group ID or name
            az: Optional availability zone filter
            target_capacity: Optional target capacity filter

        Returns:
            List of PlacementScore objects (one per unique AZ/capacity pair)
        """
        params: dict[str, Any] = {}
        if az:
            params["az"] = az
        if target_capacity is not None:
            params["target_capacity"] = target_capacity

        data = self._get(
            f"/request-groups/{request_group_id}/placement-scores/latest", params=params
        )
        return [PlacementScore.from_dict(item) for item in data]

    def get_pools(self) -> list[InstancePool]:
        """List all instance pools.

        Returns:
            List of InstancePool objects
        """
        data = self._get("/pools")
        return [InstancePool.from_dict(item) for item in data]

    def get_pool(self, pool_id: int) -> InstancePool:
        """Get a single instance pool by ID.

        Args:
            pool_id: Pool ID

        Returns:
            InstancePool object
        """
        data = self._get(f"/pools/{pool_id}")
        return InstancePool.from_dict(data)

    def get_spot_prices(
        self,
        *,
        pool_id: int | None = None,
        instance_type: str | None = None,
        region: str | None = None,
        az: str | None = None,
        since: str | None = None,
        until: str | None = None,
        order: str = "desc",
        limit: int = 500,
    ) -> list[SpotPrice]:
        """Get spot prices globally (across all pools).

        Args:
            pool_id: Filter by pool ID
            instance_type: Filter by instance type
            region: Filter by region
            az: Filter by availability zone
            since: ISO8601 timestamp (lower bound)
            until: ISO8601 timestamp (upper bound)
            order: Sort order ("asc" or "desc")
            limit: Maximum number of results

        Returns:
            List of SpotPrice objects
        """
        params: dict[str, Any] = {"order": order, "limit": limit}
        if pool_id is not None:
            params["pool_id"] = pool_id
        if instance_type:
            params["instance_type"] = instance_type
        if region:
            params["region"] = region
        if az:
            params["az"] = az
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        data = self._get("/spot-prices", params=params)
        return [SpotPrice.from_dict(item) for item in data]

    def get_pool_spot_prices(
        self,
        pool_id: int,
        *,
        since: str | None = None,
        until: str | None = None,
        order: str = "desc",
        limit: int = 500,
    ) -> list[SpotPrice]:
        """Get spot price history for a specific pool.

        Args:
            pool_id: Pool ID
            since: ISO8601 timestamp (lower bound)
            until: ISO8601 timestamp (upper bound)
            order: Sort order ("asc" or "desc")
            limit: Maximum number of results

        Returns:
            List of SpotPrice objects
        """
        params: dict[str, Any] = {"order": order, "limit": limit}
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        data = self._get(f"/pools/{pool_id}/spot-prices", params=params)
        return [SpotPrice.from_dict(item) for item in data]

    def get_latest_spot_price(self, pool_id: int) -> SpotPrice:
        """Get the latest spot price for a specific pool.

        Args:
            pool_id: Pool ID

        Returns:
            SpotPrice object
        """
        data = self._get(f"/pools/{pool_id}/spot-prices/latest")
        return SpotPrice.from_dict(data)

    def get_interruption_rates(
        self,
        *,
        pool_id: int | None = None,
        instance_type: str | None = None,
        region: str | None = None,
        az: str | None = None,
        since: str | None = None,
        until: str | None = None,
        order: str = "desc",
        limit: int = 500,
    ) -> list[InterruptionRate]:
        """Get interruption rates globally (across all pools).

        Args:
            pool_id: Filter by pool ID
            instance_type: Filter by instance type
            region: Filter by region
            az: Filter by availability zone
            since: ISO8601 timestamp (lower bound)
            until: ISO8601 timestamp (upper bound)
            order: Sort order ("asc" or "desc")
            limit: Maximum number of results

        Returns:
            List of InterruptionRate objects
        """
        params: dict[str, Any] = {"order": order, "limit": limit}
        if pool_id is not None:
            params["pool_id"] = pool_id
        if instance_type:
            params["instance_type"] = instance_type
        if region:
            params["region"] = region
        if az:
            params["az"] = az
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        data = self._get("/interruption-rates", params=params)
        return [InterruptionRate.from_dict(item) for item in data]

    def get_pool_interruption_rates(
        self,
        pool_id: int,
        *,
        since: str | None = None,
        until: str | None = None,
        order: str = "desc",
        limit: int = 500,
    ) -> list[InterruptionRate]:
        """Get interruption rate history for a specific pool.

        Args:
            pool_id: Pool ID
            since: ISO8601 timestamp (lower bound)
            until: ISO8601 timestamp (upper bound)
            order: Sort order ("asc" or "desc")
            limit: Maximum number of results

        Returns:
            List of InterruptionRate objects
        """
        params: dict[str, Any] = {"order": order, "limit": limit}
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        data = self._get(f"/pools/{pool_id}/interruption-rates", params=params)
        return [InterruptionRate.from_dict(item) for item in data]
