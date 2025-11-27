#!/usr/bin/env python3
"""Create sample data files for testing without external packages."""
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from uuid import uuid4

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "financial_data.db"
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "ETERNAL"
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)

print("Creating sample data files...")

# 1. Create sample JSON data
sample_data = {
    "company_symbol": "ETERNAL",
    "company_name": "Eternal Limited (Formerly Zomato Limited)",
    "source_url": "https://example.com",
    "scraped_at": datetime.now().isoformat(),
    "key_metrics": {
        "Market Cap": "1,50,000 Cr",
        "Current Price": "250.50",
        "P/E Ratio": "45.2",
        "ROE": "12.5%",
        "Debt to Equity": "0.3"
    },
    "quarterly_results": [
        {
            "period": "Q2 FY2026",
            "revenue": "23,164 Cr",
            "growth": "57% YoY"
        }
    ],
    "full_text": """
    Eternal Limited Q2 FY2026 Results:
    
    Key Highlights:
    - NOV (B2C business) grew 57% YoY to INR 23,164 crore
    - Adjusted Revenue grew 172% YoY to INR 13,968 crore
    - Adjusted EBITDA reached INR 224 crore, declining 32% YoY
    
    Food Delivery:
    - NOV growth improved to 14% YoY
    - Adjusted EBITDA margin reached all-time high of 5.3%
    
    Quick Commerce:
    - NOV growth accelerated to 137% YoY
    - Network expansion with 272 net new stores
    - Adjusted EBITDA margin improved to -1.3%
    
    The company continues to focus on profitability improvements
    while maintaining growth momentum across all business segments.
    """
}

# Save JSON
json_file = PROCESSED_PATH / "screener_eternal_sample.json"
with open(json_file, "w") as f:
    json.dump(sample_data, f, indent=2)
print(f"✓ Created: {json_file.name}")

# Save text file
txt_file = PROCESSED_PATH / "eternal_q2_fy26_sample.txt"
with open(txt_file, "w") as f:
    f.write(sample_data["full_text"])
print(f"✓ Created: {txt_file.name}")

# 2. Create database entries
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

cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_metrics (
        id TEXT PRIMARY KEY,
        company_id TEXT,
        metric_name TEXT NOT NULL,
        metric_value REAL,
        period_type TEXT,
        source TEXT,
        created_at TEXT
    )
""")

cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents (
        id TEXT PRIMARY KEY,
        company_id TEXT,
        document_type TEXT,
        source_url TEXT,
        content_text TEXT,
        created_at TEXT
    )
""")

# Create company
company_id = str(uuid4())
cursor.execute("""
    INSERT OR REPLACE INTO companies (id, symbol, name, sector, created_at)
    VALUES (?, ?, ?, ?, ?)
""", (company_id, "ETERNAL", "Eternal Limited", "Online Services", datetime.now().isoformat()))

# Create financial metrics
metrics = [
    ("pe_ratio", 45.2, "annual"),
    ("roe", 12.5, "annual"),
    ("debt_to_equity", 0.3, "annual"),
    ("market_cap", 150000, "current"),
]

for metric_name, value, period in metrics:
    metric_id = str(uuid4())
    cursor.execute("""
        INSERT OR REPLACE INTO financial_metrics 
        (id, company_id, metric_name, metric_value, period_type, source, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (metric_id, company_id, metric_name, value, period, "sample", datetime.now().isoformat()))

# Create document
doc_id = str(uuid4())
cursor.execute("""
    INSERT OR REPLACE INTO documents 
    (id, company_id, document_type, source_url, content_text, created_at)
    VALUES (?, ?, ?, ?, ?, ?)
""", (doc_id, company_id, "sample_data", "sample", sample_data["full_text"], datetime.now().isoformat()))

conn.commit()
conn.close()

print(f"✓ Created database entries")
print(f"  Company: ETERNAL")
print(f"  Metrics: {len(metrics)}")
print(f"  Documents: 1")

print("\n✅ Sample data created successfully!")
print(f"\nFiles created in: {PROCESSED_PATH}")
print(f"Database: {DB_PATH}")

