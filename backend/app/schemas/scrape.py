"""
Scrape Job Pydantic schemas
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.scrape_job import ScrapeJobStatus


class ScrapeJobCreate(BaseModel):
    """Schema for creating a scrape job"""
    dealer_id: int
    include_competitors: bool = True


class ScrapeProgress(BaseModel):
    """Schema for scrape progress updates"""
    total_vdps: int
    processed_vdps: int
    successful_vdps: int
    failed_vdps: int
    percent_complete: float


class ScrapeJobResponse(BaseModel):
    """Schema for scrape job response"""
    id: int
    task_id: str
    dealer_id: Optional[int] = None
    competitor_id: Optional[int] = None
    status: ScrapeJobStatus

    # Progress
    total_vdps: int
    processed_vdps: int
    successful_vdps: int
    failed_vdps: int

    # AI usage
    ai_tokens_used: int
    ai_calls_made: int

    # Errors
    error_message: Optional[str] = None
    errors: Optional[List[Dict[str, Any]]] = None

    # Timestamps
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

    @property
    def percent_complete(self) -> float:
        """Calculate completion percentage"""
        if self.total_vdps == 0:
            return 0.0
        return (self.processed_vdps / self.total_vdps) * 100
