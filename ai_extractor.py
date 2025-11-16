"""
OpenAI integration for intelligent vehicle data extraction from HTML
"""
from openai import OpenAI
import json
from typing import Dict, Optional
import re


class AIVehicleExtractor:
    def __init__(self, api_key: str):
        """
        Initialize the AI extractor

        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)

    def extract_vehicle_data(self, html_content: str, url: str, page_title: str = '') -> Dict[str, str]:
        """
        Use OpenAI to extract vehicle data from HTML content

        Args:
            html_content: HTML content from the VDP
            url: URL of the VDP (for context)
            page_title: Page title (for additional context)

        Returns:
            Dictionary containing extracted vehicle data
        """
        # Truncate HTML if too long (GPT-4 context limit consideration)
        max_html_length = 15000
        if len(html_content) > max_html_length:
            html_content = html_content[:max_html_length] + "\n...[truncated]"

        prompt = f"""You are a vehicle data extraction expert. Extract the following information from this vehicle detail page HTML:

URL: {url}
Page Title: {page_title}

Required fields:
1. VIN (Vehicle Identification Number - exactly 17 characters)
2. Year (4-digit year, e.g., 2024, 2025)
3. Make (should be "Nissan")
4. Model (e.g., Altima, Rogue, Sentra, Pathfinder, Murano, etc.)
5. Trim (e.g., SV, SL, Platinum, SR, etc.)
6. MSRP (Manufacturer's Suggested Retail Price - the original sticker price)
7. Sale Price (The final customer price after all discounts, incentives, and dealer adjustments)

IMPORTANT PRICING NOTES:
- Different dealerships use different labels for the final price: "Sale Price", "Our Price", "Your Price", "One Simple Price", "Dealer Price", "Internet Price", etc.
- The MSRP is typically labeled as "MSRP", "Sticker Price", or "Retail Price"
- The Sale Price is the LOWEST price shown that represents what the customer actually pays
- Ignore monthly payment amounts - we need the total vehicle price
- Return prices as numbers only (no dollar signs, commas, or "Price Available on Request")
- If a price is not found, return "Not Available"

Return ONLY a valid JSON object with these exact keys (no markdown, no code blocks, no explanations):
{{"vin": "", "year": "", "make": "", "model": "", "trim": "", "msrp": "", "sale_price": ""}}

HTML Content:
{html_content}
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Using mini for cost efficiency
                messages=[
                    {"role": "system", "content": "You are a data extraction expert. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,  # Low temperature for consistent extraction
                max_tokens=500
            )

            # Extract the response
            content = response.choices[0].message.content.strip()

            # Remove markdown code blocks if present
            content = re.sub(r'^```json?\s*', '', content)
            content = re.sub(r'\s*```$', '', content)

            # Parse JSON
            data = json.loads(content)

            # Validate and clean the data
            cleaned_data = {
                'vin': self._clean_vin(data.get('vin', '')),
                'year': self._clean_year(data.get('year', '')),
                'make': data.get('make', 'Nissan').strip(),
                'model': data.get('model', 'Not Available').strip(),
                'trim': data.get('trim', 'Not Available').strip(),
                'msrp': self._clean_price(data.get('msrp', '')),
                'sale_price': self._clean_price(data.get('sale_price', ''))
            }

            return cleaned_data

        except json.JSONDecodeError as e:
            # If JSON parsing fails, try to extract data from the response text
            print(f"JSON decode error: {e}. Response: {content}")
            return self._fallback_extraction(content)
        except Exception as e:
            print(f"AI extraction error: {e}")
            return {
                'vin': 'Not Available',
                'year': 'Not Available',
                'make': 'Nissan',
                'model': 'Not Available',
                'trim': 'Not Available',
                'msrp': 'Not Available',
                'sale_price': 'Not Available'
            }

    def _clean_vin(self, vin: str) -> str:
        """Clean and validate VIN"""
        vin = re.sub(r'[^A-Z0-9]', '', vin.upper())
        if len(vin) == 17:
            return vin
        return 'Not Available'

    def _clean_year(self, year: str) -> str:
        """Clean and validate year"""
        year_match = re.search(r'(20\d{2})', str(year))
        if year_match:
            return year_match.group(1)
        return 'Not Available'

    def _clean_price(self, price: str) -> str:
        """Clean and validate price"""
        if not price or price.lower() in ['not available', 'n/a', 'null', 'none']:
            return 'Not Available'

        # Remove all non-numeric characters except decimal point
        price_str = re.sub(r'[^\d.]', '', str(price))

        if price_str and price_str.replace('.', '').isdigit():
            # Convert to float and back to remove unnecessary decimals
            try:
                price_float = float(price_str)
                if price_float > 0:
                    return f"{price_float:.2f}"
            except ValueError:
                pass

        return 'Not Available'

    def _fallback_extraction(self, content: str) -> Dict[str, str]:
        """Fallback extraction if JSON parsing fails"""
        # Try to find key-value pairs in the response
        data = {
            'vin': 'Not Available',
            'year': 'Not Available',
            'make': 'Nissan',
            'model': 'Not Available',
            'trim': 'Not Available',
            'msrp': 'Not Available',
            'sale_price': 'Not Available'
        }

        # Try to extract VIN
        vin_match = re.search(r'[A-Z0-9]{17}', content)
        if vin_match:
            data['vin'] = vin_match.group(0)

        # Try to extract year
        year_match = re.search(r'20\d{2}', content)
        if year_match:
            data['year'] = year_match.group(0)

        return data
