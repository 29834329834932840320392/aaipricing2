"""
Vehicle Pydantic schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime
from decimal import Decimal


class VehicleResponse(BaseModel):
    """Schema for vehicle response"""
    id: int
    dealer_id: Optional[int] = None
    competitor_id: Optional[int] = None
    vin: Optional[str] = None
    year: int
    make: str
    model: str
    trim: Optional[str] = None
    msrp: Optional[Decimal] = None
    sale_price: Optional[Decimal] = None
    vdp_url: str
    scraped_at: datetime

    model_config = ConfigDict(from_attributes=True)


class VehicleStats(BaseModel):
    """Schema for vehicle statistics"""
    total_count: int
    avg_msrp: Optional[Decimal] = None
    avg_sale_price: Optional[Decimal] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
