# ============================================
# app/core/config.py - App Configuration
# ============================================
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List


class Settings(BaseSettings):
    # App Info
    APP_NAME: str = "Indian Journal Citation Parser"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # OpenAI (optional)
    OPENAI_API_KEY: str = ""

    # CrossRef (free, no key needed)
    CROSSREF_EMAIL: str = "citationparser@example.com"
    CROSSREF_BASE_URL: str = "https://api.crossref.org/works"
    DOI_ORG_URL: str = "https://doi.org"

    # File Upload
    MAX_FILE_SIZE_MB: int = 10

    # CORS
    CORS_ORIGINS: List[str] = ["*"]

    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"
    }


settings = Settings()
