"""Settings management for Buddy."""

import json
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings
from pydantic import Field

from src.config.defaults import (
    DATA_DIR,
    DATABASE_PATH,
    DEFAULT_REPORT_TIME,
    DEFAULT_REVIEW_TIME,
    DEFAULT_WEATHER_UNITS,
    DEFAULT_LOCATION,
    DEFAULT_PREP_TIME,
    DEFAULT_WEEK_START,
)


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # API Keys (loaded from .env file)
    weather_api_key: Optional[str] = Field(default=None, alias="WEATHER_API_KEY")
    news_api_key: Optional[str] = Field(default=None, alias="NEWS_API_KEY")
    stocks_api_key: Optional[str] = Field(default=None, alias="STOCKS_API_KEY")
    
    # User preferences
    location: str = DEFAULT_LOCATION
    weather_units: str = DEFAULT_WEATHER_UNITS
    report_time: str = DEFAULT_REPORT_TIME
    review_time: str = DEFAULT_REVIEW_TIME
    prep_time: int = DEFAULT_PREP_TIME
    week_start: str = DEFAULT_WEEK_START
    
    # Paths
    database_path: Path = DATABASE_PATH
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


# Global settings instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def save_user_preferences(preferences: dict) -> None:
    """Save user preferences to JSON file."""
    config_path = DATA_DIR / "config.json"
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load existing config
    existing = {}
    if config_path.exists():
        with open(config_path, "r") as f:
            existing = json.load(f)
    
    # Update with new preferences
    existing.update(preferences)
    
    with open(config_path, "w") as f:
        json.dump(existing, f, indent=2)


def load_user_preferences() -> dict:
    """Load user preferences from JSON file."""
    config_path = DATA_DIR / "config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {}