import pytest


duckdb = pytest.importorskip("duckdb")

from dpaas_core.storage import DuckDBStore


def test_schema_creation_and_append_only_latest_query(tmp_path):
    store = DuckDBStore(str(tmp_path / "test.duckdb"))
    try:
        run_id = store.start_run("test")
        raw = {
            "description": "Pampers M x 48",
            "price": "2400",
            "website": "example.test",
            "url": "https://example.test/pampers-m",
            "scraped_at": "2024-01-01T00:00:00",
        }
        raw_later = dict(raw, price="3000", scraped_at="2024-01-02T00:00:00")

        ok1, _ = store.write_raw_item(raw, run_id=run_id)
        ok2, _ = store.write_raw_item(raw_later, run_id=run_id)
        store.finish_run(run_id)

        latest = store.query_observations(latest=True)
        history = store.query_observations(latest=False)

        assert ok1 and ok2
        assert len(latest) == 1
        assert len(history) == 2
        assert latest[0]["price"] == 3000.0
    finally:
        store.close()


def test_rejected_observations_are_recorded(tmp_path):
    store = DuckDBStore(str(tmp_path / "test.duckdb"))
    try:
        run_id = store.start_run("test")
        ok, observation_id = store.write_raw_item({"description": "Oleo calcarea", "price": "100"}, run_id=run_id)
        quality = store.data_quality()

        assert not ok
        assert observation_id is None
        assert quality["rejected_observations"] == 1
        assert "not_diaper" in quality["rejection_reasons"]
    finally:
        store.close()
