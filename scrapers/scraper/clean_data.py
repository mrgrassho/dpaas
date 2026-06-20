from __future__ import annotations

import argparse
import csv
import json
import logging
import os
import sys
from os import environ
from os.path import dirname, join
from typing import Dict, Union

from dotenv import load_dotenv

from dpaas_core.extraction import MissingDataError, NotDiaperError, RuleBasedExtractor


class CommonDiaperException(Exception):
    pass


class NotDiaperException(CommonDiaperException):
    pass


class MissingDataException(CommonDiaperException):
    def __init__(self, missing_fields):
        self.missing_fields = missing_fields


logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

dotenv_path = join(dirname(__file__), ".env")
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

DIR_DATA = environ.get("DIR_DATA")

CSV_KEYS = [
    "price",
    "website",
    "brand",
    "size",
    "target_kg_min",
    "target_kg_max",
    "units",
    "unit_price",
]


class DiaperCleaner:
    def __init__(self, replacements: Union[Dict, str] = None):
        self.extractor = RuleBasedExtractor()

    def enhance(self, item):
        try:
            enriched = self.extractor.enrich(item)
        except NotDiaperError:
            raise NotDiaperException()
        except MissingDataError as exc:
            raise MissingDataException(exc.missing_fields)
        item.update(enriched)
        return item


class CliDiaperCleaner:
    def __init__(self, dir, fname, fall):
        self.dir = dir
        self.fname = fname
        self.fall = fall
        self.cleaner = DiaperCleaner()

    def _process_file(self, fname):
        logger.info("processing %s", fname)
        result = []
        not_diaper = 0
        missing_data = 0
        with open(fname, "r") as fp:
            items = json.load(fp)
        for item in items:
            try:
                result.append(self.cleaner.enhance(item))
            except NotDiaperException:
                not_diaper += 1
            except MissingDataException:
                missing_data += 1

        splited = fname.split(".")
        fout = f"{splited[0]}.cleaned.{splited[1]}"
        with open(fout, "w") as fp:
            json.dump(result, fp, indent=2)

        if self.fall and result:
            exists = os.path.exists(self.fall) and os.path.getsize(self.fall) > 0
            with open(self.fall, "a", newline="") as fp:
                writer = csv.DictWriter(fp, fieldnames=CSV_KEYS)
                if not exists:
                    writer.writeheader()
                for row in result:
                    writer.writerow({key: row.get(key, "") for key in CSV_KEYS})

        ignored = len(items) - len(result)
        logger.info("out=%s ignored=%s results=%s total=%s missing_data=%s not_diaper=%s", fout, ignored, len(result), len(items), missing_data, not_diaper)
        return len(items), ignored, not_diaper, missing_data

    def process(self):
        results, ignored, not_diaper, missing_data = 0, 0, 0, 0
        if self.dir:
            for root, _, files in os.walk(self.dir):
                for name in files:
                    if "cleaned" not in name:
                        counts = self._process_file(join(root, name))
                        results += counts[0]
                        ignored += counts[1]
                        not_diaper += counts[2]
                        missing_data += counts[3]
        else:
            results, ignored, not_diaper, missing_data = self._process_file(self.fname)
        logger.info("summary ignored=%s missing_data=%s not_diaper=%s results=%s total=%s", ignored, missing_data, not_diaper, results - ignored, results)
        return results, ignored


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("-d", "--dir", type=str, default=DIR_DATA, help="Specify input directory")
    parser.add_argument("-f", "--file", type=str, default=None, help="Specify input file")
    parser.add_argument("-O", "--output", type=str, default=None, help="Specify output CSV file")
    args = parser.parse_args()
    CliDiaperCleaner(args.dir, args.file, args.output).process()


if __name__ == "__main__":
    main()
