# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from datetime import datetime
import json
import logging
import re
from itemadapter import ItemAdapter
import pymongo
from scrapy.exceptions import DropItem

from scraper.clean_data import DiaperCleaner, MissingDataException, NotDiaperException

from .settings import MONGO_DATABASE, MONGO_URI

from .constants import DIAPER_SIZES, DIAPERS_REGEX


REPLACEMENTS = {
    "pr": [r"prematuro", r"prem"],
    "rn": [r"reci.*n nacido"],
    "huggies": [r"hugies"],
    "g": [r"grande"],
    "m": [r"s\-m"],
}

logger = logging.getLogger(__name__)


class DiaperPipeline:
    def __init__(self) -> None:
        self.cleaner = DiaperCleaner()

    def process_item(self, item, spider):
        try:
            adapter = ItemAdapter(item)
            self.cleaner.enhance(adapter)
            return item
        except NotDiaperException:
            raise DropItem(f"Not a diaper - {item}")
        except MissingDataException as e:
            raise DropItem(f"Missing {e.missing_fields} in {item}")


class TimestampPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        adapter["timestamp"] = datetime.now().isoformat()
        return item


class MongoPipeline:

    collection_name = "scrapy_items"

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        logger.info(f"MONGO_URI={MONGO_URI}, MONGO_DATABAS={MONGO_DATABASE}")
        return cls(mongo_uri=MONGO_URI, mongo_db=MONGO_DATABASE)

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]
        self.db[self.collection_name].delete_many(
            {"website": spider.allowed_domains[0]}
        )

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.collection_name].insert_one(ItemAdapter(item).asdict())
        return item
