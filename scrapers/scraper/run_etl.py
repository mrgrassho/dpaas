from __future__ import annotations

import argparse
import json
import os
from typing import Iterable, List

from dpaas_core.source_catalog import implemented_active_spiders
from dpaas_core.storage import DuckDBStore


DEFAULT_EXCLUDED_SPIDERS = {"meli"}


def _parse_spiders(value: str, available: Iterable[str]) -> List[str]:
    available = sorted(available)
    if value == "all":
        active = implemented_active_spiders(available)
        return [name for name in active if name not in DEFAULT_EXCLUDED_SPIDERS]
    requested = [name.strip() for name in value.split(",") if name.strip()]
    unknown = sorted(set(requested) - set(available))
    if unknown:
        raise SystemExit(f"Unknown spider(s): {', '.join(unknown)}")
    return requested


def run_sample(database: str, sample_csv: str) -> None:
    store = DuckDBStore(database)
    try:
        result = store.seed_from_csv(sample_csv)
        print(json.dumps(result, sort_keys=True))
    finally:
        store.close()


def run_spiders(database: str, spider_arg: str) -> None:
    os.environ.setdefault("SCRAPY_SETTINGS_MODULE", "scraper.settings")

    from scrapy.crawler import CrawlerProcess
    from scrapy.utils.project import get_project_settings

    settings = get_project_settings()
    settings.set("DUCKDB_PATH", database, priority="cmdline")
    process = CrawlerProcess(settings)
    spider_names = _parse_spiders(spider_arg, process.spider_loader.list())
    for spider_name in spider_names:
        process.crawl(spider_name)
    process.start()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run DPAAS local ETL into DuckDB.")
    parser.add_argument("--spider", default="all", help="Spider name, comma list, or all. all excludes Mercado Libre by default.")
    parser.add_argument("--database", default=os.environ.get("DUCKDB_PATH", "data/dpaas.duckdb"))
    parser.add_argument("--sample", dest="sample_csv", default=None, help="Load a local CSV sample instead of crawling live sites.")
    args = parser.parse_args()

    if args.sample_csv:
        run_sample(args.database, args.sample_csv)
    else:
        run_spiders(args.database, args.spider)


if __name__ == "__main__":
    main()
