"""Dashboard API endpoint."""

from datetime import date, datetime
from typing import Optional
from fastapi import APIRouter

from src.core import ActivityManager, CompletionManager, SmartSuggestions
from src.services import WeatherService, HolidaysService

router = APIRouter()


@router.get("")
def get_dashboard(location: Optional[str] = None):
    """Get all dashboard data in one call."""
    activity_manager = ActivityManager()
    completion_manager = CompletionManager()
    weather_service = WeatherService()
    holidays_service = HolidaysService()
    suggestions_engine = SmartSuggestions()
    
    try:
        today = date.today()
        now = datetime.now()
        
        # Today's activities
        activities = activity_manager.get_for_today()
        activities_data = [
            {
                "id": a.id,
                "title": a.title,
                "start_time": a.start_time.strftime("%H:%M"),
                "category": a.category,
                "duration_formatted": a.duration_formatted,
                "status": completion_manager.get_completion_status(a.id, today),
            }
            for a in activities
        ]
        
        # Count completed
        completed = sum(1 for a in activities_data if a["status"] == "done")
        
        # Weather - use passed location or default
        weather = weather_service.get_current(location)
        weather_data = None
        if weather:
            weather_data = {
                "location": weather.location,
                "temperature": weather.temperature,
                "feels_like": weather.feels_like,
                "temp_unit": weather.temp_unit,
                "description": weather.description,
                "humidity": weather.humidity,
                "wind_speed": weather.wind_speed,
                "wind_unit": weather.wind_unit,
            }
        
        # Upcoming holidays
        holidays = holidays_service.get_upcoming(days_ahead=7)
        holidays_data = [
            {
                "name": h.name,
                "date": str(h.date),
                "days_until": h.days_until,
            }
            for h in holidays
        ]
        
        # Smart suggestions
        suggestions = suggestions_engine.get_all_suggestions()
        suggestions_data = [
            {
                "message": s.message,
                "priority": s.priority,
                "category": s.category,
                "icon": s.icon,
            }
            for s in suggestions[:5]
        ]
        
        # Greeting
        hour = now.hour
        if hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        return {
            "greeting": greeting,
            "date": today.strftime("%A, %B %d, %Y"),
            "weather": weather_data,
            "activities": {
                "items": activities_data,
                "total": len(activities),
                "completed": completed,
            },
            "holidays": holidays_data,
            "suggestions": suggestions_data,
        }
    finally:
        activity_manager.close()
        completion_manager.close()
        suggestions_engine.close()