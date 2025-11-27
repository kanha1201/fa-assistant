"""FastAPI entrypoint for Vercel deployment."""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
import json
import sqlite3
import urllib.parse
import urllib.request
from pathlib import Path

# Add parent directory to path to import our modules
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set environment variable for Gemini API key if available in Vercel
if 'GEMINI_API_KEY' in os.environ:
    os.environ['GEMINI_API_KEY'] = os.environ['GEMINI_API_KEY']

# Load API key
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


def get_company_data():
    """Get company data from database."""
    if not DB_PATH.exists():
        # Return default data if DB doesn't exist
        return {
            "company_name": "Eternal Limited",
            "sector": "Online Services",
            "metrics": {},
            "text_data": ""
        }
    
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


def is_greeting(query):
    """Check if query is a greeting."""
    greetings = ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]
    return query.lower().strip() in greetings


def handle_greeting(query):
    """Handle greeting queries."""
    return "Hello, How can I help you today!"


def is_advisory_question(query):
    """Check if query is asking for investment advice."""
    advisory_keywords = [
        "should i buy", "should i sell", "should i invest",
        "is it a good buy", "is it worth buying", "should i purchase",
        "recommend", "advice", "what should i do"
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in advisory_keywords)


def is_predictive_question(query):
    """Check if query is asking for predictions."""
    predictive_keywords = [
        "target price", "future price", "will it go up", "will it go down",
        "predict", "forecast", "next month", "next year", "future performance"
    ]
    query_lower = query.lower()
    return any(keyword in query_lower for keyword in predictive_keywords)


def get_summary(company_symbol):
    """Get company summary."""
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
    
    prompt = f"""Provide a concise 3-4 line summary for {company_data['company_name']} based on the financial metrics and quarterly results.

{context}

Focus on:
- **Performance vs previous quarter/year**
- **Key drivers of performance**
- **Overall assessment**

Format: Use clear, jargon-free language. Use bullet points for key aspects. Bold important numbers and metrics. Ensure line breaks between points."""
    
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
    disclaimer = "\n\n*Generated by AI based on public data. Not a buy/sell recommendation. Please consult your financial advisor.*"
    response = response + disclaimer
    
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
    
    context += f"\nQuarterly Results:\n{company_data['text_data'][:1000]}"
    
    prompt = f"""Provide bull and bear case analysis for {company_data['company_name']}.

{context}

Format:
**🐂 BULL CASE:**

• [Point 1 with specific metrics]
• [Point 2 with specific metrics]
• [Point 3 with specific metrics]

**🐻 BEAR CASE:**

• [Point 1 with specific metrics]
• [Point 2 with specific metrics]
• [Point 3 with specific metrics]

Use neutral, professional language. Bold important numbers and metrics. Ensure line breaks between each point."""
    
    response = call_gemini_api(prompt)
    disclaimer = "\n\n*Generated by AI based on public data. Not a buy/sell recommendation. Please consult your financial advisor.*"
    response = response + disclaimer
    
    return {"bull_case": [], "bear_case": [], "full_response": response}


def answer_query(company_symbol, query):
    """Answer a query."""
    # Check guardrails
    if is_greeting(query):
        return {"answer": handle_greeting(query)}
    
    if is_advisory_question(query):
        return {"answer": "I cannot provide buy/sell recommendations or investment advice. However, I can help you analyze the company's financial metrics and performance. Please consult a qualified financial advisor for personalized investment advice."}
    
    if is_predictive_question(query):
        return {"answer": "I cannot predict future stock prices, market movements, or company performance. I can only analyze past performance, current financial metrics, and historical data. For future projections, please consult a qualified financial advisor."}
    
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
    
    return {"answer": answer}


app = FastAPI(title="Tensor API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Tensor API", "version": "1.0.0"}


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/summary")
async def summary(company_symbol: str = Query(default="ETERNAL")):
    """Get company summary."""
    return get_summary(company_symbol)


@app.get("/red-flags")
async def red_flags(company_symbol: str = Query(default="ETERNAL")):
    """Get red flags."""
    return get_red_flags(company_symbol)


@app.get("/bull-bear")
async def bull_bear(company_symbol: str = Query(default="ETERNAL")):
    """Get bull/bear case."""
    return get_bull_bear(company_symbol)


@app.get("/chat/query")
async def chat_query(
    query: str = Query(...),
    company_symbol: str = Query(default="ETERNAL")
):
    """Answer a chat query."""
    return answer_query(company_symbol, query)
