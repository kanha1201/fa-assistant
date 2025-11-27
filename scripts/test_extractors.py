"""Test individual extractors."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.extractors import (
    extract_eternal_q2_report,
    scrape_eternal_data,
    scrape_sector_data,
    scrape_eternal_moneycontrol,
    scrape_zomato_groww
)
from src.utils import logger


def test_pdf_extractor():
    """Test PDF extractor."""
    logger.info("Testing PDF extractor...")
    try:
        result = extract_eternal_q2_report()
        logger.info(f"✓ PDF extraction successful")
        logger.info(f"  - Text length: {len(result.get('text', ''))} characters")
        logger.info(f"  - Total pages: {result.get('metadata', {}).get('total_pages', 0)}")
        logger.info(f"  - Total images: {result.get('metadata', {}).get('total_images', 0)}")
        return True
    except Exception as e:
        logger.error(f"✗ PDF extraction failed: {e}", exc_info=True)
        return False


def test_screener_scraper():
    """Test Screener scraper."""
    logger.info("Testing Screener scraper...")
    try:
        result = scrape_eternal_data()
        logger.info(f"✓ Screener scraping successful")
        logger.info(f"  - Company name: {result.get('company_name', 'N/A')}")
        logger.info(f"  - Key metrics: {len(result.get('key_metrics', {}))} metrics")
        logger.info(f"  - Text length: {len(result.get('full_text', ''))} characters")
        return True
    except Exception as e:
        logger.error(f"✗ Screener scraping failed: {e}", exc_info=True)
        return False


def test_moneycontrol_scraper():
    """Test MoneyControl scraper."""
    logger.info("Testing MoneyControl scraper...")
    try:
        result = scrape_eternal_moneycontrol()
        logger.info(f"✓ MoneyControl scraping successful")
        logger.info(f"  - Company name: {result.get('company_name', 'N/A')}")
        logger.info(f"  - Price info: {result.get('price_info', {})}")
        logger.info(f"  - Text length: {len(result.get('full_text', ''))} characters")
        return True
    except Exception as e:
        logger.error(f"✗ MoneyControl scraping failed: {e}", exc_info=True)
        return False


def test_groww_scraper():
    """Test Groww scraper."""
    logger.info("Testing Groww scraper...")
    try:
        result = scrape_zomato_groww()
        logger.info(f"✓ Groww scraping successful")
        logger.info(f"  - Stock name: {result.get('stock_name', 'N/A')}")
        logger.info(f"  - Price info: {result.get('price_info', {})}")
        logger.info(f"  - Text length: {len(result.get('full_text', ''))} characters")
        return True
    except Exception as e:
        logger.error(f"✗ Groww scraping failed: {e}", exc_info=True)
        return False


def test_sector_scraper():
    """Test sector scraper."""
    logger.info("Testing sector scraper...")
    try:
        result = scrape_sector_data()
        logger.info(f"✓ Sector scraping successful")
        logger.info(f"  - Sector name: {result.get('sector_name', 'N/A')}")
        logger.info(f"  - Companies found: {len(result.get('companies', []))}")
        logger.info(f"  - Text length: {len(result.get('full_text', ''))} characters")
        return True
    except Exception as e:
        logger.error(f"✗ Sector scraping failed: {e}", exc_info=True)
        return False


if __name__ == "__main__":
    logger.info("🧪 Testing Data Extractors")
    logger.info("=" * 80)
    
    results = {
        "PDF": test_pdf_extractor(),
        "Screener": test_screener_scraper(),
        "MoneyControl": test_moneycontrol_scraper(),
        "Groww": test_groww_scraper(),
        "Sector": test_sector_scraper(),
    }
    
    logger.info("=" * 80)
    logger.info("TEST RESULTS")
    logger.info("=" * 80)
    
    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{name:15} : {status}")
    
    passed = sum(results.values())
    total = len(results)
    logger.info(f"\nOverall: {passed}/{total} tests passed")


