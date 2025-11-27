#!/usr/bin/env python3
"""Minimal API server using built-in Python libraries."""
import sys
import os
import json
import sqlite3
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Import guardrails directly without triggering __init__.py
import importlib.util

# Load guardrails
guardrails_path = BASE_DIR / "src" / "llm" / "guardrails.py"
spec_guardrails = importlib.util.spec_from_file_location("guardrails", guardrails_path)
guardrails_module = importlib.util.module_from_spec(spec_guardrails)
spec_guardrails.loader.exec_module(guardrails_module)
guardrails = guardrails_module.guardrails

# Load Gemini client
gemini_client_path = BASE_DIR / "src" / "llm" / "gemini_client_urllib.py"
spec_gemini = importlib.util.spec_from_file_location("gemini_client_urllib", gemini_client_path)
gemini_module = importlib.util.module_from_spec(spec_gemini)
spec_gemini.loader.exec_module(gemini_module)

# Load API key
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    with open(ENV_FILE, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                os.environ[key.strip()] = value.strip()

DB_PATH = BASE_DIR / "data" / "financial_data.db"
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "ETERNAL"


def get_company_data():
    """Get company data from database."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    cursor.execute("SELECT name, sector FROM companies WHERE symbol = 'ETERNAL'")
    company = cursor.fetchone()
    
    cursor.execute("""
        SELECT metric_name, metric_value, period_type 
        FROM financial_metrics 
        WHERE company_id = (SELECT id FROM companies WHERE symbol = 'ETERNAL')
    """)
    metrics = {row[0]: {"value": row[1], "period": row[2]} for row in cursor.fetchall()}
    
    conn.close()
    
    text_data = ""
    txt_file = PROCESSED_PATH / "eternal_q2_fy26_sample.txt"
    if txt_file.exists():
        with open(txt_file, "r") as f:
            text_data = f.read()
    
    return {
        "company_name": company[0] if company else "Eternal Limited",
        "sector": company[1] if company else "Online Services",
        "metrics": metrics,
        "text_data": text_data
    }


def call_gemini_api(prompt):
    """Call Gemini API."""
    return gemini_module.call_gemini_api(prompt)


def get_summary(company_symbol):
    """Get summary."""
    company_data = get_company_data()
    context = f"""
Company: {company_data['company_name']}
Sector: {company_data['sector']}

Financial Metrics:
"""
    for metric_name, metric_info in company_data['metrics'].items():
        value = metric_info['value']
        if value is not None:
            context += f"- {metric_name}: {value}\n"
    
    context += f"\nQuarterly Results:\n{company_data['text_data'][:1000]}"
    
    prompt = f"""Provide a concise 3-4 line summary of {company_data['company_name']}'s quarterly results and fundamentals.

{context}

Format: Clear, jargon-free language with specific numbers."""
    
    response = call_gemini_api(prompt)
    return {"summary": response, "full_response": response}


def get_red_flags(company_symbol):
    """Get red flags."""
    company_data = get_company_data()
    context = f"""
Company: {company_data['company_name']}
Sector: {company_data['sector']}

Financial Metrics:
"""
    for metric_name, metric_info in company_data['metrics'].items():
        value = metric_info['value']
        if value is not None:
            context += f"- {metric_name}: {value}\n"
    
    prompt = f"""Identify potential red flags for {company_data['company_name']} based on the financial metrics.

{context}

List red flags with severity (High/Medium/Low). Use neutral language."""
    
    response = call_gemini_api(prompt)
    response = guardrails.ensure_neutral_tone(response)
    response = guardrails.add_disclaimer(response, "red_flags")
    
    return {"red_flags": [{"description": response}], "full_response": response}


def get_bull_bear(company_symbol):
    """Get bull/bear case."""
    company_data = get_company_data()
    context = f"""
Company: {company_data['company_name']}
Sector: {company_data['sector']}

Financial Metrics:
"""
    for metric_name, metric_info in company_data['metrics'].items():
        value = metric_info['value']
        if value is not None:
            context += f"- {metric_name}: {value}\n"
    
    prompt = f"""Provide bull and bear case analysis for {company_data['company_name']}.

{context}

Format:
BULL CASE:
- Point 1
- Point 2

BEAR CASE:
- Point 1
- Point 2

Use neutral, professional language."""
    
    response = call_gemini_api(prompt)
    response = guardrails.ensure_neutral_tone(response)
    response = guardrails.add_disclaimer(response, "bull_bear")
    
    return {"bull_case": [], "bear_case": [], "full_response": response}


def answer_query(company_symbol, query):
    """Answer a query."""
    # Check guardrails
    if guardrails.is_greeting(query):
        return {"answer": guardrails.handle_greeting(query)}
    
    if guardrails.is_advisory_question(query):
        return {"answer": guardrails.handle_advisory_refusal(query, {})}
    
    if guardrails.is_predictive_question(query):
        return {"answer": guardrails.handle_predictive_refusal(query)}
    
    company_data = get_company_data()
    context = f"""
Company: {company_data['company_name']}
Sector: {company_data['sector']}

Financial Metrics:
"""
    for metric_name, metric_info in company_data['metrics'].items():
        value = metric_info['value']
        if value is not None:
            context += f"- {metric_name}: {value}\n"
    
    context += f"\nQuarterly Results:\n{company_data['text_data'][:1000]}"
    
    prompt = f"""Answer this question about {company_data['company_name']}:

{context}

Question: {query}

Provide a clear, accurate answer. Use neutral language. Do not provide investment advice."""
    
    answer = call_gemini_api(prompt)
    answer = guardrails.ensure_neutral_tone(answer)
    
    return {"answer": answer}


class APIHandler(BaseHTTPRequestHandler):
    """HTTP request handler for API endpoints."""
    
    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_path = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # CORS headers
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
        
        try:
            # Health check
            if parsed_path.path == '/health':
                self.wfile.write(json.dumps({"status": "healthy"}).encode())
                return
            
            # Root
            if parsed_path.path == '/':
                self.wfile.write(json.dumps({"message": "Tensor API", "version": "1.0.0"}).encode())
                return
            
            company_symbol = query_params.get('company_symbol', ['ETERNAL'])[0]
            
            # Summary endpoint
            if parsed_path.path == '/summary':
                result = get_summary(company_symbol)
                self.wfile.write(json.dumps(result).encode())
                return
            
            # Red flags endpoint
            if parsed_path.path == '/red-flags':
                result = get_red_flags(company_symbol)
                self.wfile.write(json.dumps(result).encode())
                return
            
            # Bull/bear endpoint
            if parsed_path.path == '/bull-bear':
                result = get_bull_bear(company_symbol)
                self.wfile.write(json.dumps(result).encode())
                return
            
            # Chat query endpoint
            if parsed_path.path == '/chat/query':
                query = query_params.get('query', [''])[0]
                result = answer_query(company_symbol, query)
                self.wfile.write(json.dumps(result).encode())
                return
            
            # 404 for unknown paths
            self.send_response(404)
            self.wfile.write(json.dumps({"error": "Not found"}).encode())
            
        except Exception as e:
            self.send_response(500)
            self.wfile.write(json.dumps({"error": str(e)}).encode())
    
    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def run_server(port=8000):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, APIHandler)
    print(f"🚀 Tensor API Server running on http://localhost:{port}")
    print(f"✅ Health check: http://localhost:{port}/health")
    print("Press Ctrl+C to stop")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")
        httpd.shutdown()


if __name__ == "__main__":
    run_server(8000)

