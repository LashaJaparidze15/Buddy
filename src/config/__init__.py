"""Configuration module for Buddy."""

from src.config.settings import get_settings, Settings
from src.config.defaults import CATEGORIES, RECURRENCE_OPTIONS, COMPLETION_STATUSES

__all__ = [
    "get_settings",
    "Settings", 
    "CATEGORIES",
    "RECURRENCE_OPTIONS",
    "COMPLETION_STATUSES",
]