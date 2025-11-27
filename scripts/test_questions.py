#!/usr/bin/env python3
"""Test backend by answering specific questions."""
import sys
import os
import json
import sqlite3
import urllib.request
import urllib.parse
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "financial_data.db"
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "ETERNAL"

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


def get_company_data():
    """Get company data from database and files."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # Get company info
    cursor.execute("SELECT name, sector FROM companies WHERE symbol = 'ETERNAL'")
    company = cursor.fetchone()
    
    # Get metrics
    cursor.execute("""
        SELECT metric_name, metric_value, period_type 
        FROM financial_metrics 
        WHERE company_id = (SELECT id FROM companies WHERE symbol = 'ETERNAL')
    """)
    metrics = {row[0]: {"value": row[1], "period": row[2]} for row in cursor.fetchall()}
    
    conn.close()
    
    # Get text data from files
    text_data = ""
    txt_file = PROCESSED_PATH / "eternal_q2_fy26_sample.txt"
    if txt_file.exists():
        with open(txt_file, "r") as f:
            text_data = f.read()
    
    json_file = PROCESSED_PATH / "screener_eternal_sample.json"
    json_data = {}
    if json_file.exists():
        with open(json_file, "r") as f:
            json_data = json.load(f)
    
    return {
        "company_name": company[0] if company else "Eternal Limited",
        "sector": company[1] if company else "Online Services",
        "metrics": metrics,
        "text_data": text_data,
        "json_data": json_data
    }


def call_gemini_api(prompt, context=""):
    """Call Gemini API using urllib with correct endpoint."""
    if not GEMINI_API_KEY:
        return "Error: API key not found"
    
    # Correct model names and endpoint format
    models_to_try = [
        "gemini-2.5-flash",
        "gemini-1.5-flash-latest",
        "gemini-1.5-pro-latest",
        "gemini-pro"
    ]
    
    full_prompt = f"{context}\n\nQuestion: {prompt}\n\nAnswer:" if context else prompt
    
    base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    for model in models_to_try:
        try:
            # Correct endpoint format: /models/{model}:generateContent
            url = f"{base_url}/models/{model}:generateContent"
            
            data = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }]
            }
            
            req = urllib.request.Request(url)
            req.add_header('Content-Type', 'application/json')
            req.add_header('x-goog-api-key', GEMINI_API_KEY)  # Correct header format
            
            data_json = json.dumps(data).encode('utf-8')
            
            with urllib.request.urlopen(req, data=data_json, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    print(f"✓ Successfully used model: {model}")
                    return text
                else:
                    raise Exception("No candidates in response")
        
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_body)
                error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                if e.code == 404 or 'not found' in error_msg.lower():
                    continue  # Try next model
                else:
                    return f"API Error {e.code}: {error_msg}"
            except:
                if e.code == 404:
                    continue
                return f"HTTP Error {e.code}: {e.reason}"
        
        except Exception as e:
            if "Successfully used" in str(e):
                return str(e).split("Successfully used")[1]
            continue
    
    return f"Error: Could not connect to Gemini API with any model. Please check API key and network connectivity."


def answer_question(question_num, question, company_data):
    """Answer a specific question."""
    print(f"\n{'='*80}")
    print(f"Question {question_num}: {question}")
    print(f"{'='*80}")
    
    context = f"""
Company Information:
- Name: {company_data['company_name']}
- Sector: {company_data['sector']}

Financial Metrics:
"""
    
    for metric_name, metric_info in company_data['metrics'].items():
        context += f"- {metric_name}: {metric_info['value']}\n"
    
    context += f"\nQuarterly Results Summary:\n{company_data['text_data'][:1000]}"
    
    # Customize prompt based on question type
    if "stock price" in question.lower():
        prompt = f"{question}\n\nUse the financial data provided. If exact stock price is not available, mention that and provide related information like market cap or other valuation metrics."
    elif "market cap" in question.lower():
        prompt = f"{question}\n\nUse the financial metrics provided."
    elif "p/e ratio" in question.lower() or "compare" in question.lower():
        prompt = f"{question}\n\nProvide the P/E ratio from the metrics. For sector comparison, note that sector benchmark data may be limited, but provide context about what a good P/E ratio typically is for this sector."
    elif "summarise" in question.lower() or "fundamentals" in question.lower():
        prompt = f"{question}\n\nProvide a comprehensive summary based on the quarterly results and financial metrics provided."
    elif "bear" in question.lower() or "bull" in question.lower():
        prompt = f"{question}\n\nProvide balanced bull and bear cases based on the financial data and quarterly results."
    elif "red flags" in question.lower():
        prompt = f"{question}\n\nAnalyze the financial metrics and quarterly results to identify potential concerns or red flags."
    elif "debt" in question.lower():
        prompt = f"{question}\n\nUse the Debt to Equity ratio from the financial metrics provided."
    else:
        prompt = question
    
    answer = call_gemini_api(prompt, context)
    print(f"\nAnswer:\n{answer}\n")
    return answer


def main():
    """Run all questions."""
    print("\n" + "🚀" * 40)
    print("BACKEND TESTING - Answering Questions")
    print("🚀" * 40)
    
    if not GEMINI_API_KEY:
        print("\n❌ Error: GEMINI_API_KEY not found in .env file")
        return
    
    # Get company data
    print("\nLoading company data...")
    company_data = get_company_data()
    print(f"✓ Loaded data for {company_data['company_name']}")
    print(f"✓ Found {len(company_data['metrics'])} metrics")
    
    # Questions
    questions = [
        "What is the stock price of Eternal?",
        "What is the Market Cap of Eternal?",
        "What is the P/E ratio of Eternal? Compare this with the other players of the same sector.",
        "Summarise the fundamentals of Eternal.",
        "Give me a bear and bull opinion description of Eternal.",
        "Highlight the red flags of Eternal.",
        "What is the Debt to Equity Ratio of Eternal?"
    ]
    
    answers = {}
    
    for i, question in enumerate(questions, 1):
        try:
            answer = answer_question(i, question, company_data)
            answers[i] = answer
        except Exception as e:
            print(f"\n❌ Error answering question {i}: {e}")
            answers[i] = f"Error: {str(e)}"
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    successful = sum(1 for a in answers.values() if not a.startswith("Error"))
    total = len(answers)
    
    print(f"\nQuestions answered: {successful}/{total}")
    
    if successful == total:
        print("\n✅ All questions answered successfully!")
    else:
        print(f"\n⚠️  {total - successful} question(s) had errors")
    
    # Save answers
    output_file = BASE_DIR / "data" / "processed" / "test_answers.json"
    with open(output_file, "w") as f:
        json.dump({
            "questions": {i: q for i, q in enumerate(questions, 1)},
            "answers": answers,
            "timestamp": str(Path(__file__).stat().st_mtime)
        }, f, indent=2)
    
    print(f"\n✓ Answers saved to: {output_file}")


if __name__ == "__main__":
    main()

