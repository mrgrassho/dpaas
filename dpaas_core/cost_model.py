from __future__ import annotations

from typing import Dict, Iterable, List, Mapping, Optional


DEFAULT_USAGE_SCHEDULE = {
    (0, 1): 10,
    (2, 5): 8,
    (6, 11): 6,
    (12, 24): 5,
    (25, 36): 4,
}


def usage_for_month(month: int, schedule: Optional[Mapping] = None) -> int:
    active = schedule or DEFAULT_USAGE_SCHEDULE
    for key, diapers_per_day in active.items():
        start, end = key
        if start <= month <= end:
            return int(diapers_per_day)
    return 0


def parse_usage_schedule(value: Optional[str]) -> Dict:
    if not value:
        return dict(DEFAULT_USAGE_SCHEDULE)
    parsed = {}
    for part in value.split(","):
        if not part.strip():
            continue
        month_range, daily = part.split(":", 1)
        start, end = month_range.split("-", 1)
        parsed[(int(start), int(end))] = int(daily)
    return parsed


def scenario_for_unit_price(unit_price: float, months: int = 36, schedule: Optional[Mapping] = None, days_per_month: int = 30) -> Dict:
    monthly = []
    total = 0.0
    for month in range(0, months + 1):
        diapers_per_day = usage_for_month(month, schedule)
        cost = round(unit_price * diapers_per_day * days_per_month, 2)
        total += cost
        monthly.append(
            {
                "month": month,
                "diapers_per_day": diapers_per_day,
                "estimated_diapers": diapers_per_day * days_per_month,
                "estimated_cost_ars": cost,
            }
        )
    return {"monthly": monthly, "total_cost_ars": round(total, 2)}


def build_cost_scenarios(observations: Iterable[Mapping], months: int = 36, schedule: Optional[Mapping] = None) -> List[Dict]:
    scenarios = []
    for item in observations:
        unit_price = item.get("unit_price")
        if unit_price is None:
            continue
        scenario = scenario_for_unit_price(float(unit_price), months=months, schedule=schedule)
        scenarios.append(
            {
                "product_id": item.get("product_id"),
                "description": item.get("description"),
                "brand": item.get("brand"),
                "size": item.get("size"),
                "website": item.get("website"),
                "unit_price": unit_price,
                "currency": item.get("currency", "ARS"),
                "months": scenario["monthly"],
                "total_cost_ars": scenario["total_cost_ars"],
                "scraped_at": item.get("scraped_at"),
            }
        )
    return scenarios
