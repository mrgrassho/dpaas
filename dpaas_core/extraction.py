from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import unicodedata
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple


logger = logging.getLogger(__name__)


class ExtractionError(Exception):
    """Base class for extraction failures."""


class NotDiaperError(ExtractionError):
    """Raised when a raw item does not look like a diaper product."""


class MissingDataError(ExtractionError):
    def __init__(self, missing_fields: Iterable[str]):
        self.missing_fields = list(missing_fields)
        super().__init__(", ".join(self.missing_fields))


KNOWN_BRAND_PATTERNS = {
    "huggies": [r"\bhuggies\b", r"\bhugies\b", r"\bhug(?=\s)"],
    "pampers": [r"\bpampers\b", r"\bpamp(?=\s+)", r"\bpants(?=\s+)"],
    "babysec": [r"\bbabysec\b", r"\bbaby\s+sec\b"],
    "estrella": [r"\bestrella\b"],
}

SIZE_PATTERNS = [
    ("xxxg", [r"\bxxxg\b", r"\bxxxl\b", r"\b3xg\b"]),
    ("xxg", [r"\bxxg\b", r"\bxxl\b", r"\b2xg\b"]),
    ("xg", [r"\bxg\b", r"\bxl\b"]),
    ("rn+", [r"\brn\s*\+\b", r"\brn\s*plus\b"]),
    ("rn", [r"\brn\b", r"\br\.n\b", r"\brecien\s+nacido\b"]),
    ("pr", [r"\bpr\b", r"\bprematuro\b", r"\bprem(?=\s+)"]),
    ("m", [r"\bm\b", r"\bmediano\b", r"\bmed\b", r"\bs-m\b"]),
    ("g", [r"\bg\b", r"\bgrande\b", r"\bgde\b", r"\bgd\b", r"\bl\b"]),
    ("p", [r"\bp\b", r"\bpequeno\b", r"\bpeq\b"]),
]

STOP_BRAND_TOKENS = {
    "panal",
    "panales",
    "bebe",
    "bebes",
    "mega",
    "pack",
    "super",
    "premium",
    "care",
    "confort",
    "comfort",
    "active",
    "sec",
    "pants",
}

DIAPER_SIZE_TABLE = {
    "huggies": {
        "pr": (0.0, 2.2),
        "rn": (0.0, 4.0),
        "p": (3.5, 6.0),
        "m": (5.5, 9.5),
        "g": (9.0, 12.5),
        "xg": (12.0, 15.0),
        "xxg": (14.0, 20.0),
        "xxxg": (17.0, None),
    },
    "pampers": {
        "rn": (0.0, 4.5),
        "rn+": (3.0, 6.0),
        "p": (5.0, 7.5),
        "m": (6.0, 9.5),
        "g": (9.0, 12.0),
        "xg": (12.0, 15.0),
        "xxg": (14.0, 20.0),
        "xxxg": (17.0, None),
    },
    "babysec": {
        "rn": (0.0, 4.5),
        "p": (0.0, 6.0),
        "m": (5.0, 9.5),
        "g": (8.5, 12.0),
        "xg": (11.0, 15.0),
        "xxg": (13.0, 20.0),
        "xxxg": (17.0, None),
    },
    "estrella": {
        "p": (5.0, 7.5),
        "m": (6.0, 9.5),
        "g": (9.0, 12.0),
        "xg": (12.0, 15.0),
        "xxg": (14.0, 20.0),
        "xxxg": (17.0, None),
    },
}


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    text = str(value).replace("\u00a0", " ").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text)


