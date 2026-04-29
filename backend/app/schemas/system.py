"""
System settings Pydantic schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SystemSettingsResponse(BaseModel):
    """Schema for system settings response"""
    id: int
    openai_model: str
    has_api_key: bool  # Don't expose the actual key
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SystemSettingsUpdate(BaseModel):
    """Schema for updating system settings"""
    openai_api_key: Optional[str] = None  # Only set if changing
    openai_model: Optional[str] = None
