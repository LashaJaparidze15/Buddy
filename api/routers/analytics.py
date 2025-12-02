"""Analytics API endpoint."""

from typing import Optional
from fastapi import APIRouter

from src.core import AnalyticsEngine
from src.utils import parse_date

router = APIRouter()


@router.get("")
def get_analytics(date_str: Optional[str] = None):
    """Get weekly analytics."""
    engine = AnalyticsEngine()
    
    try:
        target_date = parse_date(date_str) if date_str else None
        stats = engine.calculate_stats(target_date)
        insights = engine.get_insights(stats)
        streaks = engine.get_streaks()
        
        return {
            "week_start": str(stats["week_start"]),
            "week_end": str(stats["week_end"]),
            "total": stats["total"],
            "done": stats["done"],
            "missed": stats["missed"],
            "partial": stats["partial"],
            "rescheduled": stats["rescheduled"],
            "completion_rate": stats["completion_rate"],
            "by_category": stats["by_category"],
            "by_day": stats["by_day"],
            "best_day": stats["best_day"],
            "worst_day": stats["worst_day"],
            "insights": insights,
            "streaks": streaks[:5],  # Top 5 streaks
        }
    finally:
        engine.close()


@router.get("/compare")
def compare_weeks(date_str: Optional[str] = None):
    """Compare current week with previous week."""
    engine = AnalyticsEngine()
    
    try:
        target_date = parse_date(date_str) if date_str else None
        comparison = engine.compare_weeks(target_date)
        
        return {
            "current_rate": comparison["current"]["completion_rate"],
            "previous_rate": comparison["previous"]["completion_rate"],
            "change": comparison["rate_change"],
            "improved": comparison["improved"],
        }
    finally:
        engine.close()