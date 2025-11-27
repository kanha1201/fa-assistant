#!/usr/bin/env python3
"""Update database with real data from websites."""
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

# Real data values (manually verified from websites)
REAL_DATA = {
    "stock_price": 307.0,  # ₹307 from Groww
    "market_cap": 296073.0,  # ₹2,96,073 Cr from Groww and Screener
    "pe_ratio": 1575.0,  # 1,575 from Screener
    "debt_to_equity": 0.11,  # 0.11 from Groww
    "roe": None,  # Keep existing or update if available
}


def parse_number(value_str):
    """Parse number from string, handling Cr, Lakhs, etc."""
    if not value_str:
        return None
    
    # Remove currency symbols and spaces
    value_str = re.sub(r'[₹,\s]', '', str(value_str))
    
    # Handle Cr (Crores)
    if 'Cr' in value_str or 'cr' in value_str:
        value_str = value_str.replace('Cr', '').replace('cr', '')
        try:
            return float(value_str) * 10000  # Convert to actual number
        except:
            return None
    
    # Handle Lakhs
    if 'L' in value_str or 'Lakh' in value_str:
        value_str = value_str.replace('L', '').replace('Lakh', '').replace('lakh', '')
        try:
            return float(value_str) * 100  # Convert to actual number
        except:
            return None
    
    # Try direct conversion
    try:
        return float(value_str)
    except:
        return None


def scrape_screener_data():
    """Scrape data from Screener.in."""
    url = "https://www.screener.in/company/ETERNAL/consolidated/"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            # Extract Market Cap
            market_cap_match = re.search(r'Market Cap[^<]*?(\d+[,\d]*\.?\d*)\s*(Cr|L)', html, re.IGNORECASE)
            if market_cap_match:
                value = parse_number(market_cap_match.group(1) + market_cap_match.group(2))
                if value:
                    REAL_DATA['market_cap'] = value / 10000  # Convert back to Cr
            
            # Extract P/E Ratio
            pe_match = re.search(r'P/E[^<]*?(\d+[,\d]*\.?\d*)', html, re.IGNORECASE)
            if pe_match:
                value = parse_number(pe_match.group(1))
                if value:
                    REAL_DATA['pe_ratio'] = value
            
            # Extract Debt to Equity
            de_match = re.search(r'Debt to Equity[^<]*?(\d+\.?\d*)', html, re.IGNORECASE)
            if de_match:
                value = parse_number(de_match.group(1))
                if value:
                    REAL_DATA['debt_to_equity'] = value
            
            # Extract Current Price
            price_match = re.search(r'Current Price[^<]*?₹\s*(\d+[,\d]*\.?\d*)', html, re.IGNORECASE)
            if price_match:
                value = parse_number(price_match.group(1))
                if value:
                    REAL_DATA['stock_price'] = value
            
            print("✓ Scraped data from Screener.in")
            return True
    except Exception as e:
        print(f"⚠ Screener scraping failed: {e}")
        return False


def scrape_groww_data():
    """Scrape data from Groww."""
    url = "https://groww.in/stocks/zomato-ltd"
    
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            # Extract Stock Price
            price_patterns = [
                r'₹\s*(\d+[,\d]*\.?\d*)',
                r'price[^<]*?(\d+[,\d]*\.?\d*)',
            ]
            for pattern in price_patterns:
                price_match = re.search(pattern, html, re.IGNORECASE)
                if price_match:
                    value = parse_number(price_match.group(1))
                    if value and 200 < value < 500:  # Sanity check
                        REAL_DATA['stock_price'] = value
                        break
            
            # Extract Market Cap
            market_cap_patterns = [
                r'Market Cap[^<]*?(\d+[,\d]*\.?\d*)\s*(Cr|L)',
                r'market.*cap[^<]*?(\d+[,\d]*\.?\d*)',
            ]
            for pattern in market_cap_patterns:
                cap_match = re.search(pattern, html, re.IGNORECASE)
                if cap_match:
                    value = parse_number(cap_match.group(1) + (cap_match.group(2) if len(cap_match.groups()) > 1 else ''))
                    if value:
                        REAL_DATA['market_cap'] = value / 10000  # Convert to Cr
                        break
            
            # Extract Debt to Equity
            de_match = re.search(r'Debt.*Equity[^<]*?(\d+\.?\d*)', html, re.IGNORECASE)
            if de_match:
                value = parse_number(de_match.group(1))
                if value:
                    REAL_DATA['debt_to_equity'] = value
            
            print("✓ Scraped data from Groww")
            return True
    except Exception as e:
        print(f"⚠ Groww scraping failed: {e}")
        return False


def update_database():
    """Update database with real data."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get company ID
    cursor.execute("SELECT id FROM companies WHERE symbol = 'ETERNAL'")
    company_row = cursor.fetchone()
    
    if not company_row:
        # Create company if doesn't exist
        company_id = str(uuid4())
        cursor.execute("""
            INSERT INTO companies (id, symbol, name, sector, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (company_id, "ETERNAL", "Eternal Limited", "Online Services", datetime.now().isoformat()))
    else:
        company_id = company_row[0]
    
    # Update or insert metrics
    metrics_to_update = {
        "market_cap": REAL_DATA.get("market_cap"),
        "pe_ratio": REAL_DATA.get("pe_ratio"),
        "debt_to_equity": REAL_DATA.get("debt_to_equity"),
        "current_price": REAL_DATA.get("stock_price"),
    }
    
    for metric_name, metric_value in metrics_to_update.items():
        if metric_value is not None:
            # Check if metric exists
            cursor.execute("""
                SELECT id FROM financial_metrics 
                WHERE company_id = ? AND metric_name = ?
            """, (company_id, metric_name))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing
                cursor.execute("""
                    UPDATE financial_metrics 
                    SET metric_value = ?
                    WHERE id = ?
                """, (metric_value, existing[0]))
                print(f"✓ Updated {metric_name}: {metric_value}")
            else:
                # Insert new
                metric_id = str(uuid4())
                cursor.execute("""
                    INSERT INTO financial_metrics 
                    (id, company_id, metric_name, metric_value, period_type, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (metric_id, company_id, metric_name, metric_value, "current", "manual_update", datetime.now().isoformat()))
                print(f"✓ Inserted {metric_name}: {metric_value}")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database updated successfully!")


def main():
    """Main function."""
    print("=" * 80)
    print("Updating Database with Real Data")
    print("=" * 80)
    
    # Use provided real values
    print("\nUsing provided real data values:")
    print(f"  Stock Price: ₹{REAL_DATA['stock_price']}")
    print(f"  Market Cap: ₹{REAL_DATA['market_cap']:,.0f} Cr")
    print(f"  P/E Ratio: {REAL_DATA['pe_ratio']}")
    print(f"  Debt to Equity: {REAL_DATA['debt_to_equity']}")
    
    # Try to scrape (may fail due to website structure)
    print("\nAttempting to scrape websites...")
    scrape_screener_data()
    scrape_groww_data()
    
    # Update database
    print("\nUpdating database...")
    update_database()
    
    # Verify
    print("\nVerifying updated data...")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT metric_name, metric_value 
        FROM financial_metrics 
        WHERE company_id = (SELECT id FROM companies WHERE symbol = 'ETERNAL')
    """)
    metrics = cursor.fetchall()
    conn.close()
    
    print("\nCurrent metrics in database:")
    for name, value in metrics:
        print(f"  {name}: {value}")


if __name__ == "__main__":
    main()

