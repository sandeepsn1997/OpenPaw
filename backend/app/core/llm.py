"""Groq LLM integration - https://console.groq.com/docs/overview"""

import json
import os
from typing import Any, Dict, List, Optional

try:
    from groq import Groq
except ImportError:
    raise ImportError("Groq SDK not installed. Install with: pip install groq")


class GroqLLM:
    """Groq LLM integration using official Groq API."""

    # Available Groq models
    MODELS = {
        "llama-70b": "llama-3.3-70b-versatile",
        "llama-8b": "llama-3.1-8b-instant",
        "gpt-oss": "openai/gpt-oss-120b",
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "llama-3.3-70b-versatile",
        temperature: float = 0.7,
        max_tokens: int = 2000,
    ):
        """
        Initialize Groq LLM client.
        
        Args:
            api_key: Groq API key (uses GROQ_API_KEY env var if not provided)
            model: Model name to use
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response
            
        Reference: https://console.groq.com/docs/overview
        """
        # Get API key from parameter or environment
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Groq API key not provided. "
                "Set GROQ_API_KEY environment variable or pass api_key parameter. "
                "Get your key from https://console.groq.com"
            )

        self.client = Groq(api_key=self.api_key)
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def generate(self, prompt: str, temperature: Optional[float] = None) -> str:
        """
        Generate text response using Groq.
        
        Args:
            prompt: Prompt text
            temperature: Override default temperature
        
        Returns:
            Generated text
            
        Reference: https://console.groq.com/docs/speech-text
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")

    def generate_structured(
        self,
        prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate structured JSON response using Groq.
        
        Args:
            prompt: Prompt text
            response_format: Optional JSON schema
        
        Returns:
            Parsed JSON response
        """
        try:
            # Add JSON instruction to prompt
            json_prompt = (
                f"{prompt}\n\n"
                "Respond with ONLY a valid JSON object, no other text or markdown."
            )

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": json_prompt,
                    }
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )

            content = response.choices[0].message.content

            # Try to parse JSON
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Extract JSON from response if wrapped in markdown
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                return json.loads(content.strip())

        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")

    def chat(self, messages: List[dict], temperature: Optional[float] = None) -> str:
        """
        Chat with conversation history using Groq.
        
        Args:
            messages: List of {"role": "user"/"assistant"/"system", "content": "..."} dicts
            temperature: Override default temperature
        
        Returns:
            Generated text response
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=self.max_tokens,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Groq API error: {str(e)}")

    def set_model(self, model: str) -> None:
        """Set model name. Available models: mixtral, llama2, gemma."""
        if model in self.MODELS:
            self.model = self.MODELS[model]
        else:
            self.model = model

    def set_temperature(self, temperature: float) -> None:
        """Set temperature (0-2)."""
        if not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
        self.temperature = temperature

    def set_max_tokens(self, max_tokens: int) -> None:
        """Set max tokens."""
        if max_tokens < 1:
            raise ValueError("Max tokens must be at least 1")
        self.max_tokens = max_tokens

    @staticmethod
    def get_available_models() -> Dict[str, str]:
        """Get available Groq models."""
        return GroqLLM.MODELS.copy()
