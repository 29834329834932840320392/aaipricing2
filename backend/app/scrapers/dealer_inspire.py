"""
Dealer Inspire platform scraper

Handles scraping for dealerships using the Dealer Inspire platform.
"""
from typing import List, Optional
import re
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from app.scrapers.base import BaseScraper, ScrapedVehicle
import logging

logger = logging.getLogger(__name__)


class DealerInspireScraper(BaseScraper):
    """
    Scraper for Dealer Inspire platform

    Dealer Inspire characteristics:
    - Sitemap typically at: /dealer-inspire-inventory/inventory_sitemap
    - VDP URL pattern: /inventory/new-YEAR-MAKE-MODEL-TRIM-LOCATION-VIN/
    - Uses structured data and clean HTML
    """

    async def discover_vdp_urls(self, limit: Optional[int] = None) -> List[str]:
        """
        Discover VDP URLs from Dealer Inspire sitemap

        Args:
            limit: Maximum number of VDPs to discover

        Returns:
            List of new vehicle VDP URLs
        """
        logger.info(f"Fetching Dealer Inspire sitemap: {self.url}")

        # Navigate to sitemap
        await self.page.goto(self.url, wait_until="networkidle")

        # Get page content (XML sitemap)
        content = await self.page.content()

        # Parse XML sitemap
        try:
            root = ET.fromstring(content)

            # Handle XML namespaces (Dealer Inspire uses standard sitemap namespace)
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            url_elements = root.findall('.//ns:loc', namespaces)

            # Fallback if namespace not found
            if not url_elements:
                url_elements = root.findall('.//loc')

            vdp_urls = []
            for url_elem in url_elements:
                url = url_elem.text

                if url and self._is_new_nissan_vdp(url):
                    vdp_urls.append(url)

                    # Apply limit if specified
                    if limit and len(vdp_urls) >= limit:
                        break

            logger.info(f"Found {len(vdp_urls)} new Nissan VDP URLs in sitemap")
            return vdp_urls

        except ET.ParseError as e:
            logger.error(f"Failed to parse sitemap XML: {e}")
            return []

    def _is_new_nissan_vdp(self, url: str) -> bool:
        """
        Check if URL is a new Nissan VDP (Dealer Inspire specific)

        Dealer Inspire VDP pattern: /inventory/new-YEAR-MAKE-MODEL-...
        """
        url_lower = url.lower()

        # Must be a new vehicle
        if not self._is_new_vehicle_url(url):
            return False

        # Must contain 'nissan' (case-insensitive)
        if 'nissan' not in url_lower:
            return False

        # Should match Dealer Inspire VDP pattern
        # Pattern: /inventory/new-YEAR-MAKE-MODEL-TRIM-LOCATION-VIN/
        if '/inventory/new-' in url_lower and re.search(r'/inventory/new-\d{4}-', url_lower):
            return True

        return False

    async def scrape_vdp(self, vdp_url: str) -> ScrapedVehicle:
        """
        Scrape a single Dealer Inspire VDP

        Args:
            vdp_url: URL of the VDP to scrape

        Returns:
            ScrapedVehicle with raw HTML (AI will extract structured data)
        """
        logger.info(f"Scraping Dealer Inspire VDP: {vdp_url}")

        # Navigate to VDP
        await self.page.goto(vdp_url, wait_until="networkidle")

        # Wait for key elements to load (Dealer Inspire typically uses these)
        try:
            # Wait for price container (adjust selector if needed)
            await self.page.wait_for_selector('.pricing-container, .price-container, [class*="price"]', timeout=5000)
        except Exception:
            logger.warning(f"Price container not found on {vdp_url}, continuing anyway")

        # Get full page HTML
        html_content = await self.page.content()

        # Extract basic info from URL (Dealer Inspire encodes it in the URL)
        url_info = self._extract_info_from_url(vdp_url)

        # Create ScrapedVehicle with URL-extracted data and full HTML for AI processing
        vehicle = ScrapedVehicle(
            vin=url_info.get('vin'),
            year=url_info.get('year', 0),
            make=url_info.get('make', 'Nissan'),
            model=url_info.get('model', 'Unknown'),
            trim=url_info.get('trim'),
            msrp=None,  # AI will extract from HTML
            sale_price=None,  # AI will extract from HTML
            vdp_url=vdp_url,
            raw_html=html_content,
        )

        logger.info(f"Scraped VDP: {url_info.get('year')} {url_info.get('make')} {url_info.get('model')}")
        return vehicle

    def _extract_info_from_url(self, url: str) -> dict:
        """
        Extract vehicle info from Dealer Inspire URL pattern

        URL pattern: /inventory/new-YEAR-MAKE-MODEL-TRIM-LOCATION-VIN/
        Example: /inventory/new-2026-nissan-rogue-s-san-antonio-tx-5n1bt3aa1tc768626/
        """
        # Extract path from URL
        path = url.split('/inventory/')[-1]
        parts = path.strip('/').split('-')

        info = {}

        try:
            # Skip 'new' prefix
            if parts[0].lower() == 'new':
                parts = parts[1:]

            # Year (first part, should be 4 digits)
            if parts and re.match(r'\d{4}', parts[0]):
                info['year'] = int(parts[0])
                parts = parts[1:]

            # Make (usually 'nissan')
            if parts:
                info['make'] = parts[0].capitalize()
                parts = parts[1:]

            # Model (next part before trim)
            if parts:
                info['model'] = parts[0].capitalize()
                parts = parts[1:]

            # VIN (last part, 17 characters)
            if parts:
                vin_candidate = parts[-1].upper()
                if len(vin_candidate) == 17:
                    info['vin'] = vin_candidate
                    parts = parts[:-1]

            # Trim (everything between model and location/VIN)
            # Skip location parts (city, state abbreviations)
            trim_parts = []
            for part in parts:
                # Skip common location indicators
                if len(part) == 2 and part.isupper():  # State abbrev
                    break
                if part.lower() in ['san', 'antonio', 'tx', 'texas']:
                    break
                trim_parts.append(part.upper())

            if trim_parts:
                info['trim'] = ' '.join(trim_parts)

        except (IndexError, ValueError) as e:
            logger.warning(f"Error parsing URL {url}: {e}")

        return info
