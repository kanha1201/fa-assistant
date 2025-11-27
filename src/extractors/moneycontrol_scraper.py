"""Scraper for MoneyControl financial data."""
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from src.utils import logger, settings


class MoneyControlScraper:
    """Scrape financial data from MoneyControl."""
    
    def __init__(self):
        """Initialize MoneyControl scraper."""
        self.base_url = "https://www.moneycontrol.com"
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": settings.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        })
        self.logger = logger
    
    def _make_request(self, url: str, retries: int = None) -> requests.Response:
        """Make HTTP request with retries."""
        retries = retries or settings.retry_attempts
        
        for attempt in range(retries):
            try:
                response = self.session.get(url, timeout=settings.request_timeout)
                response.raise_for_status()
                time.sleep(settings.delay_between_requests)
                return response
            except requests.RequestException as e:
                if attempt == retries - 1:
                    raise
                self.logger.warning(f"Request failed (attempt {attempt + 1}/{retries}): {e}")
                time.sleep(2 ** attempt)
        
        raise Exception("Max retries exceeded")
    
    def scrape_company_data(self, company_url: str) -> Dict:
        """Scrape company data from MoneyControl."""
        self.logger.info(f"Scraping company data from {company_url}")
        
        response = self._make_request(company_url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        data = {
            "source_url": company_url,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Extract company name
        name_elem = soup.find("h1", class_=re.compile(r"company|name|title", re.I))
        if not name_elem:
            name_elem = soup.find("h1")
        if name_elem:
            data["company_name"] = name_elem.get_text(strip=True)
        
        # Extract current price and key metrics
        data["price_info"] = self._extract_price_info(soup)
        
        # Extract key ratios
        data["ratios"] = self._extract_ratios(soup)
        
        # Extract company overview
        data["overview"] = self._extract_overview(soup)
        
        # Extract financials
        data["financials"] = self._extract_financials(soup)
        
        # Extract news/announcements
        data["news"] = self._extract_news(soup)
        
        # Extract full text for RAG
        data["full_text"] = self._extract_full_text(soup)
        
        return data
    
    def _extract_price_info(self, soup: BeautifulSoup) -> Dict:
        """Extract current price and related information."""
        price_info = {}
        
        # Look for price elements
        price_elem = soup.find(class_=re.compile(r"price|current|last", re.I))
        if not price_elem:
            price_elem = soup.find(string=re.compile(r"₹|Rs\.|INR", re.I))
            if price_elem:
                price_elem = price_elem.find_parent()
        
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price_match = re.search(r"₹?\s*([\d,]+\.?\d*)", price_text)
            if price_match:
                price_info["current_price"] = price_match.group(1).replace(",", "")
        
        # Extract change percentage
        change_elem = soup.find(class_=re.compile(r"change|percent|gain|loss", re.I))
        if change_elem:
            change_text = change_elem.get_text(strip=True)
            change_match = re.search(r"([+-]?\d+\.?\d*)%", change_text)
            if change_match:
                price_info["change_percent"] = change_match.group(1)
        
        # Extract market cap, volume, etc.
        metric_labels = ["Market Cap", "Volume", "52 Week High", "52 Week Low", "Book Value"]
        for label in metric_labels:
            elem = soup.find(string=re.compile(label, re.I))
            if elem:
                parent = elem.find_parent()
                if parent:
                    value_elem = parent.find_next(string=True)
                    if value_elem:
                        price_info[label.lower().replace(" ", "_")] = value_elem.strip()
        
        return price_info
    
    def _extract_ratios(self, soup: BeautifulSoup) -> Dict:
        """Extract financial ratios."""
        ratios = {}
        
        # Find ratios section or table
        ratios_section = soup.find(string=re.compile(r"ratios?|valuation", re.I))
        if ratios_section:
            section = ratios_section.find_parent(["section", "div", "table"])
            if section:
                rows = section.find_all("tr")
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if len(cells) >= 2:
                        ratio_name = cells[0].get_text(strip=True)
                        ratio_value = cells[1].get_text(strip=True)
                        if ratio_name and ratio_value:
                            ratios[ratio_name] = ratio_value
        
        # Also look for specific ratio patterns
        ratio_patterns = {
            "P/E": r"P/E|PE Ratio",
            "P/B": r"P/B|PB Ratio",
            "Debt/Equity": r"Debt.*Equity|D/E",
            "ROE": r"ROE|Return.*Equity",
            "ROCE": r"ROCE|Return.*Capital"
        }
        
        for ratio_name, pattern in ratio_patterns.items():
            elem = soup.find(string=re.compile(pattern, re.I))
            if elem:
                parent = elem.find_parent()
                if parent:
                    value_elem = parent.find_next(string=True)
                    if value_elem:
                        ratios[ratio_name] = value_elem.strip()
        
        return ratios
    
    def _extract_overview(self, soup: BeautifulSoup) -> Dict:
        """Extract company overview information."""
        overview = {}
        
        # Look for overview section
        overview_section = soup.find(string=re.compile(r"overview|about|company.*info", re.I))
        if overview_section:
            section = overview_section.find_parent(["section", "div"])
            if section:
                # Extract text content
                overview["description"] = section.get_text(separator="\n", strip=True)
        
        # Extract key information
        info_labels = ["Industry", "Sector", "BSE Code", "NSE Code", "ISIN"]
        for label in info_labels:
            elem = soup.find(string=re.compile(label, re.I))
            if elem:
                parent = elem.find_parent()
                if parent:
                    value_elem = parent.find_next(string=True)
                    if value_elem:
                        overview[label.lower().replace(" ", "_")] = value_elem.strip()
        
        return overview
    
    def _extract_financials(self, soup: BeautifulSoup) -> Dict:
        """Extract financial statement data."""
        financials = {}
        
        # Find financials section
        financials_section = soup.find(string=re.compile(r"financials?|results", re.I))
        if financials_section:
            section = financials_section.find_parent(["section", "div"])
            if section:
                # Look for tables
                tables = section.find_all("table")
                for table in tables:
                    table_name = ""
                    header = table.find("thead") or table.find("tr")
                    if header:
                        header_text = header.get_text(strip=True)
                        if "profit" in header_text.lower() or "loss" in header_text.lower():
                            table_name = "profit_loss"
                        elif "balance" in header_text.lower():
                            table_name = "balance_sheet"
                        elif "cash" in header_text.lower() and "flow" in header_text.lower():
                            table_name = "cash_flow"
                    
                    if table_name:
                        rows = table.find_all("tr")[1:]
                        table_data = []
                        headers = [th.get_text(strip=True) for th in header.find_all(["th", "td"])]
                        
                        for row in rows:
                            cells = row.find_all(["td", "th"])
                            if cells:
                                row_data = {}
                                for i, cell in enumerate(cells):
                                    key = headers[i] if i < len(headers) else f"col_{i}"
                                    row_data[key] = cell.get_text(strip=True)
                                if row_data:
                                    table_data.append(row_data)
                        
                        if table_data:
                            financials[table_name] = table_data
        
        return financials
    
    def _extract_news(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract news and announcements."""
        news_items = []
        
        # Find news section
        news_section = soup.find(string=re.compile(r"news|announcements?", re.I))
        if news_section:
            section = news_section.find_parent(["section", "div"])
            if section:
                news_links = section.find_all("a", href=re.compile(r"news|announcement", re.I))
                for link in news_links[:10]:  # Limit to 10 most recent
                    news_items.append({
                        "title": link.get_text(strip=True),
                        "url": link.get("href", ""),
                        "date": ""
                    })
        
        return news_items
    
    def _extract_full_text(self, soup: BeautifulSoup) -> str:
        """Extract all readable text content for RAG."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator="\n", strip=True)
        
        # Clean up multiple newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        return text


def scrape_eternal_moneycontrol() -> Dict:
    """Scrape Eternal data from MoneyControl."""
    url = "https://www.moneycontrol.com/india/stockpricequote/online-services/eternal/Z"
    scraper = MoneyControlScraper()
    return scraper.scrape_company_data(url)


if __name__ == "__main__":
    # Test scraping
    logger.info("Scraping Eternal data from MoneyControl...")
    data = scrape_eternal_moneycontrol()
    
    output_path = Path(settings.processed_data_path) / "moneycontrol_eternal.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Data saved to {output_path}")


