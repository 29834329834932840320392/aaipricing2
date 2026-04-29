"""
Website Platform model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.database import Base


class WebsitePlatform(Base):
    """
    Website platforms (e.g., Dealer Inspire, DealerOn, Dealer.com, CDK, Sincro)
    Each platform will have a corresponding scraper module
    """

    __tablename__ = "website_platforms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)  # Notes about the platform

    # Future: Scraper configuration (JSON field)
    # scraper_config = Column(JSON, nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self):
        return f"<WebsitePlatform(id={self.id}, name='{self.name}')>"
