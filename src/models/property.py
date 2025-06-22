"""
Property data models
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class PropertyBase(BaseModel):
    address: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    square_footage: Optional[int] = None
    bedrooms: Optional[int] = None
    bathrooms: Optional[float] = None
    year_built: Optional[int] = None
    property_type: Optional[str] = None
    lot_size: Optional[int] = None

class Property(PropertyBase):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class PropertySale(BaseModel):
    property_id: int
    sale_price: Decimal
    sale_date: datetime
    list_price: Optional[Decimal] = None
    days_on_market: Optional[int] = None
    sale_type: str  # 'sold', 'active', 'pending', 'expired'

class PropertyFeature(BaseModel):
    property_id: int
    feature_name: str
    feature_value: str

class ComparableProperty(Property):
    sale_price: Decimal
    sale_date: datetime
    distance_miles: float
    similarity_score: float
    adjustments: dict
    adjusted_price: Decimal 