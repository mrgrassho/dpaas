from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

from .cost_model import build_cost_scenarios, parse_usage_schedule
from .storage import DuckDBStore


def price_series(store: DuckDBStore, filters: Optional[Mapping[str, Any]] = None):
    return store.price_series(filters)


def brand_size_summary(store: DuckDBStore, filters: Optional[Mapping[str, Any]] = None):
    return store.brand_size_summary(filters)


def cost_scenarios(store: DuckDBStore, filters: Optional[Mapping[str, Any]] = None, months: int = 36, usage_schedule: Optional[str] = None):
    latest = store.query_observations(filters=filters, latest=True, page=1, page_limit=100000)
    return build_cost_scenarios(latest, months=months, schedule=parse_usage_schedule(usage_schedule))


def data_quality(store: DuckDBStore) -> Dict[str, Any]:
    return store.data_quality()
