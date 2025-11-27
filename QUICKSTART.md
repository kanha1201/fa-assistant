# Quick Start Guide

## Prerequisites

1. **Python 3.9+** installed
2. **PostgreSQL** database (optional, for structured storage)
3. **Tesseract OCR** installed (for image text extraction)

### Install Tesseract OCR

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

## Setup

1. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure environment variables:**
```bash
# Copy example env file
cp .env.example .env

# Edit .env with your settings
# For basic testing, you can use SQLite instead of PostgreSQL:
# DATABASE_URL=sqlite:///./data/financial_data.db
```

3. **Set up database (if using PostgreSQL):**
```bash
# Create database
createdb financial_data

# Create tables
python scripts/setup_database.py
```

## Usage

### Run Full Data Ingestion Pipeline

```bash
python scripts/ingest.py
```

This will:
- Download and extract PDF report (Q2 FY2026)
- Scrape Screener.in company data
- Scrape MoneyControl stock data
- Scrape Groww stock data
- Scrape sector data
- Store all data in files and database
- Create vector embeddings for RAG pipeline

### Test Individual Extractors

```bash
python scripts/test_extractors.py
```

### Run Individual Extractors

```bash
# PDF extraction
python -m src.extractors.pdf_extractor

# Screener scraping
python -m src.extractors.screener_scraper

# MoneyControl scraping
python -m src.extractors.moneycontrol_scraper

# Groww scraping
python -m src.extractors.groww_scraper
```

## Output Structure

After running the ingestion pipeline, you'll find:

```
data/
├── raw/                    # Raw scraped data
├── processed/              # Cleaned and processed data
│   └── ETERNAL/           # Company-specific data
│       ├── *.json         # Structured data
│       └── *.txt          # Text content
├── documents/             # PDF files
└── vector_db/             # ChromaDB vector database

logs/
└── ingestion.log         # Application logs
```

## Data Sources

1. **PDF Report**: Q2 FY2026 Shareholders' Letter
   - URL: https://b.zmtcdn.com/investor-relations/Eternal_Shareholders_Letter_Q2FY26_Results.pdf
   - Extracts: Text, tables, images (with OCR)

2. **Screener.in**: Company financial data
   - URL: https://www.screener.in/company/ETERNAL/consolidated/
   - Extracts: Metrics, ratios, financial statements

3. **MoneyControl**: Stock information
   - URL: https://www.moneycontrol.com/india/stockpricequote/online-services/eternal/Z
   - Extracts: Price, ratios, company info

4. **Groww**: Stock data
   - URL: https://groww.in/stocks/zomato-ltd
   - Extracts: Price, metrics, analysis

5. **Sector Data**: Industry benchmarks
   - URL: https://www.screener.in/market/IN02/IN0206/IN020603/IN020603004/
   - Extracts: Sector companies, benchmarks

## Troubleshooting

### Database Connection Issues

If PostgreSQL is not available, you can use SQLite:
```bash
# In .env file
DATABASE_URL=sqlite:///./data/financial_data.db
```

### OCR Not Working

Make sure Tesseract is installed and path is correct in `.env`:
```bash
# macOS default path
TESSERACT_CMD=/usr/local/bin/tesseract

# Linux default path
TESSERACT_CMD=/usr/bin/tesseract
```

### Web Scraping Fails

Some websites may block automated requests. The scrapers include:
- User-Agent headers
- Rate limiting (delays between requests)
- Retry logic

If scraping fails, check:
1. Internet connection
2. Website availability
3. Rate limiting settings in `.env`

## Next Steps

After data ingestion is complete, you can:
1. Query the vector database for semantic search
2. Build RAG pipeline for AI chatbot
3. Extract structured metrics for analysis
4. Set up scheduled ingestion jobs

## Support

Check logs in `logs/ingestion.log` for detailed error messages.


