from __future__ import annotations

import csv
from dataclasses import dataclass
from importlib import resources
from typing import Dict, Iterable, List, Optional


PERCENTILE_COLUMNS = ("P01", "P1", "P3", "P5", "P10", "P15", "P25", "P50", "P75", "P85", "P90", "P95", "P97", "P99", "P999")


@dataclass(frozen=True)
class PercentileMatch:
    sex: str
    percentile: str
    month: int
    weight_kg: float


def _load_csv(package_name: str) -> List[Dict[str, str]]:
    with resources.files("dpaas_core.data").joinpath(package_name).open("r", newline="") as fp:
        return list(csv.DictReader(fp))


class PercentileMatcher:
    def __init__(self) -> None:
        self.rows = {
            "boys": _load_csv("tab_wfa_boys_p_0_5.csv"),
            "girls": _load_csv("tab_wfa_girls_p_0_5.csv"),
        }

    def match(self, target_kg_min: Optional[float], target_kg_max: Optional[float]) -> List[PercentileMatch]:
        if target_kg_min is None:
            return []
        matches: List[PercentileMatch] = []
        for sex, rows in self.rows.items():
            for row in rows:
                month = int(row["Month"])
                for percentile in PERCENTILE_COLUMNS:
                    if not row.get(percentile):
                        continue
                    weight = float(row[percentile])
                    if weight < target_kg_min:
                        continue
                    if target_kg_max is not None and weight > target_kg_max:
                        continue
                    matches.append(PercentileMatch(sex=sex, percentile=percentile, month=month, weight_kg=weight))
        return matches

    def as_month_map(self, target_kg_min: Optional[float], target_kg_max: Optional[float]) -> Dict[str, Dict[str, List[int]]]:
        result: Dict[str, Dict[str, List[int]]] = {"boys": {}, "girls": {}}
        for match in self.match(target_kg_min, target_kg_max):
            result.setdefault(match.sex, {}).setdefault(match.percentile, []).append(match.month)
        return result
