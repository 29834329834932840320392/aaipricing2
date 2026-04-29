"""
Database models
"""
from app.models.user import User
from app.models.system import SystemSettings
from app.models.platform import WebsitePlatform
from app.models.dealer import Dealer, Competitor
from app.models.vehicle import Vehicle
from app.models.scrape_job import ScrapeJob

__all__ = [
    "User",
    "SystemSettings",
    "WebsitePlatform",
    "Dealer",
    "Competitor",
    "Vehicle",
    "ScrapeJob",
]
