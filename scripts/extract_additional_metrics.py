#!/usr/bin/env python3
"""Extract additional metrics from Groww website."""
import sys
import os
import json
import sqlite3
import urllib.request
import re
from pathlib import Path
from datetime import datetime
from uuid import uuid4

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "financial_data.db"

# Load API key
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()


def extract_from_groww_json():
    """Extract metrics from Groww website JSON data."""
    url = "https://groww.in/stocks/zomato-ltd"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            # Extract JSON data from script tag
            json_match = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                data = json.loads(json_str)
                
                stats = data['props']['pageProps']['stockData']['stats']
                price_data = data['props']['pageProps']['stockData']['priceData']['nse']
                
                metrics = {
                    'eps': stats.get('epsTtm'),
                    'book_value': stats.get('bookValue'),
                    'volume': price_data.get('volume'),
                    'pb_ratio': stats.get('pbRatio'),
                }
                
                print("✓ Extracted metrics from Groww JSON:")
                for key, value in metrics.items():
                    if value is not None:
                        print(f"  {key}: {value}")
                
                return metrics
    except Exception as e:
        print(f"✗ Error extracting from Groww: {e}")
        return {}


def update_database(metrics):
    """Update database with additional metrics."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get company ID
    cursor.execute("SELECT id FROM companies WHERE symbol = 'ETERNAL'")
    company_id = cursor.fetchone()[0]
    
    metric_mapping = {
        'eps': 'eps_ttm',
        'book_value': 'book_value',
        'volume': 'traded_volume',
        'pb_ratio': 'pb_ratio',
    }
    
    print("\nUpdating database...")
    for key, db_name in metric_mapping.items():
        value = metrics.get(key)
        if value is not None:
            # Check if exists
            cursor.execute("""
                SELECT id FROM financial_metrics 
                WHERE company_id = ? AND metric_name = ?
            """, (company_id, db_name))
            
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE financial_metrics 
                    SET metric_value = ?, source = 'groww'
                    WHERE id = ?
                """, (value, existing[0]))
                print(f"  ✓ Updated {db_name}: {value}")
            else:
                metric_id = str(uuid4())
                cursor.execute("""
                    INSERT INTO financial_metrics 
                    (id, company_id, metric_name, metric_value, period_type, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (metric_id, company_id, db_name, value, "current", "groww", datetime.now().isoformat()))
                print(f"  ✓ Inserted {db_name}: {value}")
    
    conn.commit()
    conn.close()
    print("\n✅ Database updated!")


def main():
    """Main function."""
    print("="*80)
    print("Extracting Additional Metrics from Groww")
    print("="*80)
    
    metrics = extract_from_groww_json()
    
    if metrics:
        update_database(metrics)
        
        # Verify
        print("\n" + "="*80)
        print("Verification")
        print("="*80)
        conn = sqlite3.connect(str(DB_PATH))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT metric_name, metric_value 
            FROM financial_metrics 
            WHERE company_id = (SELECT id FROM companies WHERE symbol = 'ETERNAL')
            ORDER BY metric_name
        """)
        all_metrics = cursor.fetchall()
        conn.close()
        
        print("\nAll metrics in database:")
        for name, value in all_metrics:
            print(f"  {name}: {value}")


if __name__ == "__main__":
    main()


