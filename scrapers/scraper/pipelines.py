from __future__ import annotations

import logging
from datetime import datetime

from itemadapter import ItemAdapter

from dpaas_core.extraction import ExtractionService
from dpaas_core.storage import DuckDBStore

from .settings import DUCKDB_PATH


logger = logging.getLogger(__name__)


class TimestampPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        scraped_at = datetime.utcnow().isoformat()
        adapter["timestamp"] = scraped_at
        adapter["scraped_at"] = scraped_at
        return item


class DuckDBPipeline:
    def __init__(self, database_path: str) -> None:
        self.database_path = database_path
        self.store = None
        self.run_id = None
        self.extractor = None

    @classmethod
    def from_crawler(cls, crawler):
        database_path = crawler.settings.get("DUCKDB_PATH") or DUCKDB_PATH
        logger.info("DUCKDB_PATH=%s", database_path)
        return cls(database_path=database_path)

    def open_spider(self, spider):
        self.store = DuckDBStore(self.database_path)
        self.run_id = self.store.start_run(spider.name)
        self.extractor = ExtractionService.from_env(storage=self.store)

    def close_spider(self, spider):
        if self.store and self.run_id:
            self.store.finish_run(self.run_id)
            self.store.close()

    def process_item(self, item, spider):
        raw = ItemAdapter(item).asdict()
        ok, observation_id = self.store.write_raw_item(raw, run_id=self.run_id, extractor=self.extractor)
        if ok:
            logger.debug("stored observation_id=%s spider=%s", observation_id, spider.name)
        else:
            logger.debug("stored rejection spider=%s item=%s", spider.name, raw)
        return item
