COMPOSE ?= docker compose
CONTAINER_DUCKDB_PATH ?= /data/dpaas.duckdb
SAMPLE_CSV ?= /app/notebooks/diapers.csv

.PHONY: etl etl-sample api test down

etl:
	CONTAINER_DUCKDB_PATH=$(CONTAINER_DUCKDB_PATH) $(COMPOSE) build scrapers
	CONTAINER_DUCKDB_PATH=$(CONTAINER_DUCKDB_PATH) $(COMPOSE) run --rm scrapers python -m scraper.run_etl --spider all --database $(CONTAINER_DUCKDB_PATH)

etl-sample:
	CONTAINER_DUCKDB_PATH=$(CONTAINER_DUCKDB_PATH) $(COMPOSE) build scrapers
	CONTAINER_DUCKDB_PATH=$(CONTAINER_DUCKDB_PATH) $(COMPOSE) run --rm scrapers python -m scraper.run_etl --sample $(SAMPLE_CSV) --database $(CONTAINER_DUCKDB_PATH)

api:
	CONTAINER_DUCKDB_PATH=$(CONTAINER_DUCKDB_PATH) $(COMPOSE) up --build backend

test:
	CONTAINER_DUCKDB_PATH=$(CONTAINER_DUCKDB_PATH) $(COMPOSE) build tests
	CONTAINER_DUCKDB_PATH=$(CONTAINER_DUCKDB_PATH) $(COMPOSE) run --rm tests

down:
	$(COMPOSE) down
