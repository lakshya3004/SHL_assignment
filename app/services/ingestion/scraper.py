import requests
import time
import random
from typing import List, Dict, Any, Optional
from bs4 import BeautifulSoup
from loguru import logger
from app.models.catalog_models import RawAssessment

class SHLScraper:
    """
    Scraper for the SHL Assessment Catalog.
    Implements polite scraping practices with retries and realistic headers.
    """
    
    BASE_URL = "https://www.shl.com"
    CATALOG_URL = f"{BASE_URL}/products/product-catalog/"
    
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": self.BASE_URL
        }

    def _get(self, url: str, retries: int = 3) -> Optional[str]:
        """Fetch URL with retry logic and random delays."""
        for attempt in range(retries):
            try:
                # Polite delay
                time.sleep(random.uniform(1, 3))
                
                response = self.session.get(url, headers=self.headers, timeout=15)
                response.raise_for_status()
                return response.text
            except requests.RequestException as e:
                logger.error(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == retries - 1:
                    return None
        return None

    def scrape_catalog_page(self, page_num: int = 1) -> List[RawAssessment]:
        """
        Scrapes a single page of the assessment catalog.
        The SHL catalog typically uses a table or grid structure.
        """
        url = self.CATALOG_URL if page_num == 1 else f"{self.CATALOG_URL}?p={page_num}"
        logger.info(f"Scraping catalog page {page_num}...")
        
        html = self._get(url)
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        assessments = []
        
        # Based on structure identified: grid with links to view/slug
        # We look for links within the product list container
        # Note: Selectors might need adjustment if structure changes
        catalog_items = soup.select("table tbody tr") or soup.select(".product-list-item")
        
        for item in catalog_items:
            try:
                link_tag = item.find("a", href=True)
                if not link_tag:
                    continue
                    
                name = link_tag.get_text(strip=True)
                path = link_tag['href']
                full_url = path if path.startswith("http") else f"{self.BASE_URL}{path}"
                
                # Extract simple metadata from sibling columns if in table
                cols = item.find_all("td")
                metadata = {}
                if len(cols) >= 4:
                    metadata["remote"] = "Yes" in cols[1].get_text()
                    metadata["adaptive"] = "Yes" in cols[2].get_text()
                    metadata["test_type"] = cols[3].get_text(strip=True)
                
                # We save the raw entry. Full page content scraping happens per-item.
                assessments.append(RawAssessment(
                    name=name,
                    url=full_url,
                    metadata=metadata
                ))
            except Exception as e:
                logger.warning(f"Failed to parse item: {e}")
                
        return assessments

    def scrape_assessment_details(self, assessment: RawAssessment) -> RawAssessment:
        """
        Navigates to the individual assessment page to extract the full description.
        """
        logger.info(f"Scraping details for: {assessment.name}")
        html = self._get(assessment.url)
        if html:
            assessment.raw_html = html
        return assessment

    def run_full_scrape(self, max_pages: int = 5) -> List[RawAssessment]:
        """
        Orchestrates the scraping of multiple pages and detail extraction.
        """
        all_raw_data = []
        
        for p in range(1, max_pages + 1):
            page_items = self.scrape_catalog_page(p)
            if not page_items:
                break
            all_raw_data.extend(page_items)
            
        # Optional: Scrape individual pages for descriptions
        # In a real production run, we might limit this or do it concurrently
        for item in all_raw_data:
            self.scrape_assessment_details(item)
            
        logger.info(f"Full scrape completed. Total items: {len(all_raw_data)}")
        return all_raw_data
