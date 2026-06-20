import os


DUCKDB_PATH = os.environ.get("DUCKDB_PATH", "data/dpaas.duckdb")
LLM_EXTRACTOR = os.environ.get("LLM_EXTRACTOR", "0")
OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "google/gemini-2.0-flash-001")
OPENROUTER_BASE_URL = os.environ.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
SCRAPER_USER_AGENT = os.environ.get("SCRAPER_USER_AGENT", "dpaas-price-research/0.1")
