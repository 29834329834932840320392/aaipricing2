"""
Web scraping module for extracting vehicle data from competitor sitemaps and VDPs
"""
import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
from typing import List, Dict, Optional
import time
import re
from urllib.parse import urlparse


class VehicleScraper:
    def __init__(self, vdp_limit: Optional[int] = None):
        """
        Initialize the scraper

        Args:
            vdp_limit: Maximum number of VDPs to process per sitemap (None for unlimited)
        """
        self.vdp_limit = vdp_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })

    def extract_competitor_name(self, url: str) -> str:
        """Extract competitor name from URL"""
        domain = urlparse(url).netloc

        if 'gunnnissan' in domain:
            return 'Gunn Nissan'
        elif 'ingrampark' in domain:
            return 'Ingram Park Nissan'
        elif 'nissanboerne' in domain or 'boerne' in domain:
            return 'Nissan of Boerne'
        elif 'championnissan' in domain:
            return 'Champion Nissan (New Braunfels)'
        else:
            return domain

    def parse_sitemap(self, sitemap_url: str) -> List[str]:
        """
        Parse XML sitemap and extract new Nissan vehicle VDP URLs

        Args:
            sitemap_url: URL of the XML sitemap

        Returns:
            List of VDP URLs
        """
        try:
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            # Handle namespaces
            namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            urls = root.findall('.//ns:loc', namespaces)

            # If no namespace found, try without
            if not urls:
                urls = root.findall('.//loc')

            # Filter for new vehicle VDPs (looking for keywords like 'new', 'nissan', 'inventory', etc.)
            vdp_urls = []
            for url_elem in urls:
                url = url_elem.text
                if url and self._is_new_nissan_vdp(url):
                    vdp_urls.append(url)

                    # Apply VDP limit if set
                    if self.vdp_limit and len(vdp_urls) >= self.vdp_limit:
                        break

            return vdp_urls

        except Exception as e:
            raise Exception(f"Failed to parse sitemap {sitemap_url}: {str(e)}")

    def _is_new_nissan_vdp(self, url: str) -> bool:
        """Check if URL is likely a new Nissan vehicle detail page"""
        url_lower = url.lower()

        # Must contain 'new' and 'nissan'
        has_new = 'new' in url_lower or '/n/' in url_lower
        has_nissan = 'nissan' in url_lower

        # Exclude non-VDP pages
        exclude_terms = [
            'specials', 'service', 'parts', 'about', 'contact',
            'hours', 'staff', 'blog', 'news', 'reviews', 'directions',
            'finance', 'trade', 'sitemap', 'search', 'inventory/new',
            'showroom', 'certified', 'used', 'pre-owned'
        ]

        # Check for VDP indicators (VIN patterns, detail, viewdetails, etc.)
        vdp_indicators = [
            r'\d{17}',  # VIN pattern (17 alphanumeric characters)
            'detail',
            'viewdetail',
            '/auto/',
            '/vehicle/',
            '/inventory/new-\d{4}',
        ]

        has_vin_or_detail = any(re.search(pattern, url_lower) for pattern in vdp_indicators)
        has_exclude = any(term in url_lower for term in exclude_terms)

        return has_new and has_nissan and has_vin_or_detail and not has_exclude

    def scrape_vdp(self, url: str) -> Dict[str, str]:
        """
        Scrape a vehicle detail page and extract relevant HTML sections

        Args:
            url: VDP URL to scrape

        Returns:
            Dictionary containing competitor name, URL, and HTML content
        """
        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract relevant HTML sections for AI processing
            # Look for sections that typically contain vehicle info and pricing
            relevant_sections = []

            # Try to find price-related sections
            price_containers = soup.find_all(['div', 'section', 'span'],
                                            class_=re.compile(r'price|pricing|cost|msrp|sale|offer|payment', re.I))

            # Try to find vehicle info sections
            info_containers = soup.find_all(['div', 'section', 'table'],
                                           class_=re.compile(r'vehicle|details|specs|info|vin', re.I))

            # Combine and get text
            all_containers = price_containers + info_containers

            # If we found specific containers, use those
            if all_containers:
                html_content = '\n'.join([str(container) for container in all_containers[:10]])  # Limit to first 10
            else:
                # Fall back to body content (limited)
                body = soup.find('body')
                if body:
                    html_content = str(body)[:20000]  # Limit to first 20k characters
                else:
                    html_content = str(soup)[:20000]

            competitor_name = self.extract_competitor_name(url)

            return {
                'competitor': competitor_name,
                'url': url,
                'html_content': html_content,
                'page_title': soup.title.string if soup.title else '',
            }

        except Exception as e:
            raise Exception(f"Failed to scrape VDP {url}: {str(e)}")

    def retry_request(self, func, *args, max_retries=3, **kwargs):
        """Retry a function with exponential backoff"""
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                time.sleep(wait_time)
