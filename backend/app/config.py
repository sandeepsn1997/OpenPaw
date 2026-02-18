"""Application configuration."""

from typing import List
from pathlib import Path

from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application settings."""

    app_name: str = "OpenPaw Agent Server"
    version: str = "0.1.0"
    debug: bool = False
    
    # CORS settings
    cors_origins: List[str] = ["*"]
    cors_credentials: bool = True
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]
    
    # API settings
    api_prefix: str = "/api"
    
    # Groq LLM settings
    groq_api_key: str = ""
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000
    
    model_config = ConfigDict(
        env_file=str(Path(__file__).parent.parent.parent / ".env"),
        extra="ignore",
        protected_namespaces=(),
    )

settings = Settings()