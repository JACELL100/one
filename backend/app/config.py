"""Application settings loaded from environment variables.

All values have safe defaults so the app boots even without a full ``.env``.
Hosted-inference credentials are optional: when absent, the pipeline
gracefully falls back to classical CV / rules-only paths.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "one8 FitLab API"
    environment: str = "development"

    # CORS — comma-separated list of allowed origins.
    cors_origins: str = "http://localhost:3000"

    # Supabase (optional for local/demo runs).
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_jwt_secret: str = ""

    # Hosted inference (optional).
    hf_api_token: str = ""
    hf_segmentation_model: str = "briaai/RMBG-1.4"
    nvidia_api_key: str = ""
    llm_api_base: str = ""
    llm_api_key: str = ""
    llm_model: str = ""

    # Upload limits.
    max_upload_mb: int = 12

    @property
    def cors_origin_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
