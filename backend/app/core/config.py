from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the Agentic RAG application."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Application settings
    app_name: str = "Agentic RAG Platform"
    app_env: Literal["development", "testing", "production"] = "development"
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    api_prefix: str = "/api/v1"

    # Azure OpenAI
    azure_openai_endpoint: str | None = None
    azure_openai_api_key: str | None = None
    azure_openai_deployment: str | None = None
    azure_openai_api_version: str | None = None

    azure_ai_search_endpoint: str | None = None
    azure_ai_search_index: str | None = None
    azure_ai_search_api_key: str | None = None

    # LLM generation settings
    llm_temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    llm_max_tokens: int = Field(default=4000, ge=1, le=8192)

    applicationinsights_connection_string: str | None = None

    # Azure AI Search - Phase 3
    azure_ai_search_endpoint: str | None = None
    azure_ai_search_index: str | None = None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return one cached settings instance."""
    return Settings()


settings = get_settings()
