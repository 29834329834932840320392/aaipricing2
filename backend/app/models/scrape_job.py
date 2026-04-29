"""
Scrape Job model for tracking background scraping tasks
"""
from sqlalchemy import Column, Integer, String, DateTime, Enum as SQLEnum, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
import enum


class ScrapeJobStatus(str, enum.Enum):
    """Scrape job status enumeration"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ScrapeJob(Base):
    """
    Scrape job tracking - one job per dealer/competitor per refresh
    """

    __tablename__ = "scrape_jobs"

    id = Column(Integer, primary_key=True, index=True)

    # Celery task ID
    task_id = Column(String(255), unique=True, nullable=False, index=True)

    # What is being scraped (one of these will be set)
    dealer_id = Column(Integer, ForeignKey("dealers.id"), nullable=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=True, index=True)

    # Job status
    status = Column(SQLEnum(ScrapeJobStatus), default=ScrapeJobStatus.PENDING, nullable=False, index=True)

    # Progress tracking
    total_vdps = Column(Integer, default=0)
    processed_vdps = Column(Integer, default=0)
    successful_vdps = Column(Integer, default=0)
    failed_vdps = Column(Integer, default=0)

    # Error tracking
    error_message = Column(Text, nullable=True)
    errors = Column(JSON, nullable=True)  # Array of error details

    # AI usage tracking
    ai_tokens_used = Column(Integer, default=0)
    ai_calls_made = Column(Integer, default=0)

    # User who triggered the scrape
    triggered_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    dealer = relationship("Dealer")
    competitor = relationship("Competitor")
    triggered_by = relationship("User")
    vehicles = relationship("Vehicle", back_populates="scrape_job")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<ScrapeJob(id={self.id}, status='{self.status}', progress={self.processed_vdps}/{self.total_vdps})>"
