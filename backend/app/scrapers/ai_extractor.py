"""
AI-powered vehicle data extraction from HTML

Uses OpenAI to intelligently extract pricing and vehicle data from messy dealer HTML.
"""
from openai import AsyncOpenAI
from bs4 import BeautifulSoup
import json
import re
from typing import Optional
from app.scrapers.base import ScrapedVehicle
from app.models.system import SystemSettings
from app.auth.encryption import decrypt_api_key
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)


class AIVehicleExtractor:
    """
    Uses OpenAI to extract structured vehicle data from HTML

    Handles inconsistent price labeling across dealer websites.
    """

    def __init__(self, db: Session):
        """
        Initialize AI extractor

        Args:
            db: Database session to fetch OpenAI settings
        """
        self.db = db
        self.client: Optional[AsyncOpenAI] = None
        self.model = "gpt-5.4-mini-2026-03-17"  # Default
        self._initialize_client()

    def _initialize_client(self):
        """Initialize OpenAI client from system settings"""
        try:
            settings = self.db.query(SystemSettings).first()

            if settings is None or settings.openai_api_key_encrypted is None:
                logger.error("OpenAI API key not configured in system settings")
                return

            # Decrypt API key
            api_key = decrypt_api_key(settings.openai_api_key_encrypted)

            if api_key is None:
                logger.error("Failed to decrypt OpenAI API key")
                return

            # Initialize async client
            self.client = AsyncOpenAI(api_key=api_key)
            self.model = settings.openai_model

            logger.info(f"AI extractor initialized with model: {self.model}")

        except Exception as e:
            logger.error(f"Error initializing AI extractor: {e}")

    async def enhance_vehicle_data(self, vehicle: ScrapedVehicle) -> ScrapedVehicle:
        """
        Enhance scraped vehicle data using AI

        Args:
            vehicle: ScrapedVehicle with raw_html

        Returns:
            Enhanced ScrapedVehicle with extracted pricing data
        """
        if self.client is None:
            logger.warning("AI client not initialized, skipping AI extraction")
            return vehicle

        try:
            # Extract clean text from HTML for AI processing
            clean_text = self._extract_clean_text(vehicle.raw_html)

            # Use AI to extract pricing data
            ai_data = await self._extract_with_ai(
                html_text=clean_text,
                url=vehicle.vdp_url,
                known_year=vehicle.year,
                known_make=vehicle.make,
                known_model=vehicle.model,
            )

            # Enhance vehicle data with AI-extracted info
            if ai_data:
                # Override/fill in missing data
                vehicle.vin = ai_data.get('vin') or vehicle.vin
                vehicle.year = ai_data.get('year') or vehicle.year
                vehicle.make = ai_data.get('make') or vehicle.make
                vehicle.model = ai_data.get('model') or vehicle.model
                vehicle.trim = ai_data.get('trim') or vehicle.trim
                vehicle.msrp = ai_data.get('msrp')
                vehicle.sale_price = ai_data.get('sale_price')

            logger.info(f"AI enhanced vehicle: {vehicle.year} {vehicle.make} {vehicle.model} - MSRP: ${vehicle.msrp}, Sale: ${vehicle.sale_price}")

        except Exception as e:
            logger.error(f"AI extraction error for {vehicle.vdp_url}: {e}")

        return vehicle

    def _extract_clean_text(self, html: str, max_length: int = 10000) -> str:
        """
        Extract clean text from HTML for AI processing

        Args:
            html: Raw HTML
            max_length: Maximum text length to extract

        Returns:
            Cleaned text focusing on pricing and vehicle info
        """
        soup = BeautifulSoup(html, 'html.parser')

        # Remove script and style tags
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        # Focus on price-related sections
        price_sections = soup.find_all(
            ['div', 'section', 'span', 'p'],
            class_=re.compile(r'price|pricing|msrp|cost|sale|offer|payment|vehicle|details|specs', re.I)
        )

        if price_sections:
            # Concatenate text from relevant sections
            text = '\n'.join([section.get_text(separator=' ', strip=True) for section in price_sections])
        else:
            # Fallback to all text
            text = soup.get_text(separator=' ', strip=True)

        # Truncate if too long
        if len(text) > max_length:
            text = text[:max_length] + "...[truncated]"

        return text

    async def _extract_with_ai(
        self,
        html_text: str,
        url: str,
        known_year: Optional[int] = None,
        known_make: Optional[str] = None,
        known_model: Optional[str] = None,
    ) -> Optional[dict]:
        """
        Use OpenAI to extract vehicle data from HTML text

        Args:
            html_text: Cleaned text from HTML
            url: VDP URL for context
            known_year/make/model: Pre-extracted data from URL (for validation)

        Returns:
            Dictionary with extracted data
        """
        prompt = f"""Extract vehicle pricing and details from this dealership webpage.

URL: {url}
Known Info: {known_year} {known_make} {known_model}

Extract these fields:
1. VIN (17 characters)
2. Year (4 digits, e.g., 2026)
3. Make (e.g., Nissan)
4. Model (e.g., Rogue, Frontier, Pathfinder)
5. Trim (e.g., S, SV, SL, Pro-X, Platinum)
6. MSRP (Manufacturer Suggested Retail Price / Sticker Price)
7. Sale Price (final customer price - look for: "Sale Price", "Our Price", "Your Price", "Internet Price", "Dealer Price", "One Price", "Special Price")

CRITICAL RULES:
- MSRP is the original sticker price (higher price)
- Sale Price is the final price after discounts (lower price)
- IGNORE conditional prices (military, college grad, finance rebates, lease offers)
- Return prices as numbers only (no $ or commas)
- If a price is missing, return null
- If Sale Price = MSRP (no discount), that's ok - return both

Return ONLY valid JSON (no markdown, no explanations):
{{"vin": "...", "year": 2026, "make": "Nissan", "model": "...", "trim": "...", "msrp": 35000.00, "sale_price": 33000.00}}

Webpage Text:
{html_text}
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a vehicle data extraction expert. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
            )

            content = response.choices[0].message.content.strip()

            # Clean response (remove markdown code blocks if present)
            content = re.sub(r'^```json?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)

            # Parse JSON
            data = json.loads(content)

            # Clean and validate data
            cleaned = {
                'vin': self._clean_vin(data.get('vin')),
                'year': self._clean_year(data.get('year')),
                'make': str(data.get('make', '')).strip() or None,
                'model': str(data.get('model', '')).strip() or None,
                'trim': str(data.get('trim', '')).strip() or None,
                'msrp': self._clean_price(data.get('msrp')),
                'sale_price': self._clean_price(data.get('sale_price')),
            }

            return cleaned

        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}. Response: {content}")
            return None
        except Exception as e:
            logger.error(f"AI extraction error: {e}")
            return None

    def _clean_vin(self, vin) -> Optional[str]:
        """Clean and validate VIN"""
        if not vin:
            return None

        vin_clean = re.sub(r'[^A-Z0-9]', '', str(vin).upper())

        if len(vin_clean) == 17:
            return vin_clean

        return None

    def _clean_year(self, year) -> Optional[int]:
        """Clean and validate year"""
        if not year:
            return None

        # Extract 4-digit year
        year_match = re.search(r'(20\d{2})', str(year))

        if year_match:
            return int(year_match.group(1))

        # Try direct conversion
        try:
            year_int = int(year)
            if 2020 <= year_int <= 2030:
                return year_int
        except (ValueError, TypeError):
            pass

        return None

    def _clean_price(self, price) -> Optional[float]:
        """Clean and validate price"""
        if price is None or price == '':
            return None

        # Handle various formats
        if isinstance(price, (int, float)):
            return float(price) if price > 0 else None

        # Remove all non-numeric except decimal
        price_str = re.sub(r'[^\d.]', '', str(price))

        if not price_str:
            return None

        try:
            price_float = float(price_str)
            return price_float if price_float > 0 else None
        except ValueError:
            return None
