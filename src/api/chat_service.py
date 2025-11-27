"""Chat service API endpoints."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
from src.llm import LLMService
from src.utils import logger

app = FastAPI(title="Financial Analysis Chatbot API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_service = LLMService()


class QueryRequest(BaseModel):
    """Query request model."""
    company_symbol: str
    query: str


@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Financial Analysis Chatbot API", "version": "1.0.0"}


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/api/v1/companies/{company_symbol}/summary")
def get_quarterly_summary(company_symbol: str):
    """Get quarterly summary for a company."""
    try:
        result = llm_service.get_quarterly_summary(company_symbol.upper())
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Error in get_quarterly_summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/companies/{company_symbol}/bull-bear")
def get_bull_bear_case(company_symbol: str):
    """Get bull vs bear case for a company."""
    try:
        result = llm_service.get_bull_bear_case(company_symbol.upper())
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Error in get_bull_bear_case: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/companies/{company_symbol}/red-flags")
def get_red_flags(company_symbol: str):
    """Get red flags for a company."""
    try:
        result = llm_service.get_red_flags(company_symbol.upper())
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Error in get_red_flags: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/companies/{company_symbol}/benchmark")
def get_benchmark(company_symbol: str, metric_name: str):
    """Get benchmark comparison for a metric."""
    try:
        result = llm_service.get_benchmark(
            company_symbol.upper(),
            metric_name
        )
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_benchmark: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/chat/query")
def chat_query(request: QueryRequest):
    """Answer a general query about a company."""
    try:
        result = llm_service.answer_query(
            request.company_symbol.upper(),
            request.query
        )
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat_query: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Simplified endpoints for frontend
@app.get("/summary")
def get_summary(company_symbol: str):
    """Get quarterly summary (simplified endpoint)."""
    try:
        result = llm_service.get_quarterly_summary(company_symbol.upper())
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Error in get_summary: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/bull-bear")
def get_bull_bear(company_symbol: str):
    """Get bull vs bear case (simplified endpoint)."""
    try:
        result = llm_service.get_bull_bear_case(company_symbol.upper())
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Error in get_bull_bear: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/red-flags")
def get_red_flags_simple(company_symbol: str):
    """Get red flags (simplified endpoint)."""
    try:
        result = llm_service.get_red_flags(company_symbol.upper())
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except Exception as e:
        logger.error(f"Error in get_red_flags: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/chat/query")
def chat_query_get(company_symbol: str, query: str):
    """Answer a general query (GET endpoint for frontend)."""
    try:
        result = llm_service.answer_query(company_symbol.upper(), query)
        if "error" in result:
            raise HTTPException(status_code=404, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat_query_get: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

