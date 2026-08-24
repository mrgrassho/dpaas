from dpaas_core.source_catalog import list_source_stores


def test_source_catalog_filters_available_buenos_aires_candidates():
    rows = list_source_stores(
        availability="available",
        region="amba",
        popular_buenos_aires=True,
    )
    ids = {row["id"] for row in rows}

    assert "farmacity" in ids
    assert "dia" in ids
    assert "panalera_matlu" not in ids


def test_source_catalog_filters_unavailable_pages():
    rows = list_source_stores(availability="unavailable")
    by_id = {row["id"]: row for row in rows}

    assert by_id["panalera_matlu"]["scraper_status"] == "needs_review"
    assert by_id["noninoni"]["http_status"] == 404


def test_run_etl_all_uses_only_active_implemented_sources():
    from scraper.run_etl import _parse_spiders

    selected = _parse_spiders(
        "all",
        ["panales_online", "panalera_matlu", "farmacity", "meli", "custom_spider"],
    )

    assert selected == ["custom_spider", "panales_online"]
