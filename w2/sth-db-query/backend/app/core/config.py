"""
Application configuration settings.
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = f"sqlite+aiosqlite:///{os.path.join(os.path.dirname(__file__), '../../.db_query/db_query.db')}"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # OpenAI API Configuration
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    openai_model: str = "gpt-3.5-turbo"

    # Development Settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # CORS Settings - Allow all origins for development
    CORS_ORIGINS: List[str] = ["*"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            # Handle string format like '["http://localhost:3000", "http://localhost:5173"]'
            if v.startswith("[") and v.endswith("]"):
                import ast
                try:
                    return ast.literal_eval(v)
                except (ValueError, SyntaxError):
                    return [origin.strip().strip('"').strip("'") for origin in v[1:-1].split(",")]
            return [v]
        return v

    # Query Settings
    max_query_results: int = 1000
    query_timeout_seconds: int = 30

    model_config = {
        "case_sensitive": False,
    }


# Global settings instance
settings = Settings()
