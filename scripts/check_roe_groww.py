#!/usr/bin/env python3
"""Check ROE value specifically from Groww website."""
import urllib.request
import re

url = "https://groww.in/stocks/zomato-ltd"

try:
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
    
    with urllib.request.urlopen(req, timeout=30) as response:
        html = response.read().decode('utf-8')
        
        # Save HTML for inspection
        with open('/tmp/groww_page.html', 'w') as f:
            f.write(html)
        print("✓ Saved HTML to /tmp/groww_page.html")
        
        # Try multiple patterns for ROE
        roe_patterns = [
            r'ROE[^<]*?(\d+\.?\d*)%?',
            r'Return.*on.*Equity[^<]*?(\d+\.?\d*)%?',
            r'\"roe\"[^:]*?:\s*(\d+\.?\d*)',
            r'roe[^:]*?:\s*(\d+\.?\d*)',
            r'ROE.*?(\d+\.?\d*)',
        ]
        
        print("\nSearching for ROE...")
        for i, pattern in enumerate(roe_patterns):
            matches = re.findall(pattern, html, re.IGNORECASE)
            if matches:
                print(f"Pattern {i+1} found matches: {matches[:5]}")
                for match in matches:
                    try:
                        value = float(match)
                        if 0 < value < 100:
                            print(f"  ✓ Potential ROE value: {value}%")
                    except:
                        pass
        
        # Look for common financial metrics sections
        print("\nLooking for financial metrics sections...")
        metric_sections = re.findall(r'(?:ROE|Return.*Equity|roe)[^<]{0,200}', html, re.IGNORECASE)
        for section in metric_sections[:5]:
            print(f"  Found: {section[:100]}...")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()


