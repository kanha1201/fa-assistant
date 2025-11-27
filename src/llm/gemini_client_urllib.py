"""Gemini API client using urllib (no external packages needed)."""
import json
import urllib.request
import urllib.parse
from typing import List, Dict, Optional
from src.utils.logger_minimal import logger


class GeminiClientURLLib:
    """Client for Gemini API using urllib only."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client."""
        from src.utils.config_minimal import settings
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY in environment or .env file")
        
        # Try different model endpoints in order of preference
        self.models = [
            "gemini-2.5-flash",
            "gemini-1.5-flash-latest",
            "gemini-1.5-pro-latest",
            "gemini-pro"
        ]
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.logger = logger
    
    def _call_api(self, prompt: str, model: Optional[str] = None) -> Dict:
        """Call Gemini API with a specific model."""
        model_name = model or self.models[0]
        url = f"{self.base_url}/models/{model_name}:generateContent"
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        req = urllib.request.Request(url)
        req.add_header('Content-Type', 'application/json')
        req.add_header('x-goog-api-key', self.api_key)
        
        data_json = json.dumps(data).encode('utf-8')
        
        try:
            with urllib.request.urlopen(req, data=data_json, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_body)
                raise Exception(f"API Error {e.code}: {error_data.get('error', {}).get('message', e.reason)}")
            except:
                raise Exception(f"API Error {e.code}: {e.reason}")
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """Generate text using Gemini.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (None for default)
        
        Returns:
            Generated text
        """
        # Add generation config if needed
        full_prompt = prompt
        if temperature != 0.7:
            # Note: Temperature and max_tokens would need to be in request body
            # For now, we'll use default settings
            pass
        
        # Try each model until one works
        last_error = None
        for model in self.models:
            try:
                result = self._call_api(full_prompt, model)
                
                if 'candidates' in result and len(result['candidates']) > 0:
                    text = result['candidates'][0]['content']['parts'][0]['text']
                    self.logger.debug(f"Successfully used model: {model}")
                    return text
                else:
                    raise Exception("No candidates in response")
            
            except Exception as e:
                last_error = e
                self.logger.debug(f"Model {model} failed: {e}")
                continue
        
        # If all models failed
        raise Exception(f"All models failed. Last error: {last_error}")
    
    def generate_with_context(self, prompt: str, context: List[str], 
                             temperature: float = 0.7) -> str:
        """Generate text with context for RAG.
        
        Args:
            prompt: User prompt
            context: List of context documents
            temperature: Sampling temperature
        
        Returns:
            Generated text
        """
        # Combine context and prompt
        context_text = "\n\n---\n\n".join(context)
        full_prompt = f"""Context Information:
{context_text}

Based on the above context, please answer the following question:
{prompt}

Provide a clear, accurate, and helpful response based only on the context provided."""
        
        return self.generate(full_prompt, temperature=temperature)
    
    def chat(self, messages: List[Dict[str, str]], temperature: float = 0.7) -> str:
        """Chat with context from conversation history.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
        
        Returns:
            Assistant response
        """
        # Format messages for Gemini
        chat_prompt = ""
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role == "user":
                chat_prompt += f"User: {content}\n\n"
            elif role == "assistant":
                chat_prompt += f"Assistant: {content}\n\n"
        
        chat_prompt += "Assistant:"
        
        return self.generate(chat_prompt, temperature=temperature)


