"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Database
    DATABASE_URL: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20

    # Redis & Celery
    REDIS_URL: str
    CELERY_BROKER_URL: str
    CELERY_RESULT_BACKEND: str

    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ENCRYPTION_KEY: str

    # Application
    APP_NAME: str = "Ancira Competitive Intelligence Dashboard"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "production"

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Scraping
    SCRAPE_VDP_LIMIT: int = 10  # TODO: Remove 10-VDP limit before production
    SCRAPE_TIMEOUT_SECONDS: int = 30
    PLAYWRIGHT_HEADLESS: bool = True

    # OpenAI
    DEFAULT_OPENAI_MODEL: str = "gpt-5.4-mini-2026-03-17"

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "/var/log/ancira-intel/app.log"

    # Initial Admin (created on first startup)
    INITIAL_ADMIN_USERNAME: str = "admin"
    INITIAL_ADMIN_EMAIL: str = "admin@anciragroup.com"
    INITIAL_ADMIN_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Export settings instance
settings = get_settings()
