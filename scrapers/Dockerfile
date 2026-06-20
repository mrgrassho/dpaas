FROM python:3.9-slim-buster

WORKDIR /app

COPY scrapers/requirements.txt /tmp/requirements.txt

RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r /tmp/requirements.txt

COPY dpaas_core /app/dpaas_core
COPY scrapers/scraper /app/scraper
COPY scrapers/scrapy.cfg /app/scrapy.cfg

ENV PYTHONPATH=/app
