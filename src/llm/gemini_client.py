"""Gemini API client for LLM integration."""
import google.generativeai as genai
from typing import List, Dict, Optional, Any
from src.utils import logger, settings


class GeminiClient:
    """Client for interacting with Google Gemini API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client."""
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise ValueError("Gemini API key not provided. Set GEMINI_API_KEY in environment or .env file")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        self.logger = logger
    
    def generate(self, prompt: str, temperature: float = 0.7, max_tokens: Optional[int] = None) -> str:
        """Generate text using Gemini.
        
        Args:
            prompt: Input prompt
            temperature: Sampling temperature (0.0 to 1.0)
            max_tokens: Maximum tokens to generate (None for default)
        
        Returns:
            Generated text
        """
        try:
            generation_config = {
                "temperature": temperature,
            }
            if max_tokens:
                generation_config["max_output_tokens"] = max_tokens
            
            response = self.model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            return response.text
        
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}", exc_info=True)
            raise
    
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


