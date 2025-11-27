"""Scraper for Screener.in financial data."""
import json
import re
import time
from pathlib import Path
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from src.utils import logger, settings


class ScreenerScraper:
    """Scrape financial data from Screener.in."""
    
    def __init__(self):
        """Initialize Screener scraper."""
        self.base_url = "https://www.screener.in"
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
    
    def scrape_company_data(self, company_symbol: str) -> Dict:
        """Scrape company financial data from Screener.in."""
        url = f"{self.base_url}/company/{company_symbol}/consolidated/"
        self.logger.info(f"Scraping company data from {url}")
        
        response = self._make_request(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        data = {
            "company_symbol": company_symbol,
            "source_url": url,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Extract company name
        name_elem = soup.find("h1", class_="company-name")
        if name_elem:
            data["company_name"] = name_elem.get_text(strip=True)
        
        # Extract key metrics from the overview section
        data["key_metrics"] = self._extract_key_metrics(soup)
        
        # Extract financial ratios
        data["ratios"] = self._extract_ratios(soup)
        
        # Extract profit & loss data
        data["profit_loss"] = self._extract_profit_loss(soup)
        
        # Extract balance sheet data
        data["balance_sheet"] = self._extract_balance_sheet(soup)
        
        # Extract cash flow data
        data["cash_flow"] = self._extract_cash_flow(soup)
        
        # Extract quarterly results
        data["quarterly_results"] = self._extract_quarterly_results(soup)
        
        # Extract all text content for RAG
        data["full_text"] = self._extract_full_text(soup)
        
        return data
    
    def _extract_key_metrics(self, soup: BeautifulSoup) -> Dict:
        """Extract key metrics from the overview section."""
        metrics = {}
        
        # Look for key-value pairs in various sections
        metric_sections = soup.find_all(["div", "section"], class_=re.compile(r"company|overview|metrics", re.I))
        
        for section in metric_sections:
            # Look for common metric patterns
            rows = section.find_all(["tr", "div"], class_=re.compile(r"row|metric|data", re.I))
            for row in rows:
                cells = row.find_all(["td", "div", "span"])
                if len(cells) >= 2:
                    key = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if key and value:
                        metrics[key] = value
        
        # Also try to find specific metrics by text
        metric_labels = [
            "Market Cap", "Current Price", "Book Value", "Dividend Yield",
            "ROCE", "ROE", "Face Value", "P/E", "P/B", "Debt to Equity"
        ]
        
        for label in metric_labels:
            elem = soup.find(string=re.compile(label, re.I))
            if elem:
                parent = elem.find_parent()
                if parent:
                    value_elem = parent.find_next(string=True)
                    if value_elem:
                        metrics[label] = value_elem.strip()
        
        return metrics
    
    def _extract_ratios(self, soup: BeautifulSoup) -> Dict:
        """Extract financial ratios."""
        ratios = {}
        
        # Find ratios section
        ratios_section = soup.find(string=re.compile(r"ratios?", re.I))
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
        
        return ratios
    
    def _extract_profit_loss(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract profit & loss statement data."""
        pl_data = []
        
        # Find P&L table
        pl_table = soup.find("table", id=re.compile(r"profit|pl", re.I))
        if not pl_table:
            # Try to find by text content
            pl_header = soup.find(string=re.compile(r"profit.*loss|p&l", re.I))
            if pl_header:
                pl_table = pl_header.find_parent("table")
        
        if pl_table:
            headers = []
            header_row = pl_table.find("thead") or pl_table.find("tr")
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
            
            rows = pl_table.find_all("tr")[1:]  # Skip header
            for row in rows:
                cells = row.find_all(["td", "th"])
                if cells:
                    row_data = {}
                    for i, cell in enumerate(cells):
                        key = headers[i] if i < len(headers) else f"col_{i}"
                        row_data[key] = cell.get_text(strip=True)
                    if row_data:
                        pl_data.append(row_data)
        
        return pl_data
    
    def _extract_balance_sheet(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract balance sheet data."""
        bs_data = []
        
        bs_table = soup.find("table", id=re.compile(r"balance|bs", re.I))
        if not bs_table:
            bs_header = soup.find(string=re.compile(r"balance.*sheet", re.I))
            if bs_header:
                bs_table = bs_header.find_parent("table")
        
        if bs_table:
            headers = []
            header_row = bs_table.find("thead") or bs_table.find("tr")
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
            
            rows = bs_table.find_all("tr")[1:]
            for row in rows:
                cells = row.find_all(["td", "th"])
                if cells:
                    row_data = {}
                    for i, cell in enumerate(cells):
                        key = headers[i] if i < len(headers) else f"col_{i}"
                        row_data[key] = cell.get_text(strip=True)
                    if row_data:
                        bs_data.append(row_data)
        
        return bs_data
    
    def _extract_cash_flow(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract cash flow statement data."""
        cf_data = []
        
        cf_table = soup.find("table", id=re.compile(r"cash.*flow|cf", re.I))
        if not cf_table:
            cf_header = soup.find(string=re.compile(r"cash.*flow", re.I))
            if cf_header:
                cf_table = cf_header.find_parent("table")
        
        if cf_table:
            headers = []
            header_row = cf_table.find("thead") or cf_table.find("tr")
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
            
            rows = cf_table.find_all("tr")[1:]
            for row in rows:
                cells = row.find_all(["td", "th"])
                if cells:
                    row_data = {}
                    for i, cell in enumerate(cells):
                        key = headers[i] if i < len(headers) else f"col_{i}"
                        row_data[key] = cell.get_text(strip=True)
                    if row_data:
                        cf_data.append(row_data)
        
        return cf_data
    
    def _extract_quarterly_results(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract quarterly results data."""
        quarterly_data = []
        
        # Find quarterly results table
        qr_table = soup.find("table", id=re.compile(r"quarterly|results", re.I))
        if not qr_table:
            qr_header = soup.find(string=re.compile(r"quarterly.*results", re.I))
            if qr_header:
                qr_table = qr_header.find_parent("table")
        
        if qr_table:
            headers = []
            header_row = qr_table.find("thead") or qr_table.find("tr")
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(["th", "td"])]
            
            rows = qr_table.find_all("tr")[1:]
            for row in rows:
                cells = row.find_all(["td", "th"])
                if cells:
                    row_data = {}
                    for i, cell in enumerate(cells):
                        key = headers[i] if i < len(headers) else f"col_{i}"
                        row_data[key] = cell.get_text(strip=True)
                    if row_data:
                        quarterly_data.append(row_data)
        
        return quarterly_data
    
    def _extract_full_text(self, soup: BeautifulSoup) -> str:
        """Extract all readable text content for RAG."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Get text
        text = soup.get_text(separator="\n", strip=True)
        
        # Clean up multiple newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        return text
    
    def scrape_sector_data(self, sector_url: str) -> Dict:
        """Scrape sector-level data and benchmarks."""
        self.logger.info(f"Scraping sector data from {sector_url}")
        
        response = self._make_request(sector_url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        data = {
            "source_url": sector_url,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        # Extract sector name
        title = soup.find("title")
        if title:
            data["sector_name"] = title.get_text(strip=True)
        
        # Extract list of companies in sector
        data["companies"] = self._extract_sector_companies(soup)
        
        # Extract sector benchmarks/metrics
        data["benchmarks"] = self._extract_sector_benchmarks(soup)
        
        # Extract full text for RAG
        data["full_text"] = self._extract_full_text(soup)
        
        return data
    
    def _extract_sector_companies(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract list of companies in the sector."""
        companies = []
        
        # Find company links/rows
        company_links = soup.find_all("a", href=re.compile(r"/company/[A-Z]+"))
        
        for link in company_links:
            company_symbol = link["href"].split("/")[-1]
            company_name = link.get_text(strip=True)
            companies.append({
                "symbol": company_symbol,
                "name": company_name,
                "url": f"{self.base_url}{link['href']}"
            })
        
        return companies
    
    def _extract_sector_benchmarks(self, soup: BeautifulSoup) -> Dict:
        """Extract sector-level benchmarks and averages."""
        benchmarks = {}
        
        # Look for benchmark tables or sections
        benchmark_sections = soup.find_all(["table", "div"], class_=re.compile(r"benchmark|average|sector", re.I))
        
        for section in benchmark_sections:
            rows = section.find_all("tr")
            for row in rows:
                cells = row.find_all(["td", "th"])
                if len(cells) >= 2:
                    metric = cells[0].get_text(strip=True)
                    value = cells[1].get_text(strip=True)
                    if metric and value:
                        benchmarks[metric] = value
        
        return benchmarks


def scrape_eternal_data() -> Dict:
    """Scrape Eternal company data from Screener.in."""
    scraper = ScreenerScraper()
    return scraper.scrape_company_data("ETERNAL")


def scrape_sector_data() -> Dict:
    """Scrape sector data."""
    url = "https://www.screener.in/market/IN02/IN0206/IN020603/IN020603004/"
    scraper = ScreenerScraper()
    return scraper.scrape_sector_data(url)


if __name__ == "__main__":
    # Test scraping
    logger.info("Scraping Eternal data from Screener.in...")
    eternal_data = scrape_eternal_data()
    
    output_path = Path(settings.processed_data_path) / "screener_eternal.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(eternal_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Data saved to {output_path}")
    
    logger.info("Scraping sector data...")
    sector_data = scrape_sector_data()
    
    sector_output_path = Path(settings.processed_data_path) / "screener_sector.json"
    with open(sector_output_path, "w", encoding="utf-8") as f:
        json.dump(sector_data, f, indent=2, ensure_ascii=False)
    logger.info(f"Sector data saved to {sector_output_path}")


