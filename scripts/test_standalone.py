#!/usr/bin/env python3
"""Standalone test script using only built-in libraries - no package imports."""
import sys
import os
import json
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path
from datetime import datetime
from uuid import uuid4


# Setup paths
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Load .env manually
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

# Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
DB_PATH = BASE_DIR / "data" / "financial_data.db"
VECTOR_DB_PATH = BASE_DIR / "data" / "vector_db"
PROCESSED_PATH = BASE_DIR / "data" / "processed"
DOCUMENTS_PATH = BASE_DIR / "data" / "documents"

# Create directories
for path in [DB_PATH.parent, VECTOR_DB_PATH, PROCESSED_PATH, DOCUMENTS_PATH]:
    path.mkdir(parents=True, exist_ok=True)


def print_test(name):
    """Print test header."""
    print("\n" + "=" * 80)
    print(f"TEST: {name}")
    print("=" * 80)


def test_configuration():
    """Test configuration."""
    print_test("Configuration")
    
    checks = {
        "API Key": bool(GEMINI_API_KEY),
        "Database Path": str(DB_PATH),
        "Vector DB Path": str(VECTOR_DB_PATH),
        "Processed Path": str(PROCESSED_PATH),
    }
    
    for check, result in checks.items():
        status = "✓" if result else "✗"
        print(f"{status} {check}: {result if isinstance(result, str) else ('OK' if result else 'MISSING')}")
    
    return all([checks["API Key"], checks["Database Path"], checks["Vector DB Path"]])


def test_database():
    """Test SQLite database."""
    print_test("Database (SQLite)")
    
    try:
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        
        # Create tables if not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS companies (
                id TEXT PRIMARY KEY,
                symbol TEXT UNIQUE NOT NULL,
                name TEXT,
                sector TEXT,
                created_at TEXT
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM companies")
        count = cursor.fetchone()[0]
        conn.close()
        
        print(f"✓ Database connection: OK")
        print(f"  Companies in database: {count}")
        return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False


def test_file_storage():
    """Test file storage."""
    print_test("File Storage")
    
    try:
        # Test write
        test_file = PROCESSED_PATH / "test.json"
        with open(test_file, "w") as f:
            json.dump({"test": "data", "timestamp": datetime.now().isoformat()}, f)
        
        # Test read
        with open(test_file, "r") as f:
            data = json.load(f)
        
        test_file.unlink()  # Cleanup
        
        print("✓ File storage: OK")
        print(f"  Test file created and read successfully")
        return True
    except Exception as e:
        print(f"✗ File storage error: {e}")
        return False


def test_gemini_api():
    """Test Gemini API using urllib."""
    print_test("Gemini API")
    
    if not GEMINI_API_KEY:
        print("⚠ API key not found in .env file")
        return False
    
    try:
        # Try gemini-1.5-flash or gemini-pro
        # Try correct endpoint format with API key in header
        models_to_try = [
            "gemini-2.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro-latest"
        ]
        
        base_url = "https://generativelanguage.googleapis.com/v1beta"
        
        for model in models_to_try:
            try:
                url = f"{base_url}/models/{model}:generateContent"
                
                data = {
                    "contents": [{
                        "parts": [{"text": "Say 'Hello, backend test successful!' if you can read this."}]
                    }]
                }
                
                req = urllib.request.Request(url)
                req.add_header('Content-Type', 'application/json')
                req.add_header('x-goog-api-key', GEMINI_API_KEY)  # Correct header format
                
                data_json = json.dumps(data).encode('utf-8')
                
                with urllib.request.urlopen(req, data=data_json, timeout=10) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    if 'candidates' in result and len(result['candidates']) > 0:
                        text = result['candidates'][0]['content']['parts'][0]['text']
                        print("✓ Gemini API: OK")
                        print(f"  Model used: {model}")
                        print(f"  Response: {text[:150]}...")
                        return True
                    else:
                        continue  # Try next model
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    continue  # Try next model
                error_body = e.read().decode('utf-8')
                try:
                    error_data = json.loads(error_body)
                    error_msg = error_data.get('error', {}).get('message', 'Unknown')
                    if 'not found' in error_msg.lower():
                        continue  # Try next model
                except:
                    pass
                # If not 404, show error
                print(f"✗ API HTTP Error: {e.code} - {e.reason}")
                print(f"  Error details: {error_body[:200]}")
                return False
            except Exception as e:
                continue  # Try next model
        
        print("✗ All models failed. Check API key and network connectivity.")
        return False
    
    except Exception as e:
        print(f"✗ Setup error: {e}")
        return False


def check_data_files():
    """Check for existing data files."""
    print_test("Data Files Check")
    
    json_files = list(PROCESSED_PATH.glob("**/*.json"))
    txt_files = list(PROCESSED_PATH.glob("**/*.txt"))
    pdf_files = list(DOCUMENTS_PATH.glob("*.pdf"))
    
    checks = {
        "Processed JSON files": len(json_files),
        "Processed TXT files": len(txt_files),
        "PDF documents": len(pdf_files),
    }
    
    for check, count in checks.items():
        status = "✓" if count > 0 else "⚠"
        print(f"{status} {check}: {count}")
    
    if json_files:
        print(f"\n  Sample files:")
        for f in json_files[:3]:
            print(f"    - {f.name}")
    
    return any(count > 0 for count in checks.values())


def test_vector_store_files():
    """Check vector store files."""
    print_test("Vector Store Files")
    
    try:
        vector_files = list(VECTOR_DB_PATH.glob("**/*"))
        print(f"✓ Vector DB directory: {VECTOR_DB_PATH}")
        print(f"  Files/dirs: {len(vector_files)}")
        
        if vector_files:
            print(f"  Sample: {vector_files[0].name}")
        
        return True
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "🚀" * 40)
    print("STANDALONE BACKEND TESTING (No External Packages)")
    print("🚀" * 40)
    
    results = {
        "Configuration": test_configuration(),
        "Database": test_database(),
        "File Storage": test_file_storage(),
        "Gemini API": test_gemini_api(),
        "Vector Store": test_vector_store_files(),
    }
    
    data_status = check_data_files()
    
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} : {status}")
    
    passed = sum(results.values())
    total = len(results)
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if not data_status:
        print("\n⚠ No data files found.")
        print("  Note: Data ingestion requires external packages.")
        print("  However, API testing can proceed with manual data.")
    
    if passed == total:
        print("\n🎉 Core backend components working!")
        print("\n✅ Backend is ready for API testing!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed.")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS:")
    print("=" * 80)
    print("1. If Gemini API test passed, you can test API endpoints")
    print("2. Create sample data files manually if needed")
    print("3. Test API with: python3 scripts/test_api_minimal.py")


if __name__ == "__main__":
    main()

