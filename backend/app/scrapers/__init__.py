"""
Platform-based scraping architecture

Each website platform has its own scraper module that inherits from BaseScraper.
The PlatformRouter routes scraping requests to the appropriate platform scraper.
"""
from app.scrapers.base import BaseScraper, ScrapedVehicle
from app.scrapers.router import PlatformRouter
from app.scrapers.dealer_inspire import DealerInspireScraper

__all__ = [
    "BaseScraper",
    "ScrapedVehicle",
    "PlatformRouter",
    "DealerInspireScraper",
]
