from functools import lru_cache

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: SecretStr
    groq_model: str = "llama-3.3-70b-versatile"
    max_concurrency: int = 3

    # --- Phase 1.5: ingestion ---
    min_coverage: float = Field(default=0.95, ge=0, le=1)   # below this -> human review
    max_clause_chars: int = Field(default=6000, gt=0)       # review-unit size cap
    llm_segmentation_fallback: bool = True                  # switch off for offline/tests


@lru_cache
def get_settings() -> Settings:
    return Settings()