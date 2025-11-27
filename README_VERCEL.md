# Vercel Deployment Guide

## Environment Variables

Set the following environment variable in Vercel:

1. Go to your Vercel project settings
2. Navigate to "Environment Variables"
3. Add: `GEMINI_API_KEY` with your Google Gemini API key value

## Deployment

The FastAPI app is configured at `api/index.py` which Vercel will automatically detect.

## API Endpoints

- `GET /` - Root endpoint
- `GET /health` - Health check
- `GET /summary?company_symbol=ETERNAL` - Get company summary
- `GET /red-flags?company_symbol=ETERNAL` - Get red flags
- `GET /bull-bear?company_symbol=ETERNAL` - Get bull/bear case
- `GET /chat/query?query=YOUR_QUESTION&company_symbol=ETERNAL` - Answer a query

## Requirements

All dependencies are listed in `requirements.txt`. Vercel will automatically install them during deployment.

