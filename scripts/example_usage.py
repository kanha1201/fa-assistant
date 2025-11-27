"""Example usage of LLM service."""
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.llm import LLMService
from src.utils import logger

# Make sure API key is set
if not os.getenv("GEMINI_API_KEY"):
    logger.error("Please set GEMINI_API_KEY environment variable")
    sys.exit(1)

service = LLMService()

# Example 1: Get quarterly summary
logger.info("=" * 80)
logger.info("Example 1: Quarterly Summary")
logger.info("=" * 80)
summary = service.get_quarterly_summary("ETERNAL")
print(f"\n{summary.get('summary', 'N/A')}\n")

# Example 2: Get bull/bear case
logger.info("=" * 80)
logger.info("Example 2: Bull vs Bear Case")
logger.info("=" * 80)
bull_bear = service.get_bull_bear_case("ETERNAL")
print("\nBULL CASE:")
for point in bull_bear.get('bull_case', [])[:3]:
    print(f"  • {point}")
print("\nBEAR CASE:")
for point in bull_bear.get('bear_case', [])[:3]:
    print(f"  • {point}\n")

# Example 3: Get red flags
logger.info("=" * 80)
logger.info("Example 3: Red Flags")
logger.info("=" * 80)
red_flags = service.get_red_flags("ETERNAL")
for flag in red_flags.get('red_flags', [])[:3]:
    severity = flag.get('severity', 'Unknown')
    desc = flag.get('description', 'N/A')
    print(f"[{severity}] {desc}\n")

# Example 4: Answer a query
logger.info("=" * 80)
logger.info("Example 4: General Query")
logger.info("=" * 80)
answer = service.answer_query("ETERNAL", "What is the company's revenue growth?")
print(f"\nQ: What is the company's revenue growth?")
print(f"A: {answer.get('answer', 'N/A')}\n")


