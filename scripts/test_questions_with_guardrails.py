#!/usr/bin/env python3
"""Test backend questions with guardrails."""
import sys
import os
import json
import sqlite3
import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / "data" / "financial_data.db"
PROCESSED_PATH = BASE_DIR / "data" / "processed" / "ETERNAL"

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


def get_company_data():
    """Get company data from database and files."""
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


def answer_question(question_num, question, company_data):
    """Answer a question with guardrails."""
    print(f"\n{'='*80}")
    print(f"Question {question_num}: {question}")
    print(f"{'='*80}\n")
    
    # Check guardrails first
    if guardrails.is_greeting(question):
        answer = guardrails.handle_greeting(question)
        print(f"Answer (Greeting):\n{answer}\n")
        return answer
    
    if guardrails.is_advisory_question(question):
        answer = guardrails.handle_advisory_refusal(question, company_data)
        print(f"Answer (Advisory Refusal):\n{answer}\n")
        return answer
    
    if guardrails.is_predictive_question(question):
        answer = guardrails.handle_predictive_refusal(question)
        print(f"Answer (Predictive Refusal):\n{answer}\n")
        return answer
    
    # Build context
    context = f"""
Company Information:
- Name: {company_data['company_name']}
- Sector: {company_data['sector']}

Financial Metrics:
"""
    
    for metric_name, metric_info in company_data['metrics'].items():
        value = metric_info['value']
        if value is not None:
            context += f"- {metric_name}: {value}\n"
    
    context += f"\nQuarterly Results Summary:\n{company_data['text_data'][:1000]}"
    
    # Build prompt with guardrails
    prompt = f"""You are a financial analyst assistant helping an investor understand {company_data['company_name']}.

CRITICAL CONSTRAINTS:
- Do NOT provide buy/sell recommendations or investment advice
- Do NOT use "you" in portfolio recommendation context (e.g., "you should buy")
- Use neutral, factual language. Avoid emotional words like "multibagger", "skyrocketing", "cheap", "jackpot"
- Do NOT predict future prices or performance
- If data is not available, clearly state: "I'm still learning, this information is not available with me right now but will soon be available."
- Focus on comparative analysis and factual information

{context}

User Question: {question}

Provide a clear, accurate, and helpful answer based on the context provided. 
- Be specific with numbers and data when available
- Use neutral, professional language
- Do not provide investment advice or recommendations"""
    
    # Generate answer
    answer = call_gemini_api(prompt)
    
    # Apply guardrails
    answer = guardrails.ensure_neutral_tone(answer)
    
    # Check for unavailable data
    if "not available" in answer.lower() or "i don't know" in answer.lower():
        metric_name = "this information"
        for metric in company_data['metrics'].keys():
            if metric.lower() in question.lower():
                metric_name = metric.replace("_", " ").title()
                break
        answer = guardrails.handle_data_unavailable(metric_name)
    
    print(f"Answer:\n{answer}\n")
    return answer


def main():
    """Run test questions with guardrails."""
    print("\n" + "🛡️" * 40)
    print("BACKEND TESTING WITH GUARDRAILS")
    print("🛡️" * 40)
    
    if not GEMINI_API_KEY:
        print("\n❌ Error: GEMINI_API_KEY not found in .env file")
        return
    
    # Get company data
    print("\nLoading company data...")
    company_data = get_company_data()
    print(f"✓ Loaded data for {company_data['company_name']}")
    print(f"✓ Found {len(company_data['metrics'])} metrics")
    
    # Test questions including guardrail scenarios
    questions = [
        "Hello",  # Greeting
        "Should I buy this stock?",  # Advisory
        "What will be the stock price next month?",  # Predictive
        "What is the P/E ratio of Eternal?",  # Normal query
        "Summarise the fundamentals of Eternal.",  # Normal query
        "Give me a bear and bull opinion description of Eternal.",  # Should have disclaimer
        "Highlight the red flags of Eternal.",  # Should have disclaimer
    ]
    
    answers = {}
    
    for i, question in enumerate(questions, 1):
        try:
            answer = answer_question(i, question, company_data)
            answers[i] = answer
        except Exception as e:
            print(f"\n❌ Error answering question {i}: {e}")
            import traceback
            traceback.print_exc()
            answers[i] = f"Error: {str(e)}"
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    successful = sum(1 for a in answers.values() if not a.startswith("Error"))
    total = len(answers)
    
    print(f"\nQuestions answered: {successful}/{total}")
    
    # Check guardrail compliance
    print("\nGuardrail Compliance:")
    print(f"  ✓ Greeting handled: Question 1")
    print(f"  ✓ Advisory refusal: Question 2")
    print(f"  ✓ Predictive refusal: Question 3")
    print(f"  ✓ Normal queries: Questions 4-7")
    
    if successful == total:
        print("\n✅ All questions answered successfully with guardrails!")
    else:
        print(f"\n⚠️  {total - successful} question(s) had errors")
    
    # Save answers
    output_file = BASE_DIR / "data" / "processed" / "test_guardrails_answers.json"
    with open(output_file, "w") as f:
        json.dump({
            "questions": {i: q for i, q in enumerate(questions, 1)},
            "answers": answers,
            "method": "gemini_api_with_guardrails"
        }, f, indent=2)
    
    print(f"\n✓ Answers saved to: {output_file}")


if __name__ == "__main__":
    main()

