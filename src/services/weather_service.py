"""Weather service using OpenWeatherMap API."""

from typing import Optional
from dataclasses import dataclass

import requests

from src.config import get_settings


@dataclass
class WeatherData:
    """Weather information container."""
    location: str
    temperature: float
    feels_like: float
    humidity: int
    description: str
    icon: str
    wind_speed: float
    units: str
    
    @property
    def temp_unit(self) -> str:
        return "°C" if self.units == "metric" else "°F"
    
    @property
    def wind_unit(self) -> str:
        return "m/s" if self.units == "metric" else "mph"
    
    def summary(self) -> str:
        """Return a one-line summary."""
        return f"{self.temperature}{self.temp_unit}, {self.description}"
    
    def detailed(self) -> str:
        """Return detailed weather info."""
        return (
            f"📍 {self.location}\n"
            f"🌡️  {self.temperature}{self.temp_unit} (feels like {self.feels_like}{self.temp_unit})\n"
            f"☁️  {self.description.capitalize()}\n"
            f"💧 Humidity: {self.humidity}%\n"
            f"💨 Wind: {self.wind_speed} {self.wind_unit}"
        )


@dataclass
class ForecastItem:
    """Single forecast entry."""
    datetime: str
    temperature: float
    description: str
    icon: str
    units: str
    
    @property
    def temp_unit(self) -> str:
        return "°C" if self.units == "metric" else "°F"


class WeatherService:
    """Fetch weather data from OpenWeatherMap."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    
    def __init__(self):
        settings = get_settings()
        self.api_key = settings.weather_api_key
        self.location = settings.location
        self.units = settings.weather_units
    
    def _make_request(self, endpoint: str, params: dict) -> Optional[dict]:
        """Make API request with error handling."""
        if not self.api_key:
            return None
        
        params["appid"] = self.api_key
        params["units"] = self.units
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
    
    def get_current(self, location: Optional[str] = None) -> Optional[WeatherData]:
        """Get current weather for location."""
        loc = location or self.location
        data = self._make_request("weather", {"q": loc})
        
        if not data:
            return None
        
        return WeatherData(
            location=data.get("name", loc),
            temperature=round(data["main"]["temp"], 1),
            feels_like=round(data["main"]["feels_like"], 1),
            humidity=data["main"]["humidity"],
            description=data["weather"][0]["description"],
            icon=data["weather"][0]["icon"],
            wind_speed=round(data["wind"]["speed"], 1),
            units=self.units,
        )
    
    def get_forecast(self, location: Optional[str] = None, hours: int = 24) -> list[ForecastItem]:
        """Get forecast for next N hours (3-hour intervals)."""
        loc = location or self.location
        data = self._make_request("forecast", {"q": loc})
        
        if not data:
            return []
        
        # Calculate how many 3-hour intervals we need
        intervals = hours // 3
        forecasts = []
        
        for item in data.get("list", [])[:intervals]:
            forecasts.append(ForecastItem(
                datetime=item["dt_txt"],
                temperature=round(item["main"]["temp"], 1),
                description=item["weather"][0]["description"],
                icon=item["weather"][0]["icon"],
                units=self.units,
            ))
        
        return forecasts
    
    def get_weather_suggestion(self, is_outdoor: bool = False) -> Optional[str]:
        """Get context-aware suggestion based on weather."""
        weather = self.get_current()
        
        if not weather:
            return None
        
        suggestions = []
        
        # Temperature checks
        if self.units == "metric":
            if weather.temperature > 35:
                suggestions.append("🔥 Very hot - stay hydrated and avoid peak sun hours")
            elif weather.temperature > 30:
                suggestions.append("☀️ Hot day - drink plenty of water")
            elif weather.temperature < 5:
                suggestions.append("🥶 Cold weather - dress warmly")
            elif weather.temperature < 0:
                suggestions.append("❄️ Freezing - watch for ice")
        else:
            if weather.temperature > 95:
                suggestions.append("🔥 Very hot - stay hydrated and avoid peak sun hours")
            elif weather.temperature > 86:
                suggestions.append("☀️ Hot day - drink plenty of water")
            elif weather.temperature < 41:
                suggestions.append("🥶 Cold weather - dress warmly")
            elif weather.temperature < 32:
                suggestions.append("❄️ Freezing - watch for ice")
        
        # Condition checks
        desc = weather.description.lower()
        if "rain" in desc:
            suggestions.append("🌧️ Rain expected - bring an umbrella")
        elif "snow" in desc:
            suggestions.append("🌨️ Snow expected - allow extra travel time")
        elif "storm" in desc or "thunder" in desc:
            suggestions.append("⛈️ Storms expected - consider rescheduling outdoor activities")
        
        # Wind check
        if weather.wind_speed > 10 if self.units == "metric" else weather.wind_speed > 22:
            suggestions.append("💨 Strong winds expected")
        
        # Outdoor activity specific
        if is_outdoor and not suggestions:
            if "clear" in desc or "sun" in desc:
                suggestions.append("😎 Great weather for outdoor activities!")
        
        return suggestions[0] if suggestions else None