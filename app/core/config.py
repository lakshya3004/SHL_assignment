import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings and configuration management.
    Uses pydantic-settings for validation and type-safe access to environment variables.
    """
    
    # API Configuration
    PROJECT_NAME: str = "SHL Assessment Recommender"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = False
    
    # LLM Configuration
    # We use a generic OpenAI-compatible structure to allow flexibility in providers
    OPENAI_API_KEY: str = "placeholder"
    OPENAI_MODEL_NAME: str = "gpt-4-turbo-preview"
    LLM_BASE_URL: str = "https://api.openai.com/v1"
    
    # Vector Store & Data
    VECTOR_STORE_PATH: str = "./data/vectorstore"
    RAW_DATA_PATH: str = "./data/raw"
    PROCESSED_DATA_PATH: str = "./data/processed"
    
    # CORS Configuration
    # For production, we would restrict these to specific domains
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # Logging
    LOG_LEVEL: str = "INFO"

    # Load from .env file if it exists
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )


# Instantiate the settings object to be imported across the app
settings = Settings()
