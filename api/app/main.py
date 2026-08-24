from __future__ import annotations

from html import escape
from typing import List, Optional

from fastapi import FastAPI, Query, Response
from fastapi.responses import HTMLResponse

from dpaas_core import analytics
from dpaas_core.schemas import BrandSizeSummary, DiaperObservation, PriceSeriesPoint, SourceStore
from dpaas_core.source_catalog import list_source_stores
from dpaas_core.storage import DuckDBStore

from .settings import DUCKDB_PATH


app = FastAPI(title="DPAAS Diaper Price API")


def get_store() -> DuckDBStore:
    return DuckDBStore(DUCKDB_PATH)


def _filters(
    price_lte: Optional[float] = None,
    price_gte: Optional[float] = None,
    brands: Optional[str] = None,
    sizes: Optional[str] = None,
    websites: Optional[str] = None,
    target_kg: Optional[float] = None,
    unit_price_lte: Optional[float] = None,
    unit_price_gte: Optional[float] = None,
):
    return {
        "price_lte": price_lte,
        "price_gte": price_gte,
        "brands": brands,
        "sizes": sizes,
        "websites": websites,
        "target_kg": target_kg,
        "unit_price_lte": unit_price_lte,
        "unit_price_gte": unit_price_gte,
    }


@app.get("/query-diapers", response_model=List[DiaperObservation])
def query_diapers(
    price_lte: Optional[float] = Query(None),
    price_gte: Optional[float] = Query(None),
    brands: Optional[str] = Query(None),
    sizes: Optional[str] = Query(None),
    websites: Optional[str] = Query(None),
    target_kg: Optional[float] = Query(None),
    unit_price_lte: Optional[float] = Query(None),
    unit_price_gte: Optional[float] = Query(None),
    history: bool = Query(False),
    page: int = Query(1, ge=1),
    page_limit: int = Query(20, ge=1, le=500),
):
    store = get_store()
    try:
        return store.query_observations(
            filters=_filters(price_lte, price_gte, brands, sizes, websites, target_kg, unit_price_lte, unit_price_gte),
            latest=not history,
            page=page,
            page_limit=page_limit,
        )
    finally:
        store.close()


@app.get("/analytics/price-series", response_model=List[PriceSeriesPoint])
def price_series(
    brands: Optional[str] = Query(None),
    sizes: Optional[str] = Query(None),
    websites: Optional[str] = Query(None),
    target_kg: Optional[float] = Query(None),
):
    store = get_store()
    try:
        return analytics.price_series(store, _filters(brands=brands, sizes=sizes, websites=websites, target_kg=target_kg))
    finally:
        store.close()


@app.get("/analytics/brand-size-summary", response_model=List[BrandSizeSummary])
def brand_size_summary(
    brands: Optional[str] = Query(None),
    sizes: Optional[str] = Query(None),
    websites: Optional[str] = Query(None),
    target_kg: Optional[float] = Query(None),
):
    store = get_store()
    try:
        return analytics.brand_size_summary(store, _filters(brands=brands, sizes=sizes, websites=websites, target_kg=target_kg))
    finally:
        store.close()


@app.get("/analytics/cost-scenarios")
def cost_scenarios(
    brands: Optional[str] = Query(None),
    sizes: Optional[str] = Query(None),
    websites: Optional[str] = Query(None),
    target_kg: Optional[float] = Query(None),
    months: int = Query(36, ge=0, le=72),
    usage_schedule: Optional[str] = Query(None, description="Ranges like 0-1:10,2-5:8"),
):
    store = get_store()
    try:
        return analytics.cost_scenarios(
            store,
            _filters(brands=brands, sizes=sizes, websites=websites, target_kg=target_kg),
            months=months,
            usage_schedule=usage_schedule,
        )
    finally:
        store.close()


@app.get("/analytics/data-quality")
def data_quality():
    store = get_store()
    try:
        return analytics.data_quality(store)
    finally:
        store.close()


@app.get("/source-stores", response_model=List[SourceStore])
def source_stores(
    availability: Optional[str] = Query(None, description="Comma-separated statuses: available, unavailable, needs_review"),
    region: Optional[str] = Query(None, description="Region tag such as caba, gba, amba, rosario"),
    scraper_status: Optional[str] = Query(None, description="Comma-separated scraper statuses: implemented, candidate, needs_review"),
    popular_buenos_aires: Optional[bool] = Query(None),
):
    return list_source_stores(
        availability=availability,
        region=region,
        scraper_status=scraper_status,
        popular_buenos_aires=popular_buenos_aires,
    )


