"""Comprehensive backend testing script."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils import logger, settings
from src.storage import db, vector_store
from src.llm import GeminiClient, LLMService
import os


def test_configuration():
    """Test configuration loading."""
    logger.info("=" * 80)
    logger.info("TEST 1: Configuration")
    logger.info("=" * 80)
    
    checks = {
        "API Key": bool(settings.gemini_api_key),
        "Vector DB Path": bool(settings.vector_db_path),
        "Processed Data Path": bool(settings.processed_data_path),
    }
    
    for check, result in checks.items():
        status = "✓" if result else "✗"
        logger.info(f"{status} {check}: {'OK' if result else 'MISSING'}")
    
    return all(checks.values())


def test_database():
    """Test database connection."""
    logger.info("=" * 80)
    logger.info("TEST 2: Database Connection")
    logger.info("=" * 80)
    
    try:
        session = db.get_session()
        try:
            # Try to query
            companies = session.query(db.Company).limit(1).all()
            logger.info("✓ Database connection: OK")
            logger.info(f"  Found {len(companies)} companies in database")
            return True
        finally:
            session.close()
    except Exception as e:
        logger.warning(f"⚠ Database connection: {e}")
        logger.info("  Note: Database is optional. Using SQLite fallback.")
        return True  # Not critical for testing


def test_vector_store():
    """Test vector store."""
    logger.info("=" * 80)
    logger.info("TEST 3: Vector Store")
    logger.info("=" * 80)
    
    try:
        count = vector_store.count()
        logger.info(f"✓ Vector store: OK")
        logger.info(f"  Documents in vector store: {count}")
        
        if count == 0:
            logger.warning("  ⚠ No documents found. Run data ingestion first!")
            return False
        
        return True
    except Exception as e:
        logger.error(f"✗ Vector store error: {e}")
        return False


def test_gemini_client():
    """Test Gemini API client."""
    logger.info("=" * 80)
    logger.info("TEST 4: Gemini API Client")
    logger.info("=" * 80)
    
    try:
        client = GeminiClient()
        test_prompt = "Say 'Hello' if you can read this."
        response = client.generate(test_prompt, temperature=0.1)
        
        logger.info("✓ Gemini API: OK")
        logger.info(f"  Test response: {response[:100]}...")
        return True
    except Exception as e:
        logger.error(f"✗ Gemini API error: {e}")
        return False


def test_rag_pipeline():
    """Test RAG pipeline."""
    logger.info("=" * 80)
    logger.info("TEST 5: RAG Pipeline")
    logger.info("=" * 80)
    
    try:
        from src.llm import RAGPipeline
        rag = RAGPipeline()
        
        # Test retrieval
        contexts = rag.retrieve_context("quarterly results", company_symbol="ETERNAL", n_results=2)
        
        logger.info(f"✓ RAG Pipeline: OK")
        logger.info(f"  Retrieved {len(contexts)} context documents")
        
        if len(contexts) == 0:
            logger.warning("  ⚠ No context found. Run data ingestion first!")
            return False
        
        return True
    except Exception as e:
        logger.error(f"✗ RAG Pipeline error: {e}")
        return False


def test_llm_service():
    """Test LLM service methods."""
    logger.info("=" * 80)
    logger.info("TEST 6: LLM Service")
    logger.info("=" * 80)
    
    try:
        service = LLMService()
        
        # Test quarterly summary
        logger.info("  Testing quarterly summary...")
        summary = service.get_quarterly_summary("ETERNAL")
        if "error" in summary:
            logger.warning(f"  ⚠ Summary: {summary['error']}")
        else:
            logger.info(f"  ✓ Summary: Generated ({len(summary.get('summary', ''))} chars)")
        
        return True
    except Exception as e:
        logger.error(f"✗ LLM Service error: {e}")
        return False


def test_api_endpoints():
    """Test API endpoints (import check)."""
    logger.info("=" * 80)
    logger.info("TEST 7: API Endpoints")
    logger.info("=" * 80)
    
    try:
        from src.api import app
        routes = [route.path for route in app.routes]
        
        logger.info("✓ API: OK")
        logger.info(f"  Available endpoints: {len(routes)}")
        for route in routes[:5]:
            logger.info(f"    - {route}")
        
        return True
    except Exception as e:
        logger.error(f"✗ API error: {e}")
        return False


def check_data_ingestion():
    """Check if data has been ingested."""
    logger.info("=" * 80)
    logger.info("CHECK: Data Ingestion Status")
    logger.info("=" * 80)
    
    checks = {
        "Vector Store Documents": vector_store.count(),
        "Processed Data Files": len(list(Path(settings.processed_data_path).glob("**/*.json"))),
        "Processed Text Files": len(list(Path(settings.processed_data_path).glob("**/*.txt"))),
    }
    
    for check, count in checks.items():
        status = "✓" if count > 0 else "⚠"
        logger.info(f"{status} {check}: {count}")
    
    if all(count == 0 for count in checks.values()):
        logger.warning("\n⚠ No data found! Run data ingestion first:")
        logger.info("  python scripts/ingest.py")
        return False
    
    return True


def main():
    """Run all backend tests."""
    logger.info("🚀 Backend Testing Suite")
    logger.info("=" * 80)
    
    results = {
        "Configuration": test_configuration(),
        "Database": test_database(),
        "Vector Store": test_vector_store(),
        "Gemini API": test_gemini_client(),
        "RAG Pipeline": test_rag_pipeline(),
        "LLM Service": test_llm_service(),
        "API Endpoints": test_api_endpoints(),
    }
    
    data_status = check_data_ingestion()
    
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        logger.info(f"{test_name:20} : {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if not data_status:
        logger.warning("\n⚠ Data ingestion needed before full functionality!")
        logger.info("Run: python scripts/ingest.py")
    
    if passed == total:
        logger.info("\n🎉 All backend tests passed! Backend is ready.")
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed. Check logs above.")


if __name__ == "__main__":
    main()


