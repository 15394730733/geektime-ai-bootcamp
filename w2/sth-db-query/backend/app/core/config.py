"""
Application configuration settings.
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = "sqlite+aiosqlite:///./.db_query/db_query.db"

    # Server Configuration
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # OpenAI API Configuration - Read from environment variables
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_base_url: str = Field(default="https://api.openai.com/v1", env="OPENAI_BASE_URL")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")

    # Development Settings
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"

    # CORS Settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

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



# Global settings instance
settings = Settings()
