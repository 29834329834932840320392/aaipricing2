"""
Vehicle inventory model
"""
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey, DateTime, Text, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Vehicle(Base):
    """
    Scraped vehicle inventory data
    Each vehicle belongs to either a Dealer (Ancira) or a Competitor
    """

    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys (one of these will be set, the other NULL)
    dealer_id = Column(Integer, ForeignKey("dealers.id"), nullable=True, index=True)
    competitor_id = Column(Integer, ForeignKey("competitors.id"), nullable=True, index=True)

    # Vehicle identification
    vin = Column(String(17), nullable=True, index=True)  # May not always be available
    year = Column(Integer, nullable=False, index=True)
    make = Column(String(100), nullable=False, index=True)
    model = Column(String(100), nullable=False, index=True)
    trim = Column(String(200), nullable=True, index=True)

    # Pricing (stored as Decimal for precision)
    msrp = Column(Numeric(10, 2), nullable=True)  # May be null if not available
    sale_price = Column(Numeric(10, 2), nullable=True)  # May be null if "call for price"

    # Source
    vdp_url = Column(Text, nullable=False)  # Can be long

    # Scraping metadata
    scraped_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    scrape_job_id = Column(Integer, ForeignKey("scrape_jobs.id"), nullable=True, index=True)

    # Relationships
    dealer = relationship("Dealer", back_populates="vehicles")
    competitor = relationship("Competitor", back_populates="vehicles")
    scrape_job = relationship("ScrapeJob", back_populates="vehicles")

    # Composite indexes for common queries
    __table_args__ = (
        Index("idx_vehicle_ymmt", "year", "make", "model", "trim"),
        Index("idx_vehicle_dealer_scraped", "dealer_id", "scraped_at"),
        Index("idx_vehicle_competitor_scraped", "competitor_id", "scraped_at"),
    )

    def __repr__(self):
        return f"<Vehicle(id={self.id}, year={self.year}, make='{self.make}', model='{self.model}')>"
