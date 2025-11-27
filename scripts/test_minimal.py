"""Minimal test script using only built-in libraries."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# Use minimal versions
import src.utils.config_minimal as config_module
import src.utils.logger_minimal as logger_module
import src.storage.database_minimal as db_module

# Replace imports
sys.modules['src.utils.config'] = config_module
sys.modules['src.utils.logger'] = logger_module
sys.modules['src.storage.database'] = db_module

from src.utils.config_minimal import settings
from src.utils.logger_minimal import logger
from src.storage.database_minimal import db


def test_configuration():
    """Test configuration."""
    logger.info("=" * 80)
    logger.info("TEST 1: Configuration (Minimal)")
    logger.info("=" * 80)
    
    checks = {
        "API Key": bool(settings.gemini_api_key),
        "Database Path": settings.database_url,
        "Vector DB Path": settings.vector_db_path,
    }
    
    for check, result in checks.items():
        status = "✓" if result else "✗"
        logger.info(f"{status} {check}: {result if isinstance(result, str) else ('OK' if result else 'MISSING')}")
    
    return all([checks["API Key"], checks["Database Path"], checks["Vector DB Path"]])


def test_database():
    """Test database."""
    logger.info("=" * 80)
    logger.info("TEST 2: Database (SQLite)")
    logger.info("=" * 80)
    
    try:
        # Test connection
        conn = db.get_session()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM companies")
        count = cursor.fetchone()[0]
        conn.close()
        
        logger.info(f"✓ Database connection: OK")
        logger.info(f"  Companies in database: {count}")
        return True
    except Exception as e:
        logger.error(f"✗ Database error: {e}")
        return False


def test_file_storage():
    """Test file storage."""
    logger.info("=" * 80)
    logger.info("TEST 3: File Storage")
    logger.info("=" * 80)
    
    try:
        import json
        import os
        
        # Check if data directories exist
        paths = [
            settings.raw_data_path,
            settings.processed_data_path,
            settings.documents_path
        ]
        
        for path in paths:
            Path(path).mkdir(parents=True, exist_ok=True)
        
        # Test write
        test_file = Path(settings.processed_data_path) / "test.json"
        with open(test_file, "w") as f:
            json.dump({"test": "data"}, f)
        
        # Test read
        with open(test_file, "r") as f:
            data = json.load(f)
        
        test_file.unlink()  # Cleanup
        
        logger.info("✓ File storage: OK")
        return True
    except Exception as e:
        logger.error(f"✗ File storage error: {e}")
        return False


def test_gemini_api():
    """Test Gemini API (if available)."""
    logger.info("=" * 80)
    logger.info("TEST 4: Gemini API")
    logger.info("=" * 80)
    
    if not settings.gemini_api_key:
        logger.warning("⚠ API key not found")
        return False
    
    try:
        import urllib.request
        import urllib.parse
        import json
        
        # Simple API test using urllib
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={settings.gemini_api_key}"
        
        data = {
            "contents": [{
                "parts": [{"text": "Say hello"}]
            }]
        }
        
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json')
        
        data_json = json.dumps(data).encode('utf-8')
        
        try:
            with urllib.request.urlopen(req, data=data_json, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                if 'candidates' in result:
                    logger.info("✓ Gemini API: OK")
                    logger.info(f"  Response: {result['candidates'][0]['content']['parts'][0]['text'][:100]}...")
                    return True
                else:
                    logger.warning(f"⚠ API response unexpected: {result}")
                    return False
        except urllib.error.HTTPError as e:
            logger.error(f"✗ API HTTP Error: {e.code} - {e.reason}")
            return False
        except Exception as e:
            logger.error(f"✗ API error: {e}")
            return False
    
    except ImportError:
        logger.warning("⚠ urllib not available")
        return False


def check_data_files():
    """Check for existing data files."""
    logger.info("=" * 80)
    logger.info("CHECK: Data Files")
    logger.info("=" * 80)
    
    import os
    
    checks = {
        "Processed JSON files": len(list(Path(settings.processed_data_path).glob("**/*.json"))),
        "Processed TXT files": len(list(Path(settings.processed_data_path).glob("**/*.txt"))),
        "Document files": len(list(Path(settings.documents_path).glob("*.pdf"))),
    }
    
    for check, count in checks.items():
        status = "✓" if count > 0 else "⚠"
        logger.info(f"{status} {check}: {count}")
    
    return any(count > 0 for count in checks.values())


def main():
    """Run minimal tests."""
    logger.info("🧪 Minimal Backend Testing (No External Packages)")
    logger.info("=" * 80)
    
    results = {
        "Configuration": test_configuration(),
        "Database": test_database(),
        "File Storage": test_file_storage(),
        "Gemini API": test_gemini_api(),
    }
    
    data_status = check_data_files()
    
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
        logger.warning("\n⚠ No data files found. Data ingestion needed for full functionality.")
        logger.info("Note: Data ingestion requires external packages (requests, beautifulsoup4)")
    
    if passed == total:
        logger.info("\n🎉 Core backend components working!")
    else:
        logger.warning(f"\n⚠️  {total - passed} test(s) failed.")


if __name__ == "__main__":
    main()