@app.get("/exports/observations.csv")
def export_observations(history: bool = Query(True)):
    store = get_store()
    try:
        csv_text = store.observations_csv(latest=not history)
        return Response(
            content=csv_text,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=observations.csv"},
        )
    finally:
        store.close()


@app.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    store = get_store()
    try:
        quality = analytics.data_quality(store)
        summary = analytics.brand_size_summary(store)[:25]
    finally:
        store.close()
    sources = list_source_stores()
    active_sources = [source for source in sources if source["status"] == "available"]
    follow_up_sources = [source for source in sources if source["status"] != "available" or source["scraper_status"] != "implemented"][:20]

    rows = "\n".join(
        f"<tr><td>{escape(str(item.get('brand') or ''))}</td><td>{escape(str(item.get('size') or ''))}</td>"
        f"<td>{item.get('product_count')}</td><td>{item.get('min_unit_price') or ''}</td>"
        f"<td>{item.get('avg_unit_price') or ''}</td><td>{item.get('max_unit_price') or ''}</td></tr>"
        for item in summary
    )
    source_rows = "\n".join(
        f"<tr><td>{escape(source['name'])}</td><td>{escape(source['status'])}</td>"
        f"<td>{escape(source['scraper_status'])}</td><td>{escape(', '.join(source.get('regions') or []))}</td>"
        f"<td><a href=\"{escape(source.get('canonical_url') or source['diaper_url'])}\">open</a></td></tr>"
        for source in follow_up_sources
    )
    return f"""
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>DPAAS Dashboard</title>
      <style>
        :root {{
          color-scheme: light;
          --ink: #1f2933;
          --muted: #667085;
          --line: #d7dee8;
          --accent: #176b87;
          --band: #f4f7f9;
          font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
        }}
        body {{ margin: 0; color: var(--ink); background: white; }}
        header {{ padding: 28px 32px 18px; border-bottom: 1px solid var(--line); }}
        h1 {{ margin: 0; font-size: 28px; line-height: 1.2; letter-spacing: 0; }}
        main {{ padding: 24px 32px 40px; }}
        .metrics {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 12px; margin-bottom: 28px; }}
        .metric {{ border: 1px solid var(--line); border-radius: 8px; padding: 14px; background: var(--band); }}
        .metric strong {{ display: block; font-size: 24px; line-height: 1.2; }}
        .metric span {{ color: var(--muted); font-size: 13px; }}
        h2 {{ margin: 0 0 12px; font-size: 18px; letter-spacing: 0; }}
        table {{ width: 100%; border-collapse: collapse; font-size: 14px; }}
        th, td {{ padding: 10px 8px; border-bottom: 1px solid var(--line); text-align: left; }}
        th {{ color: var(--muted); font-weight: 600; background: #fbfcfd; }}
        a {{ color: var(--accent); }}
      </style>
    </head>
    <body>
      <header><h1>DPAAS Dashboard</h1></header>
      <main>
        <section class="metrics">
          <div class="metric"><strong>{quality.get('products')}</strong><span>Products</span></div>
          <div class="metric"><strong>{quality.get('observations')}</strong><span>Observations</span></div>
          <div class="metric"><strong>{quality.get('rejected_observations')}</strong><span>Rejected</span></div>
          <div class="metric"><strong>{quality.get('pipeline_runs')}</strong><span>Pipeline runs</span></div>
          <div class="metric"><strong>{len(active_sources)}</strong><span>Available sources</span></div>
        </section>
        <section>
          <h2>Brand Size Summary</h2>
          <table>
            <thead><tr><th>Brand</th><th>Size</th><th>Products</th><th>Min unit</th><th>Avg unit</th><th>Max unit</th></tr></thead>
            <tbody>{rows}</tbody>
          </table>
        </section>
        <section>
          <h2>Source Follow Up</h2>
          <table>
            <thead><tr><th>Store</th><th>Status</th><th>Scraper</th><th>Regions</th><th>URL</th></tr></thead>
            <tbody>{source_rows}</tbody>
          </table>
        </section>
      </main>
    </body>
    </html>
    """
