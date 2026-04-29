"""
Dealer and Competitor models
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Dealer(Base):
    """
    Ancira dealership (the "home team")
    """

    __tablename__ = "dealers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)

    # URL can be base URL or sitemap URL
    url = Column(String(500), nullable=False)

    # Website platform (links to WebsitePlatform table)
    platform_id = Column(Integer, ForeignKey("website_platforms.id"), nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    platform = relationship("WebsitePlatform", lazy="joined")
    competitors = relationship("Competitor", back_populates="dealer", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="dealer", cascade="all, delete-orphan")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Dealer(id={self.id}, name='{self.name}')>"


class Competitor(Base):
    """
    Competitor dealership (linked to an Ancira dealer for comparison)
    Each Ancira dealer can have up to 5 competitors
    """

    __tablename__ = "competitors"

    id = Column(Integer, primary_key=True, index=True)

    # Link to parent Ancira dealer
    dealer_id = Column(Integer, ForeignKey("dealers.id"), nullable=False, index=True)

    # Competitor info
    name = Column(String(200), nullable=False, index=True)
    url = Column(String(500), nullable=False)
    platform_id = Column(Integer, ForeignKey("website_platforms.id"), nullable=False)

    # Status
    is_active = Column(Boolean, default=True, nullable=False)

    # Relationships
    dealer = relationship("Dealer", back_populates="competitors")
    platform = relationship("WebsitePlatform", lazy="joined")
    vehicles = relationship("Vehicle", back_populates="competitor", cascade="all, delete-orphan")

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<Competitor(id={self.id}, name='{self.name}', dealer_id={self.dealer_id})>"
