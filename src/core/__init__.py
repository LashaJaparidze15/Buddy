"""Core business logic for Buddy."""

from src.core.activity_manager import ActivityManager
from src.core.report_generator import ReportGenerator
from src.core.completion_manager import CompletionManager
from src.core.analytics_engine import AnalyticsEngine
from src.core.smart_suggestions import SmartSuggestions, Suggestion

__all__ = [
    "ActivityManager",
    "ReportGenerator",
    "CompletionManager",
    "AnalyticsEngine",
    "SmartSuggestions",
    "Suggestion",
]