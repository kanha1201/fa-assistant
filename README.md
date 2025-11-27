# Financial Data Ingestion Pipeline

A comprehensive data ingestion pipeline for fetching and storing financial data from multiple sources to build a RAG (Retrieval-Augmented Generation) pipeline for AI-powered financial analysis.

## Features

- **PDF Extraction**: Extracts text and images from quarterly/annual reports with OCR support
- **Web Scraping**: Scrapes data from Screener.in, MoneyControl, and Groww
- **Sector Data**: Fetches sector-level benchmarks and comparisons
- **Data Storage**: Stores structured data in PostgreSQL and raw documents for RAG
- **Image Processing**: OCR support for extracting text from images in PDFs

## Project Structure

```
Tensor/
├── src/
│   ├── extractors/
│   │   ├── pdf_extractor.py      # PDF and image extraction
│   │   ├── screener_scraper.py   # Screener.in scraper
│   │   ├── moneycontrol_scraper.py # MoneyControl scraper
│   │   ├── groww_scraper.py      # Groww scraper
│   │   └── sector_scraper.py     # Sector data scraper
│   ├── storage/
│   │   ├── database.py           # PostgreSQL connection and models
│   │   ├── file_storage.py       # File storage utilities
│   │   └── vector_store.py      # Vector database for RAG
│   ├── processors/
│   │   ├── text_cleaner.py      # Text cleaning and normalization
│   │   └── data_validator.py    # Data validation
│   └── utils/
│       ├── config.py            # Configuration management
│       └── logger.py            # Logging setup
├── data/
│   ├── raw/                     # Raw scraped data
│   ├── processed/               # Cleaned and processed data
│   └── documents/               # PDFs and documents
├── scripts/
│   └── ingest.py               # Main ingestion script
├── .env.example                # Environment variables template
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Tesseract OCR (for image text extraction):
```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download from https://github.com/UB-Mannheim/tesseract/wiki
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

4. Set up PostgreSQL database:
```bash
# Create database
createdb financial_data

# Run migrations (will be created)
python scripts/setup_database.py
```

## Usage

Run the data ingestion pipeline:
```bash
python scripts/ingest.py
```

Or run individual extractors:
```bash
python -m src.extractors.pdf_extractor
python -m src.extractors.screener_scraper
```

## Data Sources

1. **Eternal Q2 FY2026 Report** (PDF)
2. **Screener.in** - Company financial data
3. **MoneyControl** - Stock price and company information
4. **Groww** - Stock information and analysis
5. **Sector Data** - Industry benchmarks from Screener.in

## License

Proprietary - Groww Internal Use


