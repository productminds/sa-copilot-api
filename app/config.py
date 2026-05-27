import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    log_level: str
    ai_provider: str
    anthropic_api_key: str | None
    google_cloud_project: str | None
    google_cloud_location: str
    bigquery_dataset: str | None
    claude_model_id: str


@lru_cache
def get_settings() -> Settings:
    return Settings(
        log_level=os.getenv("LOG_LEVEL", "INFO"),
        ai_provider=os.getenv("AI_PROVIDER", "mock").lower(),
        anthropic_api_key=os.getenv("ANTHROPIC_API_KEY") or os.getenv("CLAUDE_DEV_API_KEY"),
        google_cloud_project=os.getenv("GOOGLE_CLOUD_PROJECT"),
        google_cloud_location=os.getenv("GOOGLE_CLOUD_LOCATION", "US"),
        bigquery_dataset=os.getenv("BIGQUERY_DATASET"),
        claude_model_id=os.getenv("CLAUDE_MODEL_ID", "claude-3-5-haiku-20241022"),
    )
