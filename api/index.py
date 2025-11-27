"""FastAPI entrypoint for Vercel deployment."""
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import sys
import os
from pathlib import Path

# Add parent directory to path to import our modules
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR))

# Set environment variable for Gemini API key if available in Vercel
# Vercel environment variables are automatically available via os.environ
if 'GEMINI_API_KEY' in os.environ:
    # Ensure the .env file logic in run_api_standalone.py can use this
    os.environ['GEMINI_API_KEY'] = os.environ['GEMINI_API_KEY']

# Import functions from standalone API
try:
    from scripts.run_api_standalone import (
        get_summary,
        get_red_flags,
        get_bull_bear,
        answer_query
    )
except ImportError:
    # Fallback: import directly if scripts path doesn't work
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "run_api_standalone",
        BASE_DIR / "scripts" / "run_api_standalone.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    get_summary = module.get_summary
    get_red_flags = module.get_red_flags
    get_bull_bear = module.get_bull_bear
    answer_query = module.answer_query

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

