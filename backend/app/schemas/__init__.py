"""
Pydantic schemas for API request/response validation
"""
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserLogin,
    Token,
    TokenResponse,
)
from app.schemas.system import SystemSettingsResponse, SystemSettingsUpdate
from app.schemas.platform import WebsitePlatformBase, WebsitePlatformCreate, WebsitePlatformResponse
from app.schemas.dealer import (
    DealerBase,
    DealerCreate,
    DealerUpdate,
    DealerResponse,
    CompetitorBase,
    CompetitorCreate,
    CompetitorUpdate,
    CompetitorResponse,
)
from app.schemas.vehicle import VehicleResponse, VehicleStats
from app.schemas.scrape import ScrapeJobResponse, ScrapeJobCreate, ScrapeProgress

__all__ = [
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    "Token",
    "TokenResponse",
    "SystemSettingsResponse",
    "SystemSettingsUpdate",
    "WebsitePlatformBase",
    "WebsitePlatformCreate",
    "WebsitePlatformResponse",
    "DealerBase",
    "DealerCreate",
    "DealerUpdate",
    "DealerResponse",
    "CompetitorBase",
    "CompetitorCreate",
    "CompetitorUpdate",
    "CompetitorResponse",
    "VehicleResponse",
    "VehicleStats",
    "ScrapeJobResponse",
    "ScrapeJobCreate",
    "ScrapeProgress",
]
