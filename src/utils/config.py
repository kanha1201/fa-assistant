"""Configuration management for the data ingestion pipeline."""
import os
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """Application settings."""
    
    # Database
    database_url: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/financial_data")
    
    # Vector Database
    vector_db_path: str = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
    
    # Storage Paths
    raw_data_path: str = os.getenv("RAW_DATA_PATH", "./data/raw")
    processed_data_path: str = os.getenv("PROCESSED_DATA_PATH", "./data/processed")
    documents_path: str = os.getenv("DOCUMENTS_PATH", "./data/documents")
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "./logs/ingestion.log")
    
    # Scraping Configuration
    request_timeout: int = int(os.getenv("REQUEST_TIMEOUT", "30"))
    retry_attempts: int = int(os.getenv("RETRY_ATTEMPTS", "3"))
    delay_between_requests: float = float(os.getenv("DELAY_BETWEEN_REQUESTS", "2"))
    
    # OCR Configuration
    tesseract_cmd: Optional[str] = os.getenv("TESSERACT_CMD")
    ocr_language: str = os.getenv("OCR_LANGUAGE", "eng")
    
    # User Agent for web scraping
    user_agent: str = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # LLM Configuration
    gemini_api_key: Optional[str] = os.getenv("GEMINI_API_KEY")
    gemini_temperature: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    gemini_max_tokens: Optional[int] = int(os.getenv("GEMINI_MAX_TOKENS", "0")) or None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Create directories
def setup_directories(settings: Settings):
    """Create necessary directories."""
    Path(settings.raw_data_path).mkdir(parents=True, exist_ok=True)
    Path(settings.processed_data_path).mkdir(parents=True, exist_ok=True)
    Path(settings.documents_path).mkdir(parents=True, exist_ok=True)
    Path(settings.vector_db_path).mkdir(parents=True, exist_ok=True)
    Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)


settings = Settings()
setup_directories(settings)

