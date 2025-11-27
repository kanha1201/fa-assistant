# Installation Guide

## Issue Detected
There appears to be a network or pip configuration issue preventing package installation. Follow these steps:

## Manual Installation Steps

### Option 1: Using Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Option 2: Install Core Packages Individually

```bash
# Core for LLM and API
pip install google-generativeai fastapi uvicorn

# Core for data processing
pip install chromadb sqlalchemy pydantic pydantic-settings python-dotenv

# Core for web scraping
pip install requests beautifulsoup4 lxml

# Core for PDF processing
pip install pdfplumber pymupdf

# Utilities
pip install loguru pandas numpy
```

### Option 3: Check Network/Proxy Settings

If packages still can't be found:

1. **Check internet connectivity:**
   ```bash
   curl https://pypi.org/simple/
   ```

2. **Check pip configuration:**
   ```bash
   pip config list
   ```

3. **Try with explicit index:**
   ```bash
   pip install --index-url https://pypi.org/simple/ python-dotenv
   ```

4. **If behind proxy:**
   ```bash
   pip install --proxy http://proxy:port python-dotenv
   ```

## After Installation

1. **Verify installation:**
   ```bash
   python3 -c "import google.generativeai, fastapi, chromadb; print('✓ Dependencies installed')"
   ```

2. **Run data ingestion:**
   ```bash
   python3 scripts/ingest.py
   ```

3. **Test backend:**
   ```bash
   python3 scripts/test_backend.py
   ```

## Minimum Required Packages for Testing

If you can't install all packages, at minimum install:

```bash
pip install google-generativeai fastapi uvicorn chromadb sqlalchemy pydantic pydantic-settings python-dotenv loguru
```

This will allow you to test the LLM service and API endpoints.


