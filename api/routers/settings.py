"""Settings API endpoint."""

from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel

from src.config.settings import save_user_preferences, load_user_preferences, get_settings

router = APIRouter()


class SettingsUpdate(BaseModel):
    location: Optional[str] = None
    units: Optional[str] = None
    report_time: Optional[str] = None
    review_time: Optional[str] = None


@router.get("")
def get_current_settings():
    """Get current settings."""
    settings = get_settings()
    user_prefs = load_user_preferences()
    
    return {
        "location": user_prefs.get("location", settings.location),
        "units": user_prefs.get("weather_units", settings.weather_units),
        "report_time": user_prefs.get("report_time", settings.report_time),
        "review_time": user_prefs.get("review_time", settings.review_time),
    }


@router.put("")
def update_settings(data: SettingsUpdate):
    """Update settings."""
    updates = {}
    
    if data.location:
        updates["location"] = data.location
    if data.units:
        updates["weather_units"] = data.units
    if data.report_time:
        updates["report_time"] = data.report_time
    if data.review_time:
        updates["review_time"] = data.review_time
    
    if updates:
        save_user_preferences(updates)
    
    return {"message": "Settings updated", "updates": updates}