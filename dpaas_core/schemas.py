from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class TargetKG(BaseModel):
    min: Optional[float] = None
    max: Optional[float] = None


class DiaperObservation(BaseModel):
    observation_id: str
    product_id: str
    description: Optional[str] = None
    price: float
    url: Optional[str] = None
    image: Optional[str] = None
    website: Optional[str] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    target_kg: TargetKG
    units: Optional[int] = None
    unit_price: Optional[float] = None
    currency: str = "ARS"
    scraped_at: datetime
    extraction_method: Optional[str] = None
    percentil_girls: Dict[str, List[int]] = Field(default_factory=dict)
    percentil_boys: Dict[str, List[int]] = Field(default_factory=dict)


class PriceSeriesPoint(BaseModel):
    observation_id: str
    product_id: str
    description: Optional[str] = None
    price: float
    website: Optional[str] = None
    brand: Optional[str] = None
    size: Optional[str] = None
    units: Optional[int] = None
    unit_price: Optional[float] = None
    currency: str = "ARS"
    scraped_at: datetime


class BrandSizeSummary(BaseModel):
    brand: Optional[str] = None
    size: Optional[str] = None
    product_count: int
    min_unit_price: Optional[float] = None
    avg_unit_price: Optional[float] = None
    max_unit_price: Optional[float] = None
    avg_price: Optional[float] = None


class SourceStore(BaseModel):
    id: str
    name: str
    diaper_url: str
    status: str
    scraper_status: str
    homepage_url: Optional[str] = None
    canonical_url: Optional[str] = None
    spider: Optional[str] = None
    ecommerce: Optional[str] = None
    http_status: Optional[int] = None
    checked_at: str
    regions: List[str] = Field(default_factory=list)
    popular_buenos_aires: bool = False
    notes: Optional[str] = None