def parse_price(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = re.sub(r"[^\d,.\-]", "", str(value))
    if not text:
        return None
    if "," in text and "." in text:
        if text.rfind(",") > text.rfind("."):
            text = text.replace(".", "").replace(",", ".")
        else:
            text = text.replace(",", "")
    elif "," in text:
        text = text.replace(".", "").replace(",", ".")
    elif "." in text:
        parts = text.split(".")
        if len(parts) > 1 and len(parts[-1]) == 3 and all(len(part) == 3 for part in parts[1:]):
            text = "".join(parts)
    try:
        return float(text)
    except ValueError:
        return None


def parse_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    match = re.search(r"\d+", str(value))
    return int(match.group(0)) if match else None


def normalize_brand(value: Any) -> Optional[str]:
    text = normalize_text(value)
    if not text:
        return None
    for brand, patterns in KNOWN_BRAND_PATTERNS.items():
        if any(re.search(pattern, text) for pattern in patterns):
            return brand
    cleaned = re.sub(r"[^a-z0-9 ]+", " ", text).strip()
    return re.sub(r"\s+", " ", cleaned) or None


def extract_known_brand(text: str) -> Optional[str]:
    for brand, patterns in KNOWN_BRAND_PATTERNS.items():
        if any(re.search(pattern, text) for pattern in patterns):
            return brand
    return None


def extract_arbitrary_brand(text: str) -> Optional[str]:
    if not re.search(r"\bpanales?\b|\bdiapers?\b", text):
        return None
    candidates = []
    for pattern in (r"\bpanales?\s+([a-z0-9][a-z0-9\-]*)", r"\b([a-z0-9][a-z0-9\-]*)\b.*\bpanales?\b"):
        match = re.search(pattern, text)
        if match:
            candidates.append(match.group(1))
    for candidate in candidates:
        candidate = candidate.strip("- ")
        if candidate and candidate not in STOP_BRAND_TOKENS and not normalize_size(candidate):
            return candidate
    return None


def normalize_size(value: Any) -> Optional[str]:
    text = normalize_text(value)
    if not text:
        return None
    for size, patterns in SIZE_PATTERNS:
        if any(re.search(pattern, text) for pattern in patterns):
            return size
    return None


def _parse_weight_number(value: str) -> float:
    return float(value.replace(",", "."))


def extract_kg_range(text: str) -> Tuple[Optional[float], Optional[float]]:
    range_patterns = [
        r"(?:de\s+|desde\s+)?(?P<min>\d+(?:[\.,]\d+)?)\s*(?:a|hasta|\-|/)\s*(?P<max>\d+(?:[\.,]\d+)?)\s*kg",
        r"(?P<min>\d+(?:[\.,]\d+)?)\s*kg\s*(?:a|hasta|\-|/)\s*(?P<max>\d+(?:[\.,]\d+)?)\s*kg",
    ]
    for pattern in range_patterns:
        match = re.search(pattern, text)
        if match:
            return _parse_weight_number(match.group("min")), _parse_weight_number(match.group("max"))

    min_match = re.search(r"(?:mas\s+de|mayor\s+a|desde)\s*(?P<min>\d+(?:[\.,]\d+)?)\s*kg", text)
    if min_match:
        return _parse_weight_number(min_match.group("min")), None

    max_match = re.search(r"hasta\s*(?P<max>\d+(?:[\.,]\d+)?)\s*kg", text)
    if max_match:
        return 0.0, _parse_weight_number(max_match.group("max"))

    return None, None


def table_target_kg(brand: Optional[str], size: Optional[str]) -> Tuple[Optional[float], Optional[float]]:
    if not brand or not size:
        return None, None
    target = DIAPER_SIZE_TABLE.get(brand, {}).get(size)
    return target if target else (None, None)


def extract_units(raw_units: Any, text: str) -> Optional[int]:
    units = parse_int(raw_units)
    if units:
        return units
    patterns = [
        r"\bx\s*(?P<units>\d{1,4})\b",
        r"\[(?P<units>\d{1,4})\s*uni\.?\]",
        r"\b(?P<units>\d{1,4})\s*(?:u|un|uni|unid|unidades|panales|pa)\.?\b",
        r"\b(?P<units>\d{1,4})\s*$",
    ]
    for pattern in patterns:
        matches = list(re.finditer(pattern, text))
        if matches:
            return int(matches[-1].group("units"))
    return None


def extract_pack_multiplier(text: str) -> int:
    patterns = [
        r"(?:promo|combo)\s*(?:pack\s*)?x\s*(?P<pack>\d{1,2})\b",
        r"\b(?P<pack>\d{1,2})\s*(?:packs|paquetes)\b",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            value = int(match.group("pack"))
            return value if value > 0 else 1
    return 1


def stable_cache_key(raw_item: Mapping[str, Any], model: str) -> str:
    payload = json.dumps(raw_item, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(f"{model}:{payload}".encode("utf-8")).hexdigest()


@dataclass
class RuleBasedExtractor:
    """Deterministic product enrichment for diaper listings."""

    require_brand: bool = True

    def enrich(self, raw_item: Mapping[str, Any]) -> Dict[str, Any]:
        raw = dict(raw_item)
        description_original = (raw.get("description") or "").strip()
        description = normalize_text(description_original)
        source_text = " ".join(
            part for part in [
                description,
                normalize_text(raw.get("brand")),
                normalize_text(raw.get("size")),
                normalize_text(raw.get("units")),
            ]
            if part
        )

        brand = normalize_brand(raw.get("brand")) or extract_known_brand(source_text) or extract_arbitrary_brand(source_text)
        size = normalize_size(raw.get("size")) or normalize_size(source_text)
        units = extract_units(raw.get("units"), source_text)
        price = parse_price(raw.get("price"))

        if not any([brand, size, units]) and not re.search(r"\bpanales?\b|\bdiapers?\b", source_text):
            raise NotDiaperError(description_original or str(raw_item))

        missing = []
        if self.require_brand and not brand:
            missing.append("brand")
        if price is None:
            missing.append("price")
        if not size:
            missing.append("size")
        if not units:
            missing.append("units")
        if missing:
            raise MissingDataError(missing)

        units = units * extract_pack_multiplier(source_text)
        explicit_min, explicit_max = extract_kg_range(source_text)
        if explicit_min is not None or explicit_max is not None:
            target_min, target_max = explicit_min, explicit_max
        else:
            target_min, target_max = table_target_kg(brand, size)

        unit_price = round(price / units, 2) if price is not None and units else None

        return {
            "description": description_original,
            "price": price,
            "url": raw.get("url"),
            "image": raw.get("image"),
            "website": raw.get("website"),
            "brand": brand,
            "size": size,
            "target_kg_min": target_min,
            "target_kg_max": target_max,
            "units": units,
            "unit_price": unit_price,
            "currency": raw.get("currency") or "ARS",
            "scraped_at": raw.get("scraped_at") or raw.get("timestamp") or datetime.utcnow().isoformat(),
            "extraction_method": "rules",
        }


class OpenRouterExtractor:
    """Optional cached OpenRouter structured-output extractor with rule fallback upstream."""

    schema = {
        "type": "object",
        "properties": {
            "is_diaper": {"type": "boolean"},
            "brand": {"type": ["string", "null"]},
            "size": {"type": ["string", "null"]},
            "units": {"type": ["integer", "null"]},
            "target_kg_min": {"type": ["number", "null"]},
            "target_kg_max": {"type": ["number", "null"]},
        },
        "required": ["is_diaper", "brand", "size", "units", "target_kg_min", "target_kg_max"],
        "additionalProperties": False,
    }

    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        base_url: str = "https://openrouter.ai/api/v1",
        storage: Any = None,
        client: Any = None,
        rule_extractor: Optional[RuleBasedExtractor] = None,
        timeout_seconds: float = 30.0,
    ) -> None:
        self.model = model
        self.api_key = api_key or os.environ.get("OPENROUTER_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.storage = storage
        self.client = client
        self.rule_extractor = rule_extractor or RuleBasedExtractor()
        self.timeout_seconds = timeout_seconds

    def _call_model(self, raw_item: Mapping[str, Any]) -> Dict[str, Any]:
        if self.client is not None and hasattr(self.client, "extract"):
            return self.client.extract(raw_item, self.schema)
        if not self.api_key:
            raise MissingDataError(["OPENROUTER_API_KEY"])

        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "Extract diaper product fields from Argentine ecommerce listings. "
                        "Return null for unknown values and do not infer price."
                    ),
                },
                {"role": "user", "content": json.dumps(dict(raw_item), ensure_ascii=False, default=str)},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "diaper_extraction",
                    "strict": True,
                    "schema": self.schema,
                },
            },
            "provider": {
                "require_parameters": True,
            },
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        site_url = os.environ.get("OPENROUTER_SITE_URL")
        app_name = os.environ.get("OPENROUTER_APP_NAME")
        if site_url:
            headers["HTTP-Referer"] = site_url
        if app_name:
            headers["X-Title"] = app_name

        request = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
                response_payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            body = exc.read().decode("utf-8", errors="replace")
            raise ExtractionError(f"OpenRouter request failed: HTTP {exc.code} {body}") from exc
        except urllib.error.URLError as exc:
            raise ExtractionError(f"OpenRouter request failed: {exc}") from exc

        content = response_payload["choices"][0]["message"]["content"]
        if isinstance(content, list):
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        if not isinstance(content, str) or not content.strip():
            raise ExtractionError("OpenRouter response had no text content")
        return json.loads(content)

    def _cached_response(self, key: str) -> Optional[Dict[str, Any]]:
        if self.storage is None:
            return None
        cached = self.storage.get_extraction_cache(key)
        if not cached:
            return None
        try:
            return json.loads(cached)
        except json.JSONDecodeError:
            return None

    def _store_response(self, key: str, response: Mapping[str, Any]) -> None:
        if self.storage is not None:
            self.storage.set_extraction_cache(
                cache_key=key,
                provider="openrouter",
                model=self.model,
                response_json=json.dumps(dict(response), ensure_ascii=False, sort_keys=True),
            )

    def enrich(self, raw_item: Mapping[str, Any]) -> Dict[str, Any]:
        cache_key = stable_cache_key(raw_item, self.model)
        response = self._cached_response(cache_key)
        if response is None:
            response = self._call_model(raw_item)
            self._store_response(cache_key, response)

        if not response.get("is_diaper", True):
            raise NotDiaperError(raw_item.get("description") or str(raw_item))

        required = {"brand", "size", "units"}
        if any(response.get(key) in (None, "") for key in required):
            raise MissingDataError([key for key in required if response.get(key) in (None, "")])

        merged = dict(raw_item)
        for key in ("brand", "size", "units", "target_kg_min", "target_kg_max"):
            if response.get(key) is not None:
                merged[key] = response.get(key)
        enriched = self.rule_extractor.enrich(merged)
        if response.get("target_kg_min") is not None or response.get("target_kg_max") is not None:
            enriched["target_kg_min"] = response.get("target_kg_min")
            enriched["target_kg_max"] = response.get("target_kg_max")
        enriched["extraction_method"] = "openrouter"
        return enriched


class ExtractionService:
    def __init__(self, rule_extractor: Optional[RuleBasedExtractor] = None, llm_extractor: Optional[OpenRouterExtractor] = None) -> None:
        self.rule_extractor = rule_extractor or RuleBasedExtractor()
        self.llm_extractor = llm_extractor

    @classmethod
    def from_env(cls, storage: Any = None) -> "ExtractionService":
        rule = RuleBasedExtractor()
        enabled = os.environ.get("LLM_EXTRACTOR", "0").lower() in {"1", "true", "yes"}
        if not enabled or not os.environ.get("OPENROUTER_API_KEY"):
            return cls(rule_extractor=rule)
        model = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
        base_url = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        return cls(
            rule_extractor=rule,
            llm_extractor=OpenRouterExtractor(model=model, base_url=base_url, storage=storage, rule_extractor=rule),
        )

    def enrich(self, raw_item: Mapping[str, Any]) -> Dict[str, Any]:
        if self.llm_extractor is not None:
            try:
                return self.llm_extractor.enrich(raw_item)
            except Exception as exc:  # pragma: no cover - exact provider failures vary.
                logger.debug("LLM extraction failed; falling back to rules: %s", exc)
        return self.rule_extractor.enrich(raw_item)
