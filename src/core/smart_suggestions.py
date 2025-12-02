"""Smart suggestions engine for context-aware recommendations."""

from datetime import date, datetime, time, timedelta
from typing import Optional
from dataclasses import dataclass

from src.models import Activity, Completion, SessionLocal
from src.services import WeatherService


@dataclass
class Suggestion:
    """A single suggestion."""
    message: str
    priority: str  # high, medium, low
    category: str  # weather, time, pattern, reminder
    activity_id: Optional[int] = None
    
    @property
    def icon(self) -> str:
        icons = {
            "weather": "🌤️",
            "time": "⏰",
            "pattern": "📊",
            "reminder": "🔔",
            "health": "💪",
            "general": "💡",
        }
        return icons.get(self.category, "💡")
    
    def display(self) -> str:
        priority_colors = {
            "high": "red",
            "medium": "yellow", 
            "low": "dim",
        }
        return f"{self.icon} {self.message}"


class SmartSuggestions:
    """Generate context-aware suggestions."""
    
    # Rush hour times
    MORNING_RUSH = (time(7, 0), time(9, 30))
    EVENING_RUSH = (time(16, 30), time(19, 0))
    
    def __init__(self):
        self.db = SessionLocal()
        self.weather_service = WeatherService()
    
    def get_all_suggestions(self, target_date: Optional[date] = None) -> list[Suggestion]:
        """Get all relevant suggestions for a date."""
        if target_date is None:
            target_date = date.today()
        
        suggestions = []
        
        # Weather-based suggestions
        suggestions.extend(self._get_weather_suggestions(target_date))
        
        # Time-based suggestions
        suggestions.extend(self._get_time_suggestions(target_date))
        
        # Pattern-based suggestions
        suggestions.extend(self._get_pattern_suggestions(target_date))
        
        # Activity-specific suggestions
        suggestions.extend(self._get_activity_suggestions(target_date))
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 2))
        
        return suggestions
    
    def _get_weather_suggestions(self, target_date: date) -> list[Suggestion]:
        """Generate weather-based suggestions."""
        suggestions = []
        
        # Only for today (weather forecast)
        if target_date != date.today():
            return suggestions
        
        weather = self.weather_service.get_current()
        if not weather:
            return suggestions
        
        # Get today's outdoor activities
        outdoor_activities = self._get_outdoor_activities(target_date)
        
        # Temperature suggestions
        temp = weather.temperature
        units = weather.units
        
        if units == "metric":
            if temp > 35:
                suggestions.append(Suggestion(
                    message=f"Extreme heat ({temp}°C)! Stay hydrated and avoid midday sun.",
                    priority="high",
                    category="weather",
                ))
            elif temp > 30:
                suggestions.append(Suggestion(
                    message=f"Hot day ({temp}°C) - drink plenty of water.",
                    priority="medium",
                    category="weather",
                ))
            elif temp < 0:
                suggestions.append(Suggestion(
                    message=f"Freezing ({temp}°C)! Watch for ice, dress warmly.",
                    priority="high",
                    category="weather",
                ))
            elif temp < 10:
                suggestions.append(Suggestion(
                    message=f"Cold day ({temp}°C) - dress in layers.",
                    priority="low",
                    category="weather",
                ))
        else:
            if temp > 95:
                suggestions.append(Suggestion(
                    message=f"Extreme heat ({temp}°F)! Stay hydrated and avoid midday sun.",
                    priority="high",
                    category="weather",
                ))
            elif temp > 86:
                suggestions.append(Suggestion(
                    message=f"Hot day ({temp}°F) - drink plenty of water.",
                    priority="medium",
                    category="weather",
                ))
            elif temp < 32:
                suggestions.append(Suggestion(
                    message=f"Freezing ({temp}°F)! Watch for ice, dress warmly.",
                    priority="high",
                    category="weather",
                ))
            elif temp < 50:
                suggestions.append(Suggestion(
                    message=f"Cold day ({temp}°F) - dress in layers.",
                    priority="low",
                    category="weather",
                ))
        
        # Condition-based suggestions
        desc = weather.description.lower()
        
        if "rain" in desc or "drizzle" in desc:
            suggestions.append(Suggestion(
                message="Rain expected - bring an umbrella! ☔",
                priority="high",
                category="weather",
            ))
            if outdoor_activities:
                for activity in outdoor_activities:
                    suggestions.append(Suggestion(
                        message=f"Consider moving '{activity.title}' indoors due to rain.",
                        priority="medium",
                        category="weather",
                        activity_id=activity.id,
                    ))
        
        if "snow" in desc:
            suggestions.append(Suggestion(
                message="Snow expected - allow extra travel time. ❄️",
                priority="high",
                category="weather",
            ))
        
        if "storm" in desc or "thunder" in desc:
            suggestions.append(Suggestion(
                message="Storms expected - stay safe, avoid outdoor activities. ⛈️",
                priority="high",
                category="weather",
            ))
        
        # Wind
        if weather.wind_speed > (15 if units == "metric" else 33):
            suggestions.append(Suggestion(
                message="Strong winds today - secure loose items.",
                priority="medium",
                category="weather",
            ))
        
        return suggestions
    
    def _get_time_suggestions(self, target_date: date) -> list[Suggestion]:
        """Generate time-based suggestions."""
        suggestions = []
        
        if target_date != date.today():
            return suggestions
        
        now = datetime.now()
        current_time = now.time()
        
        # Get today's activities
        activities = self._get_activities_for_date(target_date)
        
        for activity in activities:
            # Check for rush hour conflicts
            if activity.location and self._is_rush_hour(activity.start_time):
                suggestions.append(Suggestion(
                    message=f"'{activity.title}' is during rush hour - leave early!",
                    priority="medium",
                    category="time",
                    activity_id=activity.id,
                ))
            
            # Check for upcoming activities
            if activity.start_time > current_time:
                # Calculate minutes until activity
                activity_dt = datetime.combine(target_date, activity.start_time)
                minutes_until = (activity_dt - now).total_seconds() / 60
                
                if minutes_until <= activity.prep_time and minutes_until > 0:
                    suggestions.append(Suggestion(
                        message=f"'{activity.title}' starts in {int(minutes_until)} minutes!",
                        priority="high",
                        category="reminder",
                        activity_id=activity.id,
                    ))
        
        # Evening reminder about tomorrow
        if current_time >= time(20, 0):
            tomorrow = target_date + timedelta(days=1)
            tomorrow_activities = self._get_activities_for_date(tomorrow)
            
            early_activities = [a for a in tomorrow_activities if a.start_time < time(8, 0)]
            if early_activities:
                earliest = min(early_activities, key=lambda a: a.start_time)
                suggestions.append(Suggestion(
                    message=f"Early start tomorrow: '{earliest.title}' at {earliest.start_time.strftime('%H:%M')}",
                    priority="medium",
                    category="time",
                ))
        
        return suggestions
    
    def _get_pattern_suggestions(self, target_date: date) -> list[Suggestion]:
        """Generate suggestions based on activity patterns."""
        suggestions = []
        
        activities = self._get_activities_for_date(target_date)
        
        for activity in activities:
            # Get completion history
            completions = (
                self.db.query(Completion)
                .filter(Completion.activity_id == activity.id)
                .order_by(Completion.date.desc())
                .limit(10)
                .all()
            )
            
            if len(completions) < 3:
                continue
            
            # Calculate completion rate
            done_count = sum(1 for c in completions if c.status == "done")
            rate = done_count / len(completions) * 100
            
            if rate < 40:
                suggestions.append(Suggestion(
                    message=f"'{activity.title}' often missed ({int(rate)}%). Set extra reminders?",
                    priority="medium",
                    category="pattern",
                    activity_id=activity.id,
                ))
            
            # Check for day-specific patterns
            day_name = target_date.strftime("%A")
            day_completions = [c for c in completions if c.date.strftime("%A") == day_name]
            
            if len(day_completions) >= 2:
                day_missed = sum(1 for c in day_completions if c.status == "missed")
                if day_missed / len(day_completions) > 0.5:
                    suggestions.append(Suggestion(
                        message=f"'{activity.title}' is often missed on {day_name}s.",
                        priority="low",
                        category="pattern",
                        activity_id=activity.id,
                    ))
        
        return suggestions
    
    def _get_activity_suggestions(self, target_date: date) -> list[Suggestion]:
        """Generate activity-specific suggestions."""
        suggestions = []
        
        activities = self._get_activities_for_date(target_date)
        
        # Check for Health activities
        health_activities = [a for a in activities if a.category == "Health"]
        
        for activity in health_activities:
            if activity.is_outdoor:
                weather = self.weather_service.get_current()
                if weather:
                    if weather.humidity > 80:
                        suggestions.append(Suggestion(
                            message=f"High humidity ({weather.humidity}%) for '{activity.title}' - take it easy.",
                            priority="medium",
                            category="health",
                            activity_id=activity.id,
                        ))
        
        # Check for back-to-back activities
        for i, activity in enumerate(activities[:-1]):
            next_activity = activities[i + 1]
            
            if activity.duration:
                # Calculate end time
                end_minutes = activity.start_time.hour * 60 + activity.start_time.minute + activity.duration
                end_time = time(end_minutes // 60, end_minutes % 60)
                
                # Check gap to next activity
                next_start_minutes = next_activity.start_time.hour * 60 + next_activity.start_time.minute
                gap = next_start_minutes - (end_minutes)
                
                if gap < 15 and gap >= 0:
                    suggestions.append(Suggestion(
                        message=f"Tight schedule: only {gap} min between '{activity.title}' and '{next_activity.title}'",
                        priority="low",
                        category="time",
                    ))
        
        return suggestions
    
    def _get_outdoor_activities(self, target_date: date) -> list[Activity]:
        """Get outdoor activities for a date."""
        activities = self._get_activities_for_date(target_date)
        return [a for a in activities if a.is_outdoor]
    
    def _get_activities_for_date(self, target_date: date) -> list[Activity]:
        """Get all activities scheduled for a date."""
        from src.core.activity_manager import ActivityManager
        manager = ActivityManager(self.db)
        return manager.get_for_date(target_date)
    
    def _is_rush_hour(self, check_time: time) -> bool:
        """Check if time falls within rush hour."""
        morning = self.MORNING_RUSH[0] <= check_time <= self.MORNING_RUSH[1]
        evening = self.EVENING_RUSH[0] <= check_time <= self.EVENING_RUSH[1]
        return morning or evening
    
    def display_suggestions(self, target_date: Optional[date] = None) -> None:
        """Display all suggestions."""
        from rich.console import Console
        from rich.panel import Panel
        from rich import box
        
        console = Console()
        suggestions = self.get_all_suggestions(target_date)
        
        if not suggestions:
            console.print("\n[green]✨ No suggestions - you're all set![/green]\n")
            return
        
        console.print()
        console.print(Panel(
            "[bold]Context-aware tips for your day[/bold]",
            title="💡 [cyan]Smart Suggestions[/cyan]",
            box=box.ROUNDED,
        ))
        
        # Group by priority
        high = [s for s in suggestions if s.priority == "high"]
        medium = [s for s in suggestions if s.priority == "medium"]
        low = [s for s in suggestions if s.priority == "low"]
        
        if high:
            console.print("\n[bold red]⚠️ Important:[/bold red]")
            for s in high:
                console.print(f"  {s.display()}")
        
        if medium:
            console.print("\n[bold yellow]📌 Recommended:[/bold yellow]")
            for s in medium:
                console.print(f"  {s.display()}")
        
        if low:
            console.print("\n[dim]💭 Tips:[/dim]")
            for s in low:
                console.print(f"  [dim]{s.display()}[/dim]")
        
        console.print()
    
    def close(self):
        """Close database session."""
        self.db.close()