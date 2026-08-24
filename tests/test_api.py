import importlib

import pytest


pytest.importorskip("fastapi")
pytest.importorskip("duckdb")


from fastapi.testclient import TestClient
from dpaas_core.storage import DuckDBStore


def test_query_diapers_and_analytics_filters(tmp_path, monkeypatch):
    db_path = tmp_path / "api.duckdb"
    store = DuckDBStore(str(db_path))
    try:
        run_id = store.start_run("test")
        store.write_raw_item(
            {
                "description": "Huggies G x 60",
                "price": "6000",
                "website": "example.test",
                "url": "https://example.test/huggies-g",
                "scraped_at": "2024-01-01T00:00:00",
            },
            run_id=run_id,
        )
        store.finish_run(run_id)
    finally:
        store.close()

    monkeypatch.setenv("DUCKDB_PATH", str(db_path))
    import app.settings
    import app.main

    importlib.reload(app.settings)
    main = importlib.reload(app.main)
    client = TestClient(main.app)

    response = client.get("/query-diapers?brands=huggies")
    assert response.status_code == 200
    assert response.json()[0]["brand"] == "huggies"
    assert "scraped_at" in response.json()[0]
    assert "target_kg" in response.json()[0]
    assert "percentil_girls" in response.json()[0]

    summary = client.get("/analytics/brand-size-summary?brands=huggies")
    assert summary.status_code == 200
    assert summary.json()[0]["product_count"] == 1


def test_source_stores_endpoint_filters_catalog(monkeypatch, tmp_path):
    monkeypatch.setenv("DUCKDB_PATH", str(tmp_path / "api.duckdb"))

    import app.settings
    import app.main

    importlib.reload(app.settings)
    main = importlib.reload(app.main)
    client = TestClient(main.app)

    response = client.get("/source-stores?availability=available&region=amba&popular_buenos_aires=true")
    assert response.status_code == 200
    ids = {row["id"] for row in response.json()}
    assert "farmacity" in ids
    assert "panalera_matlu" not in ids

    inactive = client.get("/source-stores?availability=unavailable,needs_review")
    assert inactive.status_code == 200
    assert any(row["id"] == "panalera_matlu" for row in inactive.json())
