"""Text cleaning and normalization utilities."""
import re
from typing import List, Optional


class TextCleaner:
    """Clean and normalize text content."""
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text content."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep essential punctuation
        text = re.sub(r'[^\w\s\.\,\;\:\!\?\-\(\)\[\]\{\}\%\/\$\€\₹]', '', text)
        
        # Normalize newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def extract_numbers(text: str) -> List[float]:
        """Extract numeric values from text."""
        # Pattern to match numbers (including decimals and with commas)
        pattern = r'[\d,]+\.?\d*'
        matches = re.findall(pattern, text)
        
        numbers = []
        for match in matches:
            try:
                # Remove commas and convert to float
                num = float(match.replace(',', ''))
                numbers.append(num)
            except ValueError:
                continue
        
        return numbers
    
    @staticmethod
    def normalize_metric_name(name: str) -> str:
        """Normalize metric names for consistency."""
        if not name:
            return ""
        
        # Convert to lowercase
        name = name.lower().strip()
        
        # Replace common variations
        replacements = {
            'p/e': 'pe_ratio',
            'pe ratio': 'pe_ratio',
            'price to earnings': 'pe_ratio',
            'p/b': 'pb_ratio',
            'pb ratio': 'pb_ratio',
            'price to book': 'pb_ratio',
            'roe': 'return_on_equity',
            'return on equity': 'return_on_equity',
            'roce': 'return_on_capital_employed',
            'return on capital employed': 'return_on_capital_employed',
            'debt to equity': 'debt_to_equity',
            'd/e': 'debt_to_equity',
            'market cap': 'market_capitalization',
            'market capitalization': 'market_capitalization',
        }
        
        for key, value in replacements.items():
            if key in name:
                return value
        
        # Replace spaces and special chars with underscores
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', '_', name)
        
        return name
    
    @staticmethod
    def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Split text into chunks for processing."""
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                sentence_end = max(
                    text.rfind('.', start, end),
                    text.rfind('!', start, end),
                    text.rfind('?', start, end),
                    text.rfind('\n', start, end)
                )
                
                if sentence_end > start:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    @staticmethod
    def remove_html_tags(text: str) -> str:
        """Remove HTML tags from text."""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Decode HTML entities (basic)
        html_entities = {
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
        }
        
        for entity, char in html_entities.items():
            text = text.replace(entity, char)
        
        return text


text_cleaner = TextCleaner()


