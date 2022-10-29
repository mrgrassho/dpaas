import re
import json
from typing import Dict, TypedDict, Union

from .items import ScraperItem
from .constants import DIAPER_SIZES, DIAPERS_NO_BRAND_REGEX, DIAPERS_REGEX

class CommonDiaperException(Exception):
    pass

class NotDiaperException(CommonDiaperException):
    pass

class MissingDataException(CommonDiaperException):
    def __init__(self, missing_fields):
        self.missing_fields = missing_fields


class ReplacementDict(TypedDict):
    brand: Dict
    size: Dict


DEFAULT_REPLACEMENTS : ReplacementDict = {
    "brand": {
        "huggies": [r"hugies", r"hug(?=\s)"],
        "pampers": [r"pamp(?=\s+)", r"^pants(?=\s+)"],
        "babysec": [r"baby sec"],
    },
    "size": {
        "pr": [r"prematuro", r"prem(?=\s+)"],
        "rn": [r"reci.*n nacido", r"r\.n"],
        "g": [r"grande", r"gde", r"gd", r"(?<=\s)l(?=\s+)"],
        "m": [r"s\-m", r"mediano(?=\s*)", r"(?<=\s)med(?=\s+)"],
        "p": [r"pequeño", r"peq"],
        "xg": [r"xl"],
        "x": [r"extra "],
        "xxg": [r"xxxg" ],
    }
}

PROMOS_PACKS = {
    "promo pack (?P<pack>[0-9]+)",
    "pack x(?P<pack>[0-9]+)",
}

REPLACEMENTS_BLANCKS = {
    " ": ["\u00a0"]
}

class DiaperCleaner:
    def __init__(self, replacements: Union[Dict, str]=None):
        _replacements = {}
        if isinstance(replacements, str):
            _replacements = json.load(open(replacements, 'r'))
        elif isinstance(replacements, dict):
            _replacements = replacements
        self.replacements = {**DEFAULT_REPLACEMENTS, **_replacements}

    def _extract_info(self, description: str) -> Dict:
        """Extract information such as brand, size and units based on
        a provided descrition.

        :param description: Item description
        :type description: str
        :raises NotDiaperException: There is not an attribute match
        :return: Returns a dictionary information
        :rtype: Dict
        """
        for expresion in DIAPERS_REGEX:
            match = re.search(expresion, description)
            if match:
                data = {
                    "brand": match.group("brand")
                }
                if len(match.groups()) >= 2:
                    data["size"] = match.group("size")
                if len(match.groups()) >= 3:
                    data["units"] = int(match.group("units"))
                return data
        raise NotDiaperException()

    def _size_and_units(self, size_units: str) -> Dict:
        for expresion in DIAPERS_NO_BRAND_REGEX:
            match = re.search(expresion, size_units)
            if match:
                data = {
                    "size": match.group("size")
                }
                if len(match.groups()) >= 2:
                    data["units"] = int(match.group("units"))
                return data

    def _get_pack(self, description: str) -> int:
        for expresion in PROMOS_PACKS:
            match = re.search(expresion, description)
            if match:
                return int(match.group("pack"))
        return 1

    def _sanitize_float(self, item: str) -> float:
        """Given a string number formatted as currency returns a float.

        :param item: String number
        :type item: str
        :return: Floats
        :rtype: float
        """
        try:
            if not item:
                return None
            if isinstance(item, str) and re.match(".*\.\d{3}", item):
                item = item.replace(".", "")
            return float(item)
        except ValueError:
            if re.match(".*\.\d{2}$", item):
                return float(item.replace(",", ""))
            elif re.match(".*\,\d{2}$", item):
                return float(item.replace(".", "").replace(",", "."))

    def _sanitize_key(self, key: str, val: str) -> str:
        """Sanitizes key to a standard format.

        This methods applies the following operations:
         - Lowercase strings.
         - Applies replacements based on key

        :param description: Raw description
        :type description: str
        :return: Sanitized description
        :rtype: str
        """
        if not val:
            return None
        rvalue = val.lower()
        for fstr, repls in REPLACEMENTS_BLANCKS.items():
            for repl in repls:
                rvalue = rvalue.replace(repl, fstr)
        current_replacements = self.replacements.get(key)
        for value, expressions in current_replacements.items():
            for expresion in expressions:
                if re.search(expresion, rvalue):
                    rvalue = re.sub(expresion, value, rvalue)
                    break
        return rvalue

    def _sanitize_size(self, value: str) -> str:
        return self._sanitize_key("size", value)

    def _sanitize_brand(self, value: str) -> str:
        return self._sanitize_key("brand", value)

    def _sanitize_description(self, value: str) -> str:
        rvalue = self._sanitize_key("size", value)
        return self._sanitize_key("brand", rvalue)

    def _sanitize_fields(self, item: ScraperItem) -> ScraperItem:
        item.update({
            "price": self._sanitize_float(item.get("price")),
            "description": self._sanitize_description(item.get("description")),
            "size": self._sanitize_size(item.get("size")),
            "brand": self._sanitize_brand(item.get("brand")),
            "units": int(item.get("units")) if item.get("units") else None,
        })
        return item

    def _get_target_kg(self, item: ScraperItem) -> str:
        target_kg = DIAPER_SIZES.get(item.get("brand"), {}).get(item.get("size"))
        return {
            "target_kg_min": target_kg.get("min") if target_kg else None,
            "target_kg_max": target_kg.get("max") if target_kg else None
        }

    def _get_unit_price(self, item: ScraperItem) -> str:
        units = item.get("units")
        price = item.get("price")
        return round(price / int(units), 2) if all((units, price)) else None

    def _check_keys(self, item, keys):
        _keys = []
        for key in keys:
            val = item.get(key)
            if val is None or val == "":
                _keys.append(key)
        if _keys:
            raise MissingDataException(_keys)

    def enhance(self, item: ScraperItem) -> ScraperItem:
        item = self._sanitize_fields(item)
        brand = item.get("brand")
        size = item.get("size")
        units = item.get("units")
        description = item.get("description") or ""
        if not all((brand, size, units)):
            extracted_info = self._extract_info(description)
            item.update(**extracted_info)
        if not item.get("units") and item.get("size"):
            extracted_info = self._size_and_units(item.get("size"))
            item.update(**extracted_info) if extracted_info else None
        self._check_keys(item, ["brand", "price", "size", "units"])
        item["units"] *= self._get_pack(description)
        target_kgs = self._get_target_kg(item)
        item.update(**target_kgs)
        item["unit_price"] = self._get_unit_price(item)
        return item
