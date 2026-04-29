"""
Platform Router - routes scraping requests to the correct platform scraper
"""
from typing import Type, Optional
from app.scrapers.base import BaseScraper
from app.scrapers.dealer_inspire import DealerInspireScraper
import logging

logger = logging.getLogger(__name__)


class PlatformRouter:
    """
    Routes scraping requests to the appropriate platform scraper

    This is the central dispatcher that maps platform names to scraper classes.
    """

    # Platform name → Scraper class mapping
    PLATFORM_SCRAPERS = {
        "dealer inspire": DealerInspireScraper,
        "dealerinspire": DealerInspireScraper,
        # Future platforms:
        # "dealeron": DealerOnScraper,
        # "dealer.com": DealerDotComScraper,
        # "cdk": CDKScraper,
        # "sincro": SincroScraper,
    }

    @classmethod
    def get_scraper_class(cls, platform_name: str) -> Optional[Type[BaseScraper]]:
        """
        Get the scraper class for a given platform

        Args:
            platform_name: Name of the platform (case-insensitive)

        Returns:
            Scraper class, or None if platform not supported
        """
        platform_key = platform_name.lower().strip()
        scraper_class = cls.PLATFORM_SCRAPERS.get(platform_key)

        if scraper_class is None:
            logger.warning(f"No scraper found for platform: {platform_name}")

        return scraper_class

    @classmethod
    def create_scraper(
        cls,
        platform_name: str,
        url: str,
        headless: bool = True,
        timeout: int = 30000
    ) -> Optional[BaseScraper]:
        """
        Create a scraper instance for the given platform

        Args:
            platform_name: Name of the platform
            url: Dealership URL or sitemap URL
            headless: Run browser in headless mode
            timeout: Page load timeout

        Returns:
            Scraper instance, or None if platform not supported
        """
        scraper_class = cls.get_scraper_class(platform_name)

        if scraper_class is None:
            return None

        logger.info(f"Creating {scraper_class.__name__} for {url}")
        return scraper_class(url=url, headless=headless, timeout=timeout)

    @classmethod
    def is_platform_supported(cls, platform_name: str) -> bool:
        """Check if a platform is supported"""
        return cls.get_scraper_class(platform_name) is not None

    @classmethod
    def list_supported_platforms(cls) -> list:
        """List all supported platform names"""
        return list(cls.PLATFORM_SCRAPERS.keys())
