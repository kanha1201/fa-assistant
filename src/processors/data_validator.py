"""Data validation utilities."""
from typing import Dict, List, Any, Optional
from datetime import datetime
from src.utils import logger


class DataValidator:
    """Validate extracted data."""
    
    def __init__(self):
        """Initialize validator."""
        self.logger = logger
    
    def validate_company_data(self, data: Dict[str, Any]) -> bool:
        """Validate company data structure."""
        required_fields = ["company_symbol", "source_url"]
        
        for field in required_fields:
            if field not in data:
                self.logger.warning(f"Missing required field: {field}")
                return False
        
        return True
    
    def validate_financial_metric(self, metric: Dict[str, Any]) -> bool:
        """Validate financial metric data."""
        required_fields = ["metric_name"]
        
        for field in required_fields:
            if field not in metric:
                self.logger.warning(f"Missing required field in metric: {field}")
                return False
        
        # Validate metric value if present
        if "metric_value" in metric and metric["metric_value"] is not None:
            try:
                float(metric["metric_value"])
            except (ValueError, TypeError):
                self.logger.warning(f"Invalid metric value: {metric.get('metric_value')}")
                return False
        
        return True
    
    def validate_document(self, document: Dict[str, Any]) -> bool:
        """Validate document data."""
        required_fields = ["content_text", "source_url", "document_type"]
        
        for field in required_fields:
            if field not in document:
                self.logger.warning(f"Missing required field in document: {field}")
                return False
        
        # Check if content is not empty
        if not document.get("content_text", "").strip():
            self.logger.warning("Document content is empty")
            return False
        
        return True
    
    def sanitize_text(self, text: str, max_length: int = 1000000) -> str:
        """Sanitize text content."""
        if not text:
            return ""
        
        # Truncate if too long
        if len(text) > max_length:
            self.logger.warning(f"Text truncated from {len(text)} to {max_length} characters")
            text = text[:max_length]
        
        return text
    
    def normalize_company_symbol(self, symbol: str) -> str:
        """Normalize company symbol."""
        if not symbol:
            return ""
        
        # Convert to uppercase and remove spaces
        symbol = symbol.upper().strip()
        
        # Remove special characters
        symbol = ''.join(c for c in symbol if c.isalnum() or c in ['-', '_'])
        
        return symbol


data_validator = DataValidator()


