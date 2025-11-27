#!/usr/bin/env python3
"""Verify and update data with priority order: Zomato Report > Groww > Screener > MoneyControl."""
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
PDF_PATH = BASE_DIR / "data" / "documents"

# Priority order: Zomato Report > Groww > Screener > MoneyControl
PRIORITY_ORDER = ["zomato_report", "groww", "screener", "moneycontrol"]

# Data sources with their values
DATA_SOURCES = {
    "zomato_report": {},  # Will extract from PDF if available
    "groww": {},
    "screener": {},
    "moneycontrol": {}
}


def extract_from_pdf():
    """Extract data from Zomato PDF report."""
    print("\n1. Checking Zomato Report (PDF)...")
    
    pdf_files = list(PDF_PATH.glob("*.pdf"))
    if not pdf_files:
        print("   ⚠ No PDF files found")
        return {}
    
    # Try to extract text from PDF
    data = {}
    try:
        import PyPDF2
        pdf_file = pdf_files[0]
        with open(pdf_file, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages[:10]:  # First 10 pages
                text += page.extract_text()
            
            # Look for ROE
            roe_match = re.search(r'ROE[:\s]*(\d+\.?\d*)%?', text, re.IGNORECASE)
            if roe_match:
                data['roe'] = float(roe_match.group(1))
                print(f"   ✓ Found ROE: {data['roe']}%")
            
            # Look for other metrics in PDF
            # Add more extraction patterns as needed
            
    except Exception as e:
        print(f"   ⚠ PDF extraction failed: {e}")
    
    return data


def scrape_groww():
    """Scrape data from Groww website."""
    print("\n2. Scraping Groww website...")
    url = "https://groww.in/stocks/zomato-ltd"
    
    data = {}
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            # Extract ROE
            roe_patterns = [
                r'ROE[^<]*?(\d+\.?\d*)%?',
                r'Return.*Equity[^<]*?(\d+\.?\d*)%?',
                r'roe[^<]*?(\d+\.?\d*)',
            ]
            for pattern in roe_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    value = float(match.group(1))
                    if 0 < value < 100:  # Sanity check
                        data['roe'] = value
                        print(f"   ✓ Found ROE: {data['roe']}%")
                        break
            
            # Extract Stock Price
            price_patterns = [
                r'₹\s*(\d{2,4}(?:\.\d+)?)',
            ]
            for pattern in price_patterns:
                matches = re.findall(pattern, html)
                for match in matches:
                    value = float(match.replace(',', ''))
                    if 200 < value < 500:  # Sanity check for stock price
                        data['current_price'] = value
                        print(f"   ✓ Found Stock Price: ₹{data['current_price']}")
                        break
                if 'current_price' in data:
                    break
            
            # Extract Market Cap
            market_cap_patterns = [
                r'Market.*Cap[^<]*?(\d+[,\d]*\.?\d*)\s*(Cr|L)',
                r'₹\s*(\d+[,\d]*)\s*Cr',
            ]
            for pattern in market_cap_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    value_str = match.group(1).replace(',', '')
                    if 'Cr' in html[match.start():match.end()+50] or len(match.groups()) > 1:
                        value = float(value_str)
                        data['market_cap'] = value
                        print(f"   ✓ Found Market Cap: ₹{data['market_cap']:,.0f} Cr")
                        break
            
            # Extract P/E Ratio
            pe_patterns = [
                r'P/E[^<]*?(\d+[,\d]*\.?\d*)',
                r'Price.*Earnings[^<]*?(\d+[,\d]*\.?\d*)',
            ]
            for pattern in pe_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    value = float(match.group(1).replace(',', ''))
                    if value > 0:
                        data['pe_ratio'] = value
                        print(f"   ✓ Found P/E Ratio: {data['pe_ratio']}")
                        break
            
            # Extract Debt to Equity
            de_patterns = [
                r'Debt.*Equity[^<]*?(\d+\.?\d*)',
                r'D/E[^<]*?(\d+\.?\d*)',
            ]
            for pattern in de_patterns:
                match = re.search(pattern, html, re.IGNORECASE)
                if match:
                    value = float(match.group(1))
                    if 0 <= value < 10:  # Sanity check
                        data['debt_to_equity'] = value
                        print(f"   ✓ Found Debt to Equity: {data['debt_to_equity']}")
                        break
            
    except Exception as e:
        print(f"   ⚠ Groww scraping failed: {e}")
    
    return data


def scrape_screener():
    """Scrape data from Screener.in."""
    print("\n3. Scraping Screener.in...")
    url = "https://www.screener.in/company/ETERNAL/consolidated/"
    
    data = {}
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            # Extract ROE
            roe_match = re.search(r'ROE[^<]*?(\d+\.?\d*)%?', html, re.IGNORECASE)
            if roe_match:
                value = float(roe_match.group(1))
                if 0 < value < 100:
                    data['roe'] = value
                    print(f"   ✓ Found ROE: {data['roe']}%")
            
            # Extract Market Cap
            market_cap_match = re.search(r'Market Cap[^<]*?(\d+[,\d]*\.?\d*)\s*(Cr|L)', html, re.IGNORECASE)
            if market_cap_match:
                value = float(market_cap_match.group(1).replace(',', ''))
                data['market_cap'] = value
                print(f"   ✓ Found Market Cap: ₹{data['market_cap']:,.0f} Cr")
            
            # Extract P/E Ratio
            pe_match = re.search(r'P/E[^<]*?(\d+[,\d]*\.?\d*)', html, re.IGNORECASE)
            if pe_match:
                value = float(pe_match.group(1).replace(',', ''))
                if value > 0:
                    data['pe_ratio'] = value
                    print(f"   ✓ Found P/E Ratio: {data['pe_ratio']}")
            
            # Extract Debt to Equity
            de_match = re.search(r'Debt to Equity[^<]*?(\d+\.?\d*)', html, re.IGNORECASE)
            if de_match:
                value = float(de_match.group(1))
                if 0 <= value < 10:
                    data['debt_to_equity'] = value
                    print(f"   ✓ Found Debt to Equity: {data['debt_to_equity']}")
            
    except Exception as e:
        print(f"   ⚠ Screener scraping failed: {e}")
    
    return data


def scrape_moneycontrol():
    """Scrape data from MoneyControl."""
    print("\n4. Scraping MoneyControl...")
    url = "https://www.moneycontrol.com/india/stockpricequote/online-services/eternal/Z"
    
    data = {}
    try:
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36')
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode('utf-8')
            
            # Extract ROE
            roe_match = re.search(r'ROE[^<]*?(\d+\.?\d*)%?', html, re.IGNORECASE)
            if roe_match:
                value = float(roe_match.group(1))
                if 0 < value < 100:
                    data['roe'] = value
                    print(f"   ✓ Found ROE: {data['roe']}%")
            
            # Extract other metrics similarly
            
    except Exception as e:
        print(f"   ⚠ MoneyControl scraping failed: {e}")
    
    return data


def select_best_value(metric_name):
    """Select best value based on priority order."""
    for source in PRIORITY_ORDER:
        if source in DATA_SOURCES and metric_name in DATA_SOURCES[source]:
            value = DATA_SOURCES[source][metric_name]
            if value is not None:
                return value, source
    return None, None


def update_database():
    """Update database with best values based on priority."""
    print("\n" + "="*80)
    print("Updating Database with Priority-Based Values")
    print("="*80)
    
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get company ID
    cursor.execute("SELECT id FROM companies WHERE symbol = 'ETERNAL'")
    company_row = cursor.fetchone()
    
    if not company_row:
        company_id = str(uuid4())
        cursor.execute("""
            INSERT INTO companies (id, symbol, name, sector, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (company_id, "ETERNAL", "Eternal Limited", "Online Services", datetime.now().isoformat()))
    else:
        company_id = company_row[0]
    
    # Metrics to update
    metrics = ['roe', 'current_price', 'market_cap', 'pe_ratio', 'debt_to_equity']
    
    print("\nSelected values (by priority):")
    for metric_name in metrics:
        value, source = select_best_value(metric_name)
        if value is not None:
            print(f"  {metric_name}: {value} (from {source})")
            
            # Check if metric exists
            cursor.execute("""
                SELECT id FROM financial_metrics 
                WHERE company_id = ? AND metric_name = ?
            """, (company_id, metric_name))
            
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE financial_metrics 
                    SET metric_value = ?, source = ?
                    WHERE id = ?
                """, (value, source, existing[0]))
            else:
                metric_id = str(uuid4())
                cursor.execute("""
                    INSERT INTO financial_metrics 
                    (id, company_id, metric_name, metric_value, period_type, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (metric_id, company_id, metric_name, value, "current", source, datetime.now().isoformat()))
        else:
            print(f"  {metric_name}: Not found in any source")
    
    conn.commit()
    conn.close()
    
    print("\n✅ Database updated!")


def main():
    """Main function."""
    print("="*80)
    print("Data Verification and Update with Priority Order")
    print("Priority: Zomato Report > Groww > Screener > MoneyControl")
    print("="*80)
    
    # Collect data from all sources
    DATA_SOURCES["zomato_report"] = extract_from_pdf()
    DATA_SOURCES["groww"] = scrape_groww()
    DATA_SOURCES["screener"] = scrape_screener()
    DATA_SOURCES["moneycontrol"] = scrape_moneycontrol()
    
    # Update database with best values
    update_database()
    
    # Verify final values
    print("\n" + "="*80)
    print("Final Database Values")
    print("="*80)
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT metric_name, metric_value, source 
        FROM financial_metrics 
        WHERE company_id = (SELECT id FROM companies WHERE symbol = 'ETERNAL')
        ORDER BY metric_name
    """)
    metrics = cursor.fetchall()
    conn.close()
    
    print("\nMetrics in database:")
    for name, value, source in metrics:
        if name == 'market_cap':
            print(f"  {name}: ₹{value:,.0f} Cr (from {source})")
        elif name == 'current_price':
            print(f"  {name}: ₹{value} (from {source})")
        else:
            print(f"  {name}: {value} (from {source})")


if __name__ == "__main__":
    main()


