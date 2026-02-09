from __future__ import annotations

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.constants import (
    DEFAULT_LLM_MODEL,
    DEFAULT_LLM_TEMPERATURE,
    DEFAULT_MAX_ITERATIONS,
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    groq_api_key: str = Field(alias="GROQ_API_KEY")
    tavily_api_key: str = Field(alias="TAVILY_API_KEY")

    llm_model: str = DEFAULT_LLM_MODEL
    llm_temperature: float = DEFAULT_LLM_TEMPERATURE

    max_iterations: int = DEFAULT_MAX_ITERATIONS


settings = Settings()
