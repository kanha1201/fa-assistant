"""File storage utilities for raw and processed data."""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
from src.utils import logger, settings


class FileStorage:
    """Handle file storage for raw and processed data."""
    
    def __init__(self):
        """Initialize file storage."""
        self.raw_path = Path(settings.raw_data_path)
        self.processed_path = Path(settings.processed_data_path)
        self.documents_path = Path(settings.documents_path)
        self.logger = logger
        
        # Ensure directories exist
        self.raw_path.mkdir(parents=True, exist_ok=True)
        self.processed_path.mkdir(parents=True, exist_ok=True)
        self.documents_path.mkdir(parents=True, exist_ok=True)
    
    def save_json(self, data: Dict[str, Any], filename: str, subdirectory: Optional[str] = None) -> Path:
        """Save data as JSON file."""
        if subdirectory:
            save_path = self.processed_path / subdirectory / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            save_path = self.processed_path / filename
        
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        
        self.logger.debug(f"Saved JSON to {save_path}")
        return save_path
    
    def save_text(self, text: str, filename: str, subdirectory: Optional[str] = None) -> Path:
        """Save text content to file."""
        if subdirectory:
            save_path = self.processed_path / subdirectory / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            save_path = self.processed_path / filename
        
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)
        
        self.logger.debug(f"Saved text to {save_path}")
        return save_path
    
    def save_raw_data(self, data: bytes, filename: str, subdirectory: Optional[str] = None) -> Path:
        """Save raw binary data."""
        if subdirectory:
            save_path = self.raw_path / subdirectory / filename
            save_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            save_path = self.raw_path / filename
        
        with open(save_path, "wb") as f:
            f.write(data)
        
        self.logger.debug(f"Saved raw data to {save_path}")
        return save_path
    
    def load_json(self, filename: str, subdirectory: Optional[str] = None) -> Dict[str, Any]:
        """Load JSON file."""
        if subdirectory:
            load_path = self.processed_path / subdirectory / filename
        else:
            load_path = self.processed_path / filename
        
        with open(load_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def get_document_path(self, filename: str) -> Path:
        """Get path for document storage."""
        return self.documents_path / filename
    
    def save_extraction_result(self, source: str, data: Dict[str, Any], 
                              company_symbol: str = "ETERNAL") -> Dict[str, Path]:
        """Save extraction result with organized structure."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_paths = {}
        
        # Save main data as JSON
        json_filename = f"{company_symbol}_{source}_{timestamp}.json"
        saved_paths["json"] = self.save_json(data, json_filename, company_symbol)
        
        # Save text content if available
        if "text" in data or "full_text" in data:
            text_content = data.get("text") or data.get("full_text", "")
            text_filename = f"{company_symbol}_{source}_{timestamp}.txt"
            saved_paths["text"] = self.save_text(text_content, text_filename, company_symbol)
        
        return saved_paths


# Initialize file storage
file_storage = FileStorage()


