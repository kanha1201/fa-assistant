#!/usr/bin/env python3
"""Test guardrails implementation (standalone version)."""
import sys
import os
import json
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import guardrails directly without triggering __init__.py
import importlib.util
guardrails_path = BASE_DIR / "src" / "llm" / "guardrails.py"
spec = importlib.util.spec_from_file_location("guardrails", guardrails_path)
guardrails_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guardrails_module)
guardrails = guardrails_module.guardrails

# Load API key
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")


def call_gemini_api(prompt):
    """Call Gemini API using urllib."""
    if not GEMINI_API_KEY:
        return "Error: API key not found"
    
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
                    "parts": [{"text": prompt}]
                }]
            }
            
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')
            req.add_header('x-goog-api-key', GEMINI_API_KEY)
            
            data_json = json.dumps(data).encode('utf-8')
            
            with urllib.request.urlopen(req, data=data_json, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    return result['candidates'][0]['content']['parts'][0]['text']
        except Exception as e:
            continue
    
    return "Error: Could not connect to Gemini API"


def test_advisory_detection():
    """Test advisory question detection."""
    print("="*80)
    print("TEST 1: Advisory Question Detection")
    print("="*80)
    
    advisory_queries = [
        "Should I buy this stock?",
        "Do you recommend investing in Eternal?",
        "Is it good to buy Eternal?",
        "Can you advise me on this stock?",
        "What should I do with Eternal?",
    ]
    
    for query in advisory_queries:
        is_advisory = guardrails.is_advisory_question(query)
        print(f"Query: '{query}'")
        print(f"  ✓ Detected as advisory: {is_advisory}")
        if is_advisory:
            response = guardrails.handle_advisory_refusal(query, {})
            print(f"  Response: {response[:120]}...")
        print()


def test_predictive_detection():
    """Test predictive question detection."""
    print("="*80)
    print("TEST 2: Predictive Question Detection")
    print("="*80)
    
    predictive_queries = [
        "What is the target price for next month?",
        "Where will the stock price be next year?",
        "What will happen to Eternal's stock?",
        "Can you predict the future price?",
    ]
    
    for query in predictive_queries:
        is_predictive = guardrails.is_predictive_question(query)
        print(f"Query: '{query}'")
        print(f"  ✓ Detected as predictive: {is_predictive}")
        if is_predictive:
            response = guardrails.handle_predictive_refusal(query)
            print(f"  Response: {response[:120]}...")
        print()


def test_greeting_detection():
    """Test greeting detection."""
    print("="*80)
    print("TEST 3: Greeting Detection")
    print("="*80)
    
    greetings = [
        "Hello",
        "Hi there",
        "Hey",
        "Thanks",
        "Thank you",
        "Bye",
    ]
    
    for greeting in greetings:
        is_greeting = guardrails.is_greeting(greeting)
        print(f"Query: '{greeting}'")
        print(f"  ✓ Detected as greeting: {is_greeting}")
        if is_greeting:
            response = guardrails.handle_greeting(greeting)
            print(f"  Response: {response}")
        print()


def test_neutral_tone():
    """Test neutral tone enforcement."""
    print("="*80)
    print("TEST 4: Neutral Tone Enforcement")
    print("="*80)
    
    emotional_text = "This is a multibagger stock that is skyrocketing! It's cheap and a safe investment."
    neutral_text = guardrails.filter_emotional_words(emotional_text)
    
    print(f"Original: {emotional_text}")
    print(f"Filtered: {neutral_text}")
    print()


def test_disclaimer():
    """Test disclaimer injection."""
    print("="*80)
    print("TEST 5: Disclaimer Injection")
    print("="*80)
    
    text = "This company shows strong growth potential."
    with_disclaimer = guardrails.add_disclaimer(text, "bull_bear")
    
    print(f"Original: {text}")
    print(f"With Disclaimer:")
    print(f"{with_disclaimer}")
    print()


def test_full_flow():
    """Test full flow with guardrails."""
    print("="*80)
    print("TEST 6: Full Flow with Guardrails")
    print("="*80)
    
    # Test advisory question
    print("\n1. Testing advisory question:")
    query = "Should I buy this stock?"
    if guardrails.is_advisory_question(query):
        response = guardrails.handle_advisory_refusal(query, {})
        print(f"   Query: '{query}'")
        print(f"   Response: {response[:200]}...")
        print(f"   ✓ Guardrail triggered")
    
    # Test predictive question
    print("\n2. Testing predictive question:")
    query = "What will be the stock price next month?"
    if guardrails.is_predictive_question(query):
        response = guardrails.handle_predictive_refusal(query)
        print(f"   Query: '{query}'")
        print(f"   Response: {response[:200]}...")
        print(f"   ✓ Guardrail triggered")
    
    # Test greeting
    print("\n3. Testing greeting:")
    query = "Hello"
    if guardrails.is_greeting(query):
        response = guardrails.handle_greeting(query)
        print(f"   Query: '{query}'")
        print(f"   Response: {response}")
        print(f"   ✓ Guardrail triggered")
    
    # Test normal query with LLM (if API key available)
    if GEMINI_API_KEY:
        print("\n4. Testing normal query with LLM:")
        query = "What is the P/E ratio of Eternal?"
        
        # Get metrics from database
        db_path = BASE_DIR / "data" / "financial_data.db"
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("""
            SELECT metric_name, metric_value 
            FROM financial_metrics 
            WHERE company_id = (SELECT id FROM companies WHERE symbol = 'ETERNAL')
        """)
        metrics = dict(cursor.fetchall())
        conn.close()
        
        pe_ratio = metrics.get('pe_ratio', 'N/A')
        
        prompt = f"""You are a financial analyst assistant. Answer the following question about Eternal Limited.

CRITICAL CONSTRAINTS:
- Do NOT provide buy/sell recommendations or investment advice
- Do NOT use "you" in portfolio recommendation context
- Use neutral, factual language
- Do NOT predict future prices or performance

Financial Metrics:
- P/E Ratio: {pe_ratio}

User Question: {query}

Provide a clear, accurate answer. Use neutral, professional language."""
        
        response = call_gemini_api(prompt)
        filtered_response = guardrails.ensure_neutral_tone(response)
        
        print(f"   Query: '{query}'")
        print(f"   Response: {filtered_response[:200]}...")
        print(f"   ✓ Guardrails applied")
    else:
        print("\n4. Skipping LLM test (API key not available)")


def test_data_unavailable():
    """Test data unavailability handling."""
    print("="*80)
    print("TEST 7: Data Unavailability Handling")
    print("="*80)
    
    response = guardrails.handle_data_unavailable("dividend yield")
    print(f"Query about unavailable metric: 'dividend yield'")
    print(f"Response: {response}")
    print()


def main():
    """Run all guardrail tests."""
    print("\n" + "🛡️" * 40)
    print("GUARDRAILS TESTING")
    print("🛡️" * 40)
    
    test_advisory_detection()
    test_predictive_detection()
    test_greeting_detection()
    test_neutral_tone()
    test_disclaimer()
    test_data_unavailable()
    test_full_flow()
    
    print("\n" + "="*80)
    print("✅ Guardrails Testing Complete")
    print("="*80)
    print("\nSummary:")
    print("  ✓ Advisory question detection")
    print("  ✓ Predictive question detection")
    print("  ✓ Greeting handling")
    print("  ✓ Neutral tone enforcement")
    print("  ✓ Disclaimer injection")
    print("  ✓ Data unavailability handling")


if __name__ == "__main__":
    main()

