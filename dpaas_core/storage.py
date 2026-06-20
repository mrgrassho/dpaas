from __future__ import annotations

import csv
import io
import json
import os
import uuid
from datetime import datetime
from hashlib import sha256
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

import duckdb

from .extraction import ExtractionService, MissingDataError, NotDiaperError
from .percentiles import PercentileMatcher


DEFAULT_DUCKDB_PATH = "data/dpaas.duckdb"


def utcnow() -> datetime:
    return datetime.utcnow()


def parse_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    if not value:
        return utcnow()
    text = str(value).replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(text)
    except ValueError:
        return utcnow()


def product_id_for(item: Mapping[str, Any]) -> str:
    key = {
        "website": item.get("website"),
        "url": item.get("url"),
        "brand": item.get("brand"),
        "size": item.get("size"),
        "units": item.get("units"),
        "description": item.get("description"),
    }
    payload = json.dumps(key, sort_keys=True, ensure_ascii=False, default=str).lower()
    return sha256(payload.encode("utf-8")).hexdigest()[:32]


class DuckDBStore:
    def __init__(self, path: Optional[str] = None) -> None:
        self.path = path or os.environ.get("DUCKDB_PATH") or DEFAULT_DUCKDB_PATH
        parent = Path(self.path).expanduser().resolve().parent
        parent.mkdir(parents=True, exist_ok=True)
        self.connection = duckdb.connect(self.path)
        self.percentiles = PercentileMatcher()
        self.initialize()

    def close(self) -> None:
        self.connection.close()

    def initialize(self) -> None:
        statements = [
            """
            CREATE TABLE IF NOT EXISTS pipeline_runs (
                run_id VARCHAR PRIMARY KEY,
                spider VARCHAR,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                status VARCHAR,
                item_count INTEGER DEFAULT 0,
                rejected_count INTEGER DEFAULT 0
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS products (
                product_id VARCHAR PRIMARY KEY,
                description VARCHAR,
                brand VARCHAR,
                size VARCHAR,
                units INTEGER,
                target_kg_min DOUBLE,
                target_kg_max DOUBLE,
                url VARCHAR,
                image VARCHAR,
                website VARCHAR,
                first_seen TIMESTAMP,
                last_seen TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS price_observations (
                observation_id VARCHAR PRIMARY KEY,
                product_id VARCHAR,
                run_id VARCHAR,
                scraped_at TIMESTAMP,
                price DOUBLE,
                unit_price DOUBLE,
                currency VARCHAR,
                extraction_method VARCHAR,
                raw_payload VARCHAR
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS percentile_matches (
                observation_id VARCHAR,
                sex VARCHAR,
                percentile VARCHAR,
                month INTEGER,
                weight_kg DOUBLE
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS extraction_cache (
                cache_key VARCHAR PRIMARY KEY,
                provider VARCHAR,
                model VARCHAR,
                prompt_hash VARCHAR,
                response_json VARCHAR,
                created_at TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS rejected_observations (
                rejection_id VARCHAR PRIMARY KEY,
                run_id VARCHAR,
                scraped_at TIMESTAMP,
                website VARCHAR,
                description VARCHAR,
                raw_payload VARCHAR,
                reasons VARCHAR
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS external_indices (
                index_name VARCHAR,
                period VARCHAR,
                value DOUBLE,
                source VARCHAR,
                loaded_at TIMESTAMP
            )
            """,
        ]
        for statement in statements:
            self.connection.execute(statement)
        self.connection.commit()

    def start_run(self, spider: str) -> str:
        run_id = str(uuid.uuid4())
        self.connection.execute(
            "INSERT INTO pipeline_runs (run_id, spider, started_at, status, item_count, rejected_count) VALUES (?, ?, ?, ?, 0, 0)",
            [run_id, spider, utcnow(), "running"],
        )
        self.connection.commit()
        return run_id

    def finish_run(self, run_id: str, status: str = "completed") -> None:
        counts = self.connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM price_observations WHERE run_id = ?) AS item_count,
                (SELECT COUNT(*) FROM rejected_observations WHERE run_id = ?) AS rejected_count
            """,
            [run_id, run_id],
        ).fetchone()
        self.connection.execute(
            "UPDATE pipeline_runs SET completed_at = ?, status = ?, item_count = ?, rejected_count = ? WHERE run_id = ?",
            [utcnow(), status, counts[0], counts[1], run_id],
        )
        self.connection.commit()

    def get_extraction_cache(self, cache_key: str) -> Optional[str]:
        row = self.connection.execute("SELECT response_json FROM extraction_cache WHERE cache_key = ?", [cache_key]).fetchone()
        return row[0] if row else None

    def set_extraction_cache(self, cache_key: str, provider: str, model: str, response_json: str, prompt_hash: str = "") -> None:
        existing = self.connection.execute("SELECT cache_key FROM extraction_cache WHERE cache_key = ?", [cache_key]).fetchone()
        if existing:
            return
        self.connection.execute(
            """
            INSERT INTO extraction_cache (cache_key, provider, model, prompt_hash, response_json, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            [cache_key, provider, model, prompt_hash, response_json, utcnow()],
        )
        self.connection.commit()

    def write_raw_item(
        self,
        raw_item: Mapping[str, Any],
        run_id: str,
        extractor: Optional[ExtractionService] = None,
    ) -> Tuple[bool, Optional[str]]:
        service = extractor or ExtractionService.from_env(storage=self)
        try:
            enriched = service.enrich(raw_item)
        except NotDiaperError as exc:
            self.insert_rejection(raw_item, run_id=run_id, reasons=["not_diaper", str(exc)])
            return False, None
        except MissingDataError as exc:
            self.insert_rejection(raw_item, run_id=run_id, reasons=["missing_data"] + exc.missing_fields)
            return False, None
        except Exception as exc:
            self.insert_rejection(raw_item, run_id=run_id, reasons=["extraction_error", str(exc)])
            return False, None

        observation_id = self.insert_observation(enriched, raw_payload=raw_item, run_id=run_id)
        return True, observation_id

    def insert_rejection(self, raw_item: Mapping[str, Any], run_id: str, reasons: Sequence[str]) -> str:
        rejection_id = str(uuid.uuid4())
        self.connection.execute(
            """
            INSERT INTO rejected_observations (rejection_id, run_id, scraped_at, website, description, raw_payload, reasons)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            [
                rejection_id,
                run_id,
                parse_datetime(raw_item.get("scraped_at") or raw_item.get("timestamp")),
                raw_item.get("website"),
                raw_item.get("description"),
                json.dumps(dict(raw_item), ensure_ascii=False, default=str),
                json.dumps(list(reasons), ensure_ascii=False),
            ],
        )
        self.connection.commit()
        return rejection_id

    def upsert_product(self, item: Mapping[str, Any], scraped_at: datetime) -> str:
        product_id = product_id_for(item)
        existing = self.connection.execute("SELECT product_id FROM products WHERE product_id = ?", [product_id]).fetchone()
        values = [
            item.get("description"),
            item.get("brand"),
            item.get("size"),
            item.get("units"),
            item.get("target_kg_min"),
            item.get("target_kg_max"),
            item.get("url"),
            item.get("image"),
            item.get("website"),
            scraped_at,
            product_id,
        ]
        if existing:
            self.connection.execute(
                """
                UPDATE products
                SET description = ?, brand = ?, size = ?, units = ?, target_kg_min = ?, target_kg_max = ?,
                    url = ?, image = ?, website = ?, last_seen = ?
                WHERE product_id = ?
                """,
                values,
            )
        else:
            self.connection.execute(
                """
                INSERT INTO products (
                    product_id, description, brand, size, units, target_kg_min, target_kg_max,
                    url, image, website, first_seen, last_seen
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    product_id,
                    item.get("description"),
                    item.get("brand"),
                    item.get("size"),
                    item.get("units"),
                    item.get("target_kg_min"),
                    item.get("target_kg_max"),
                    item.get("url"),
                    item.get("image"),
                    item.get("website"),
                    scraped_at,
                    scraped_at,
                ],
            )
        return product_id

    def insert_observation(self, item: Mapping[str, Any], raw_payload: Mapping[str, Any], run_id: str) -> str:
        scraped_at = parse_datetime(item.get("scraped_at"))
        product_id = self.upsert_product(item, scraped_at)
        observation_id = str(uuid.uuid4())
        self.connection.execute(
            """
            INSERT INTO price_observations (
                observation_id, product_id, run_id, scraped_at, price, unit_price, currency, extraction_method, raw_payload
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                observation_id,
                product_id,
                run_id,
                scraped_at,
                item.get("price"),
                item.get("unit_price"),
                item.get("currency") or "ARS",
                item.get("extraction_method") or "rules",
                json.dumps(dict(raw_payload), ensure_ascii=False, default=str),
            ],
        )
        for match in self.percentiles.match(item.get("target_kg_min"), item.get("target_kg_max")):
            self.connection.execute(
                """
                INSERT INTO percentile_matches (observation_id, sex, percentile, month, weight_kg)
                VALUES (?, ?, ?, ?, ?)
                """,
                [observation_id, match.sex, match.percentile, match.month, match.weight_kg],
            )
        self.connection.commit()
        return observation_id

    def seed_from_csv(self, csv_path: str, spider: str = "sample_csv") -> Dict[str, int]:
        run_id = self.start_run(spider)
        count = 0
        rejected = 0
        with open(csv_path, "r", newline="") as fp:
            for row in csv.DictReader(fp):
                raw = {
                    "description": row.get("description") or f"{row.get('brand')} {row.get('size')} x{row.get('units')}",
                    "price": row.get("price"),
                    "website": row.get("website"),
                    "brand": row.get("brand"),
                    "size": row.get("size"),
                    "units": row.get("units"),
                    "target_kg_min": row.get("target_kg_min"),
                    "target_kg_max": row.get("target_kg_max"),
                    "unit_price": row.get("unit_price"),
                    "scraped_at": utcnow().isoformat(),
                }
                ok, _ = self.write_raw_item(raw, run_id=run_id)
                count += int(ok)
                rejected += int(not ok)
        self.finish_run(run_id)
        return {"run_id": run_id, "inserted": count, "rejected": rejected}

    def _where_clause(self, filters: Mapping[str, Any], latest: bool) -> Tuple[str, List[Any]]:
        clauses = []
        params: List[Any] = []
        if latest:
            clauses.append("rn = 1")
        for column, lte_key, gte_key in (
            ("price", "price_lte", "price_gte"),
            ("unit_price", "unit_price_lte", "unit_price_gte"),
        ):
            if filters.get(lte_key) is not None:
                clauses.append(f"{column} <= ?")
                params.append(filters[lte_key])
            if filters.get(gte_key) is not None:
                clauses.append(f"{column} >= ?")
                params.append(filters[gte_key])
        for column, key in (("brand", "brands"), ("size", "sizes"), ("website", "websites")):
            values = filters.get(key)
            if isinstance(values, str):
                values = [value.strip() for value in values.split(",") if value.strip()]
            if values:
                placeholders = ",".join(["?"] * len(values))
                clauses.append(f"{column} IN ({placeholders})")
                params.extend(values)
        if filters.get("target_kg") is not None:
            clauses.append("target_kg_min <= ? AND (target_kg_max IS NULL OR target_kg_max >= ?)")
            params.extend([filters["target_kg"], filters["target_kg"]])
        where = "WHERE " + " AND ".join(clauses) if clauses else ""
        return where, params

    def query_observations(self, filters: Optional[Mapping[str, Any]] = None, latest: bool = True, page: int = 1, page_limit: int = 20) -> List[Dict[str, Any]]:
        filters = filters or {}
        where, params = self._where_clause(filters, latest)
        offset = max(page - 1, 0) * page_limit
        query = f"""
            WITH joined AS (
                SELECT
                    o.observation_id, o.product_id, p.description, o.price, p.url, p.image, p.website,
                    p.brand, p.size, p.target_kg_min, p.target_kg_max, p.units, o.unit_price,
                    o.currency, o.scraped_at, o.extraction_method,
                    row_number() OVER (PARTITION BY o.product_id ORDER BY o.scraped_at DESC, o.observation_id DESC) AS rn
                FROM price_observations o
                JOIN products p ON p.product_id = o.product_id
            )
            SELECT observation_id, product_id, description, price, url, image, website, brand, size,
                   target_kg_min, target_kg_max, units, unit_price, currency, scraped_at, extraction_method
            FROM joined
            {where}
            ORDER BY scraped_at DESC, observation_id DESC
            LIMIT ? OFFSET ?
        """
        rows = self.connection.execute(query, params + [page_limit, offset]).fetchall()
        columns = [
            "observation_id",
            "product_id",
            "description",
            "price",
            "url",
            "image",
            "website",
            "brand",
            "size",
            "target_kg_min",
            "target_kg_max",
            "units",
            "unit_price",
            "currency",
            "scraped_at",
            "extraction_method",
        ]
        items = [dict(zip(columns, row)) for row in rows]
        self._attach_percentiles(items)
        return items

    def _attach_percentiles(self, items: List[Dict[str, Any]]) -> None:
        if not items:
            return
        ids = [item["observation_id"] for item in items]
        placeholders = ",".join(["?"] * len(ids))
        rows = self.connection.execute(
            f"""
            SELECT observation_id, sex, percentile, month
            FROM percentile_matches
            WHERE observation_id IN ({placeholders})
            ORDER BY sex, percentile, month
            """,
            ids,
        ).fetchall()
        by_id: Dict[str, Dict[str, Dict[str, List[int]]]] = {
            item["observation_id"]: {"boys": {}, "girls": {}} for item in items
        }
        for observation_id, sex, percentile, month in rows:
            by_id[observation_id].setdefault(sex, {}).setdefault(percentile, []).append(month)
        for item in items:
            maps = by_id[item["observation_id"]]
            item["percentil_boys"] = maps.get("boys", {})
            item["percentil_girls"] = maps.get("girls", {})
            item["target_kg"] = {"min": item.pop("target_kg_min"), "max": item.pop("target_kg_max")}

    def price_series(self, filters: Optional[Mapping[str, Any]] = None) -> List[Dict[str, Any]]:
        filters = filters or {}
        where, params = self._where_clause(filters, latest=False)
        query = f"""
            WITH joined AS (
                SELECT
                    o.observation_id, o.product_id, p.description, o.price, p.website, p.brand, p.size,
                    p.units, p.target_kg_min, p.target_kg_max, o.unit_price, o.currency, o.scraped_at, 1 AS rn
                FROM price_observations o
                JOIN products p ON p.product_id = o.product_id
            )
            SELECT observation_id, product_id, description, price, website, brand, size, units, unit_price, currency, scraped_at
            FROM joined
            {where}
            ORDER BY scraped_at ASC
        """
        columns = ["observation_id", "product_id", "description", "price", "website", "brand", "size", "units", "unit_price", "currency", "scraped_at"]
        return [dict(zip(columns, row)) for row in self.connection.execute(query, params).fetchall()]

    def brand_size_summary(self, filters: Optional[Mapping[str, Any]] = None) -> List[Dict[str, Any]]:
        latest = self.query_observations(filters=filters, latest=True, page=1, page_limit=100000)
        groups: Dict[Tuple[Any, Any], List[Dict[str, Any]]] = {}
        for item in latest:
            groups.setdefault((item.get("brand"), item.get("size")), []).append(item)
        rows = []
        for (brand, size), items in sorted(groups.items(), key=lambda kv: (kv[0][0] or "", kv[0][1] or "")):
            unit_prices = [float(item["unit_price"]) for item in items if item.get("unit_price") is not None]
            prices = [float(item["price"]) for item in items if item.get("price") is not None]
            rows.append(
                {
                    "brand": brand,
                    "size": size,
                    "product_count": len(items),
                    "min_unit_price": round(min(unit_prices), 2) if unit_prices else None,
                    "avg_unit_price": round(sum(unit_prices) / len(unit_prices), 2) if unit_prices else None,
                    "max_unit_price": round(max(unit_prices), 2) if unit_prices else None,
                    "avg_price": round(sum(prices) / len(prices), 2) if prices else None,
                }
            )
        return rows

    def data_quality(self) -> Dict[str, Any]:
        totals = self.connection.execute(
            """
            SELECT
                (SELECT COUNT(*) FROM products),
                (SELECT COUNT(*) FROM price_observations),
                (SELECT COUNT(*) FROM rejected_observations),
                (SELECT COUNT(*) FROM pipeline_runs)
            """
        ).fetchone()
        rejection_rows = self.connection.execute("SELECT reasons FROM rejected_observations").fetchall()
        reason_counts: Dict[str, int] = {}
        for (reason_json,) in rejection_rows:
            try:
                reasons = json.loads(reason_json)
            except Exception:
                reasons = [reason_json]
            for reason in reasons:
                reason_counts[str(reason)] = reason_counts.get(str(reason), 0) + 1
        return {
            "products": totals[0],
            "observations": totals[1],
            "rejected_observations": totals[2],
            "pipeline_runs": totals[3],
            "rejection_reasons": reason_counts,
        }

    def observations_csv(self, filters: Optional[Mapping[str, Any]] = None, latest: bool = False) -> str:
        rows = self.query_observations(filters=filters, latest=latest, page=1, page_limit=1000000)
        output = io.StringIO()
        fieldnames = [
            "observation_id",
            "product_id",
            "scraped_at",
            "website",
            "brand",
            "size",
            "units",
            "price",
            "unit_price",
            "currency",
            "target_kg_min",
            "target_kg_max",
            "description",
            "url",
            "image",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            flat = dict(row)
            target = flat.pop("target_kg", {}) or {}
            flat["target_kg_min"] = target.get("min")
            flat["target_kg_max"] = target.get("max")
            writer.writerow({key: flat.get(key) for key in fieldnames})
        return output.getvalue()
