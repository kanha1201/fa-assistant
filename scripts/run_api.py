"""Run the chat service API."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import uvicorn
from src.api.chat_service import app
from src.utils import logger

if __name__ == "__main__":
    logger.info("Starting Financial Analysis Chatbot API...")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


