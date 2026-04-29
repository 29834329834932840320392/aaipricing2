"""
Base scraper class - all platform scrapers inherit from this
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from playwright.async_api import async_playwright, Browser, Page
import logging

logger = logging.getLogger(__name__)


@dataclass
class ScrapedVehicle:
    """Data class for scraped vehicle information"""
    vin: Optional[str]
    year: int
    make: str
    model: str
    trim: Optional[str]
    msrp: Optional[float]
    sale_price: Optional[float]
    vdp_url: str
    raw_html: str  # Store for AI processing


class BaseScraper(ABC):
    """
    Abstract base class for all platform scrapers

    Each platform (Dealer Inspire, DealerOn, etc.) implements this interface.
    """

    def __init__(self, url: str, headless: bool = True, timeout: int = 30000):
        """
        Initialize scraper

        Args:
            url: Base URL or sitemap URL for the dealership
            headless: Run browser in headless mode
            timeout: Page load timeout in milliseconds
        """
        self.url = url
        self.headless = headless
        self.timeout = timeout
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def __aenter__(self):
        """Async context manager entry"""
        await self.start_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.close_browser()

    async def start_browser(self):
        """Start Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.page = await self.browser.new_page()
        self.page.set_default_timeout(self.timeout)
        logger.info(f"Started browser for {self.__class__.__name__}")

    async def close_browser(self):
        """Close Playwright browser"""
        if self.browser:
            await self.browser.close()
            logger.info(f"Closed browser for {self.__class__.__name__}")

    @abstractmethod
    async def discover_vdp_urls(self, limit: Optional[int] = None) -> List[str]:
        """
        Discover VDP URLs from sitemap or inventory pages

        Args:
            limit: Maximum number of VDPs to discover (for testing)

        Returns:
            List of VDP URLs (new vehicles only)
        """
        pass

    @abstractmethod
    async def scrape_vdp(self, vdp_url: str) -> ScrapedVehicle:
        """
        Scrape a single VDP (Vehicle Detail Page)

        Args:
            vdp_url: URL of the VDP to scrape

        Returns:
            ScrapedVehicle object with extracted data
        """
        pass

    async def scrape_all(self, limit: Optional[int] = None) -> List[ScrapedVehicle]:
        """
        Complete scraping workflow: discover VDPs → scrape each VDP

        Args:
            limit: Maximum number of VDPs to process

        Returns:
            List of ScrapedVehicle objects
        """
        logger.info(f"Starting scrape for {self.url} (limit: {limit})")

        # Discover VDP URLs
        vdp_urls = await self.discover_vdp_urls(limit=limit)
        logger.info(f"Discovered {len(vdp_urls)} VDP URLs")

        # Scrape each VDP
        vehicles = []
        for idx, vdp_url in enumerate(vdp_urls, 1):
            try:
                logger.info(f"Scraping VDP {idx}/{len(vdp_urls)}: {vdp_url}")
                vehicle = await self.scrape_vdp(vdp_url)
                vehicles.append(vehicle)
            except Exception as e:
                logger.error(f"Error scraping {vdp_url}: {e}")
                continue

        logger.info(f"Successfully scraped {len(vehicles)}/{len(vdp_urls)} vehicles")
        return vehicles

    def _is_new_vehicle_url(self, url: str) -> bool:
        """
        Check if URL is for a new vehicle (not used/CPO)

        Override this in platform-specific scrapers if needed
        """
        url_lower = url.lower()
        return (
            'new' in url_lower
            and 'used' not in url_lower
            and 'certified' not in url_lower
            and 'cpo' not in url_lower
            and 'pre-owned' not in url_lower
        )
