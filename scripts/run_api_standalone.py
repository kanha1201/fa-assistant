#!/usr/bin/env python3
"""Standalone API server using only built-in Python libraries."""
import sys
import os
import json
import sqlite3
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent

# Load API key - check environment variables first (for Vercel), then .env file
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    ENV_FILE = BASE_DIR / ".env"
    if ENV_FILE.exists():
        with open(ENV_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if key.strip() == "GEMINI_API_KEY":
                        GEMINI_API_KEY = value.strip()
                        break

DB_PATH = BASE_DIR / "data" / "financial_data.db"
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "ETERNAL"


def call_gemini_api(prompt):
    """Call Gemini API using urllib."""
    if not GEMINI_API_KEY:
        return None  # Return None to indicate error
    
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
                elif 'error' in result:
                    # API returned an error - try next model
                    continue
        except urllib.error.HTTPError:
            # HTTP error - try next model
            continue
        except Exception:
            # Any other error - try next model
            continue
    
    # All models failed - return None to indicate error
    return None


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


def is_advisory_question(query):
    """Check if query is asking for investment advice."""
    import re
    query_lower = query.lower()
    patterns = [
        r"should i (buy|sell|invest|purchase)",
        r"do you (recommend|suggest|advise)",
        r"is it (good|bad|worth) (to|for) (buy|sell|invest)",
        r"would you (buy|sell|invest)",
    ]
    for pattern in patterns:
        if re.search(pattern, query_lower):
            return True
    return False


def is_predictive_question(query):
    """Check if query is asking for predictions."""
    import re
    query_lower = query.lower()
    patterns = [
        r"(target|future|next|tomorrow|next month|next year|will|forecast|prediction)",
        r"what (will|would) (happen|be|price)",
    ]
    for pattern in patterns:
        if re.search(pattern, query_lower):
            return True
    return False


def is_greeting(query):
    """Check if query is a greeting or non-financial conversational question."""
    import re
    query_lower = query.strip().lower()
    
    # Exact greeting patterns
    greeting_patterns = [
        r"^(hi|hello|hey|greetings)$",
        r"^(thanks|thank you|thx)$",
        r"^(bye|goodbye|see you)$",
    ]
    for pattern in greeting_patterns:
        if re.match(pattern, query_lower):
            return True
    
    # Conversational questions (non-financial)
    conversational_patterns = [
        r"^how are you",
        r"^how do you do",
        r"^what's up",
        r"^whats up",
        r"^how's it going",
        r"^how is it going",
        r"^how are things",
        r"^what are you",
        r"^who are you",
        r"^tell me about yourself",
    ]
    for pattern in conversational_patterns:
        if re.match(pattern, query_lower):
            return True
    
    return False


def handle_greeting(query):
    """Handle greeting queries."""
    query_lower = query.strip().lower()
    if query_lower.startswith(('hi', 'hello', 'hey')):
        return "Hello! How can I help you today? I can assist you with analyzing Eternal Limited's financial data, including fundamentals, metrics, and quarterly results."
    elif query_lower.startswith(('thanks', 'thank')):
        return "You're welcome! Feel free to ask if you need any more information."
    elif query_lower.startswith(('bye', 'goodbye')):
        return "Goodbye! Feel free to return if you have more questions."
    return "Hello! How can I help you today?"


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
    
    prompt = f"""Provide a concise, well-structured summary of {company_data['company_name']}'s quarterly results and fundamentals.

{context}

Format the response with:
- Clear headings in bold
- Bullet points for key metrics
- Line breaks between sections and new points
- Bold important numbers and percentages
- Start each new point on a new line
- Use structure like:

**Performance Overview:**

• Revenue: [number] (YoY growth)

• EBITDA: [number] (change)

**Key Metrics:**

• P/E Ratio: [number]

• ROE: [number]

**Analysis:**

[Brief assessment - each sentence on new line]

Use clear, jargon-free language with specific numbers. Add line breaks when starting a new point."""
    
    response = call_gemini_api(prompt)
    if response is None:
        return {"summary": "Unable to answer this right now. Please try again.", "full_response": "Unable to answer this right now. Please try again.", "has_financial_context": False}
    
    sources = [
        {"name": "Eternal Q2 FY2026 Report", "url": "https://b.zmtcdn.com/investor-relations/Eternal_Shareholders_Letter_Q2FY26_Results.pdf"},
        {"name": "Groww", "url": "https://groww.in/stocks/zomato-ltd"},
        {"name": "Screener", "url": "https://www.screener.in/company/ETERNAL/consolidated/"},
        {"name": "MoneyControl", "url": "https://www.moneycontrol.com/india/stockpricequote/online-services/eternal/Z"}
    ]
    return {"summary": response, "full_response": response, "has_financial_context": True, "sources": sources}


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

Format the response with:
- Clear headings in bold
- Bullet points for each red flag
- Severity indicators (High/Medium/Low)
- Bold important metrics
- Line breaks between each red flag
- Start each new point on a new line
- Use structure like:

**Red Flags:**

• **[Flag Name]** (High/Medium/Low)

[Description with specific metrics]

• **[Flag Name]** (High/Medium/Low)

[Description with specific metrics]

Use neutral language and be specific with numbers. Add line breaks when starting a new point."""
    
    response = call_gemini_api(prompt)
    if response is None:
        return {"red_flags": [{"description": "Unable to answer this right now. Please try again."}], "full_response": "Unable to answer this right now. Please try again.", "has_financial_context": False}
    
    disclaimer = "\n\n*Generated by AI based on public data. Not a buy/sell recommendation. Please consult your financial advisor.*"
    response = response + disclaimer
    
    sources = [
        {"name": "Eternal Q2 FY2026 Report", "url": "https://b.zmtcdn.com/investor-relations/Eternal_Shareholders_Letter_Q2FY26_Results.pdf"},
        {"name": "Groww", "url": "https://groww.in/stocks/zomato-ltd"},
        {"name": "Screener", "url": "https://www.screener.in/company/ETERNAL/consolidated/"},
        {"name": "MoneyControl", "url": "https://www.moneycontrol.com/india/stockpricequote/online-services/eternal/Z"}
    ]
    
    return {"red_flags": [{"description": response}], "full_response": response, "has_financial_context": True, "sources": sources}


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

Format the response with clear structure:

**BULL CASE:**

• [Point 1 with specific metrics]

• [Point 2 with specific metrics]

• [Point 3 with specific metrics]

**BEAR CASE:**

• [Point 1 with specific metrics]

• [Point 2 with specific metrics]

• [Point 3 with specific metrics]

Use neutral, professional language. Bold important numbers and metrics. Add line breaks between each point."""
    
    response = call_gemini_api(prompt)
    if response is None:
        return {"bull_case": [], "bear_case": [], "full_response": "Unable to answer this right now. Please try again.", "has_financial_context": False}
    
    disclaimer = "\n\n*Generated by AI based on public data. Not a buy/sell recommendation. Please consult your financial advisor.*"
    response = response + disclaimer
    
    sources = [
        {"name": "Eternal Q2 FY2026 Report", "url": "https://b.zmtcdn.com/investor-relations/Eternal_Shareholders_Letter_Q2FY26_Results.pdf"},
        {"name": "Groww", "url": "https://groww.in/stocks/zomato-ltd"},
        {"name": "Screener", "url": "https://www.screener.in/company/ETERNAL/consolidated/"},
        {"name": "MoneyControl", "url": "https://www.moneycontrol.com/india/stockpricequote/online-services/eternal/Z"}
    ]
    
    return {"bull_case": [], "bear_case": [], "full_response": response, "has_financial_context": True, "sources": sources}


def answer_query(company_symbol, query):
    """Answer a query."""
    # Check guardrails
    if is_greeting(query):
        return {"answer": handle_greeting(query), "has_financial_context": False}
    
    if is_advisory_question(query):
        return {"answer": "I cannot provide buy/sell recommendations or investment advice. However, I can help you analyze the company's financial metrics and performance. Please consult a qualified financial advisor for personalized investment advice.", "has_financial_context": False}
    
    if is_predictive_question(query):
        return {"answer": "I cannot predict future stock prices, market movements, or company performance. I can only analyze past performance, current financial metrics, and historical data. For future projections, please consult a qualified financial advisor.", "has_financial_context": False}
    
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

Provide a clear, accurate, direct answer. 

For simple factual questions (like "What is the stock price?" or "What is the P/E ratio?"), answer directly without headings or section titles. Just state the answer clearly with the key metric in bold.

For complex questions requiring multiple points, use:
- Bullet points for lists
- Bold important numbers and metrics
- Line breaks between sections and new points
- Start each new point on a new line

Do NOT:
- Start with "Answer:" - start directly with the response
- Add headings like "Stock Price:" or "P/E Ratio:" for simple questions
- Use section headers for single-answer questions

Example for simple question:
"The current stock price of Eternal Limited is **307.0**."

Example for complex question:
**Performance Overview:**

• Revenue increased by **20%** to **₹500 Cr**

• Profit margin improved to **15%**

Use neutral language. Do not provide investment advice. Add line breaks when starting a new point."""
    
    answer = call_gemini_api(prompt)
    
    # If API call failed, return user-friendly error
    if answer is None:
        return {"answer": "Unable to answer this right now. Please try again.", "has_financial_context": False}
    
    # Define source URLs based on data sources
    sources = [
        {"name": "Eternal Q2 FY2026 Report", "url": "https://b.zmtcdn.com/investor-relations/Eternal_Shareholders_Letter_Q2FY26_Results.pdf"},
        {"name": "Groww", "url": "https://groww.in/stocks/zomato-ltd"},
        {"name": "Screener", "url": "https://www.screener.in/company/ETERNAL/consolidated/"},
        {"name": "MoneyControl", "url": "https://www.moneycontrol.com/india/stockpricequote/online-services/eternal/Z"}
    ]
    
    return {"answer": answer, "has_financial_context": True, "sources": sources}


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
            error_msg = {"error": str(e)}
            self.wfile.write(json.dumps(error_msg).encode())
    
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

