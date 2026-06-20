import pytest

from dpaas_core.extraction import ExtractionService, OpenRouterExtractor, RuleBasedExtractor, parse_price


def test_parse_argentine_prices():
    assert parse_price("$3.470") == 3470.0
    assert parse_price("2.190,92") == 2190.92
    assert parse_price("2190.92") == 2190.92


def test_rule_extractor_normalizes_brand_size_units_and_unit_price():
    result = RuleBasedExtractor().enrich(
        {
            "description": "Hugies Classic Grande x 36",
            "price": "$3.600",
            "website": "example.test",
        }
    )
    assert result["brand"] == "huggies"
    assert result["size"] == "g"
    assert result["units"] == 36
    assert result["unit_price"] == 100.0
    assert result["target_kg_min"] == 9.0
    assert result["target_kg_max"] == 12.5


def test_explicit_kg_range_takes_precedence_over_table():
    result = RuleBasedExtractor().enrich(
        {
            "description": "Pampers XG de 10 a 14 kg x 30",
            "price": "1500",
            "website": "example.test",
        }
    )
    assert result["brand"] == "pampers"
    assert result["size"] == "xg"
    assert result["target_kg_min"] == 10.0
    assert result["target_kg_max"] == 14.0


def test_arbitrary_brand_with_diaper_text_is_supported():
    result = RuleBasedExtractor().enrich(
        {
            "description": "Panales Duffy XXG x 20",
            "price": "2000",
            "website": "example.test",
        }
    )
    assert result["brand"] == "duffy"
    assert result["size"] == "xxg"
    assert result["units"] == 20


def test_rule_extractor_handles_compact_tienda_nube_variant_size_units():
    result = RuleBasedExtractor().enrich(
        {
            "description": "Huggies Protect Plus mes de consumo M, G, XG, XXG",
            "price": 20060,
            "website": "example.test",
            "size": "XXGx50",
        }
    )
    assert result["brand"] == "huggies"
    assert result["size"] == "xxg"
    assert result["units"] == 50


def test_rule_extractor_handles_und_and_explicit_kg_range():
    result = RuleBasedExtractor().enrich(
        {
            "description": "BABYSEC ULTRA SEC (talle/peso: G 8.5 a 12 kg. 60 und.)",
            "price": "12000",
            "website": "example.test",
        }
    )
    assert result["brand"] == "babysec"
    assert result["size"] == "g"
    assert result["units"] == 60
    assert result["target_kg_min"] == 8.5
    assert result["target_kg_max"] == 12.0


def test_rule_extractor_handles_line_alias_and_leading_pack_multiplier():
    result = RuleBasedExtractor().enrich(
        {
            "description": "2 Natural Care M x68 + 2 Toallitas Disney Amarillas x48",
            "price": "58.160",
            "website": "example.test",
        }
    )
    assert result["brand"] == "huggies"
    assert result["size"] == "m"
    assert result["units"] == 136


def test_rule_extractor_handles_size_then_units_without_x():
    result = RuleBasedExtractor().enrich(
        {
            "description": "Babysec Ultrasec Med 68 Mes De Cons",
            "price": "16.220",
            "website": "example.test",
        }
    )
    assert result["brand"] == "babysec"
    assert result["size"] == "m"
    assert result["units"] == 68


def test_rule_extractor_preserves_rn_plus_size():
    result = RuleBasedExtractor().enrich(
        {
            "description": "Pampers Deluxe RN+ 56 (hasta 6 kg)",
            "price": "27100",
            "website": "example.test",
        }
    )
    assert result["brand"] == "pampers"
    assert result["size"] == "rn+"
    assert result["units"] == 56


def test_rule_extractor_uses_image_slug_for_sparse_listing_units():
    result = RuleBasedExtractor().enrich(
        {
            "description": "PAMPERS BABYSAN HIPOALERGENICO PAÑAL",
            "price": 39000,
            "website": "example.test",
            "image": "https://cdn.example.test/pampers-babysan-hipo-talle-xg-x58.webp",
        }
    )
    assert result["brand"] == "pampers"
    assert result["size"] == "xg"
    assert result["units"] == 58


def test_rule_extractor_uses_url_slug_for_units():
    result = RuleBasedExtractor().enrich(
        {
            "description": "Pañales Pampers Premium Care XXXG",
            "price": 36890,
            "website": "example.test",
            "url": "https://example.test/productos/panales-pampers-premium-care-xxxg-x52/",
        }
    )
    assert result["brand"] == "pampers"
    assert result["size"] == "xxxg"
    assert result["units"] == 52


def test_rule_extractor_uses_hyphenated_x_units_from_image_slug():
    result = RuleBasedExtractor().enrich(
        {
            "description": "HUGGIES RECIEN NACIDO",
            "price": 11100,
            "website": "example.test",
            "image": "https://cdn.example.test/huggies-natural-care-rec-nacido-x-34.webp",
        }
    )
    assert result["brand"] == "huggies"
    assert result["size"] == "rn"
    assert result["units"] == 34


class FakeOpenRouterClient:
    def __init__(self):
        self.calls = 0

    def extract(self, raw_item, schema):
        self.calls += 1
        return {
            "is_diaper": True,
            "brand": "pampers",
            "size": "m",
            "units": 48,
            "target_kg_min": None,
            "target_kg_max": None,
        }


class FakeCache:
    def __init__(self):
        self.values = {}

    def get_extraction_cache(self, key):
        return self.values.get(key)

    def set_extraction_cache(self, cache_key, provider, model, response_json, prompt_hash=""):
        self.values[cache_key] = response_json


def test_openrouter_extractor_uses_fake_provider_and_cache_only():
    client = FakeOpenRouterClient()
    cache = FakeCache()
    extractor = OpenRouterExtractor(model="test-model", api_key="test-key", client=client, storage=cache)
    service = ExtractionService(llm_extractor=extractor)

    raw = {"description": "texto dificil", "price": 2400, "website": "example.test"}
    first = service.enrich(raw)
    second = service.enrich(raw)

    assert first["brand"] == "pampers"
    assert second["brand"] == "pampers"
    assert client.calls == 1
    assert first["extraction_method"] == "openrouter"
