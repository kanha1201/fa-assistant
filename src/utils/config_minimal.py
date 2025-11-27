"""Minimal configuration without external dependencies."""
import os
from pathlib import Path
from typing import Optional


class MinimalSettings:
    """Minimal settings using only built-in libraries."""
    
    def __init__(self):
        """Load settings from environment and .env file."""
        # Load .env file manually
        env_file = Path(".env")
        if env_file.exists():
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()
        
        # Database (use SQLite by default)
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./data/financial_data.db")
        
        # Vector Database
        self.vector_db_path = os.getenv("VECTOR_DB_PATH", "./data/vector_db")
        
        # Storage Paths
        self.raw_data_path = os.getenv("RAW_DATA_PATH", "./data/raw")
        self.processed_data_path = os.getenv("PROCESSED_DATA_PATH", "./data/processed")
        self.documents_path = os.getenv("DOCUMENTS_PATH", "./data/documents")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "./logs/ingestion.log")
        
        # LLM Configuration
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_temperature = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
        max_tokens = os.getenv("GEMINI_MAX_TOKENS", "")
        self.gemini_max_tokens = int(max_tokens) if max_tokens else None
        
        # User Agent
        self.user_agent = os.getenv("USER_AGENT", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36")
        
        # Create directories
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary directories."""
        Path(self.raw_data_path).mkdir(parents=True, exist_ok=True)
        Path(self.processed_data_path).mkdir(parents=True, exist_ok=True)
        Path(self.documents_path).mkdir(parents=True, exist_ok=True)
        Path(self.vector_db_path).mkdir(parents=True, exist_ok=True)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)


# Create singleton
settings = MinimalSettings()


