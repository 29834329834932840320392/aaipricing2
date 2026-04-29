"""
Website Platform Pydantic schemas
"""
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class WebsitePlatformBase(BaseModel):
    """Base platform schema"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None


class WebsitePlatformCreate(WebsitePlatformBase):
    """Schema for creating a platform"""
    pass


class WebsitePlatformUpdate(BaseModel):
    """Schema for updating a platform"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None


class WebsitePlatformResponse(WebsitePlatformBase):
    """Schema for platform response"""
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
