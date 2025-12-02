"""Weather API endpoint."""

from typing import Optional
from fastapi import APIRouter

from src.services import WeatherService

router = APIRouter()


@router.get("")
def get_weather(location: Optional[str] = None):
    """Get current weather."""
    service = WeatherService()
    weather = service.get_current(location)
    
    if not weather:
        return {"error": "Weather data unavailable"}
    
    return {
        "location": weather.location,
        "temperature": weather.temperature,
        "feels_like": weather.feels_like,
        "temp_unit": weather.temp_unit,
        "description": weather.description,
        "humidity": weather.humidity,
        "wind_speed": weather.wind_speed,
        "wind_unit": weather.wind_unit,
    }


@router.get("/forecast")
def get_forecast(location: Optional[str] = None, hours: int = 24):
    """Get weather forecast."""
    service = WeatherService()
    forecasts = service.get_forecast(location, hours)
    
    return [
        {
            "datetime": f.datetime,
            "temperature": f.temperature,
            "temp_unit": f.temp_unit,
            "description": f.description,
        }
        for f in forecasts
    ]


@router.get("/suggestion")
def get_weather_suggestion(is_outdoor: bool = False):
    """Get weather-based suggestion."""
    service = WeatherService()
    suggestion = service.get_weather_suggestion(is_outdoor)
    
    return {"suggestion": suggestion}