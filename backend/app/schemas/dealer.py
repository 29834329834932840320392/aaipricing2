"""
Dealer and Competitor Pydantic schemas
"""
from pydantic import BaseModel, Field, HttpUrl, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.schemas.platform import WebsitePlatformResponse


class CompetitorBase(BaseModel):
    """Base competitor schema"""
    name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=500)
    platform_id: int


class CompetitorCreate(CompetitorBase):
    """Schema for creating a competitor"""
    dealer_id: int


class CompetitorUpdate(BaseModel):
    """Schema for updating a competitor"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    platform_id: Optional[int] = None
    is_active: Optional[bool] = None


class CompetitorResponse(CompetitorBase):
    """Schema for competitor response"""
    id: int
    dealer_id: int
    is_active: bool
    platform: WebsitePlatformResponse
    last_scraped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DealerBase(BaseModel):
    """Base dealer schema"""
    name: str = Field(..., min_length=1, max_length=200)
    url: str = Field(..., min_length=1, max_length=500)
    platform_id: int


class DealerCreate(DealerBase):
    """Schema for creating a dealer"""
    pass


class DealerUpdate(BaseModel):
    """Schema for updating a dealer"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url: Optional[str] = Field(None, min_length=1, max_length=500)
    platform_id: Optional[int] = None
    is_active: Optional[bool] = None


class DealerResponse(DealerBase):
    """Schema for dealer response"""
    id: int
    is_active: bool
    platform: WebsitePlatformResponse
    competitors: List[CompetitorResponse] = []
    last_scraped_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
