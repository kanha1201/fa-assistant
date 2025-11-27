"""Test LLM service."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import LLMService
from src.utils import logger


def test_quarterly_summary():
    """Test quarterly summary."""
    logger.info("Testing quarterly summary...")
    service = LLMService()
    result = service.get_quarterly_summary("ETERNAL")
    
    if "error" in result:
        logger.error(f"✗ Failed: {result['error']}")
        return False
    
    logger.info(f"✓ Success")
    logger.info(f"Summary: {result.get('summary', '')[:200]}...")
    return True


def test_bull_bear_case():
    """Test bull/bear case."""
    logger.info("Testing bull/bear case...")
    service = LLMService()
    result = service.get_bull_bear_case("ETERNAL")
    
    if "error" in result:
        logger.error(f"✗ Failed: {result['error']}")
        return False
    
    logger.info(f"✓ Success")
    logger.info(f"Bull case points: {len(result.get('bull_case', []))}")
    logger.info(f"Bear case points: {len(result.get('bear_case', []))}")
    return True


def test_red_flags():
    """Test red flags."""
    logger.info("Testing red flags...")
    service = LLMService()
    result = service.get_red_flags("ETERNAL")
    
    if "error" in result:
        logger.error(f"✗ Failed: {result['error']}")
        return False
    
    logger.info(f"✓ Success")
    logger.info(f"Red flags found: {len(result.get('red_flags', []))}")
    return True


def test_benchmark():
    """Test benchmark."""
    logger.info("Testing benchmark...")
    service = LLMService()
    result = service.get_benchmark("ETERNAL", "pe_ratio")
    
    if "error" in result:
        logger.warning(f"⚠ Benchmark test: {result['error']}")
        return False
    
    logger.info(f"✓ Success")
    logger.info(f"Comparison: {result.get('comparison', '')[:200]}...")
    return True


def test_general_query():
    """Test general query."""
    logger.info("Testing general query...")
    service = LLMService()
    result = service.answer_query("ETERNAL", "What is the current revenue growth?")
    
    if "error" in result:
        logger.error(f"✗ Failed: {result['error']}")
        return False
    
    logger.info(f"✓ Success")
    logger.info(f"Answer: {result.get('answer', '')[:200]}...")
    return True


if __name__ == "__main__":
    logger.info("🧪 Testing LLM Service")
    logger.info("=" * 80)
    
    # Check if API key is set
    import os
    if not os.getenv("GEMINI_API_KEY"):
        logger.error("✗ GEMINI_API_KEY not set. Please set it in .env file or environment.")
        sys.exit(1)
    
    results = {
        "Quarterly Summary": test_quarterly_summary(),
        "Bull/Bear Case": test_bull_bear_case(),
        "Red Flags": test_red_flags(),
        "Benchmark": test_benchmark(),
        "General Query": test_general_query(),
    }
    
    logger.info("=" * 80)
    logger.info("TEST RESULTS")
    logger.info("=" * 80)
    
    for name, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        logger.info(f"{name:20} : {status}")
    
    passed = sum(results.values())
    total = len(results)
    logger.info(f"\nOverall: {passed}/{total} tests passed")


