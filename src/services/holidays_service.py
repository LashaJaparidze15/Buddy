"""Holidays service with built-in holidays and optional API support."""

from datetime import date, timedelta
from typing import Optional
from dataclasses import dataclass

import requests

from src.config import get_settings


@dataclass
class Holiday:
    """Single holiday entry."""
    name: str
    date: date
    country: str = "US"
    type: str = "public"
    
    @property
    def days_until(self) -> int:
        """Days until this holiday."""
        return (self.date - date.today()).days
    
    def summary(self) -> str:
        """One-line summary."""
        if self.days_until == 0:
            when = "Today!"
        elif self.days_until == 1:
            when = "Tomorrow"
        else:
            when = f"in {self.days_until} days"
        
        return f"🎉 {self.name} - {self.date.strftime('%b %d')} ({when})"


class HolidaysService:
    """Provide holiday information."""
    
    # Built-in US holidays (month, day, name)
    US_HOLIDAYS_2024 = [
        (1, 1, "New Year's Day"),
        (1, 15, "Martin Luther King Jr. Day"),
        (2, 14, "Valentine's Day"),
        (2, 19, "Presidents' Day"),
        (3, 17, "St. Patrick's Day"),
        (4, 21, "Easter Sunday"),
        (5, 12, "Mother's Day"),
        (5, 27, "Memorial Day"),
        (6, 16, "Father's Day"),
        (7, 4, "Independence Day"),
        (9, 2, "Labor Day"),
        (10, 14, "Columbus Day"),
        (10, 31, "Halloween"),
        (11, 11, "Veterans Day"),
        (11, 28, "Thanksgiving"),
        (12, 25, "Christmas Day"),
        (12, 31, "New Year's Eve"),
    ]
    
    US_HOLIDAYS_2025 = [
        (1, 1, "New Year's Day"),
        (1, 20, "Martin Luther King Jr. Day"),
        (2, 14, "Valentine's Day"),
        (2, 17, "Presidents' Day"),
        (3, 17, "St. Patrick's Day"),
        (4, 20, "Easter Sunday"),
        (5, 11, "Mother's Day"),
        (5, 26, "Memorial Day"),
        (6, 15, "Father's Day"),
        (7, 4, "Independence Day"),
        (9, 1, "Labor Day"),
        (10, 13, "Columbus Day"),
        (10, 31, "Halloween"),
        (11, 11, "Veterans Day"),
        (11, 27, "Thanksgiving"),
        (12, 25, "Christmas Day"),
        (12, 31, "New Year's Eve"),
    ]
    
    def __init__(self):
        settings = get_settings()
        self.location = settings.location
    
    def _get_builtin_holidays(self, year: int) -> list[Holiday]:
        """Get built-in holidays for a year."""
        if year == 2024:
            holidays_data = self.US_HOLIDAYS_2024
        elif year == 2025:
            holidays_data = self.US_HOLIDAYS_2025
        else:
            # Use 2025 as fallback, adjust year
            holidays_data = self.US_HOLIDAYS_2025
        
        holidays = []
        for month, day, name in holidays_data:
            try:
                holidays.append(Holiday(
                    name=name,
                    date=date(year, month, day),
                    country="US",
                    type="public",
                ))
            except ValueError:
                # Invalid date, skip
                continue
        
        return holidays
    
    def get_upcoming(self, days_ahead: int = 7) -> list[Holiday]:
        """Get holidays within the next N days."""
        today = date.today()
        end_date = today + timedelta(days=days_ahead)
        
        # Get holidays for current year and next year (for year-end)
        all_holidays = []
        all_holidays.extend(self._get_builtin_holidays(today.year))
        all_holidays.extend(self._get_builtin_holidays(today.year + 1))
        
        # Filter to upcoming
        upcoming = [
            h for h in all_holidays
            if today <= h.date <= end_date
        ]
        
        return sorted(upcoming, key=lambda h: h.date)
    
    def get_next_holiday(self) -> Optional[Holiday]:
        """Get the next upcoming holiday."""
        today = date.today()
        
        all_holidays = []
        all_holidays.extend(self._get_builtin_holidays(today.year))
        all_holidays.extend(self._get_builtin_holidays(today.year + 1))
        
        future = [h for h in all_holidays if h.date >= today]
        
        if future:
            return min(future, key=lambda h: h.date)
        return None
    
    def is_holiday(self, check_date: date = None) -> Optional[Holiday]:
        """Check if a date is a holiday."""
        if check_date is None:
            check_date = date.today()
        
        holidays = self._get_builtin_holidays(check_date.year)
        
        for holiday in holidays:
            if holiday.date == check_date:
                return holiday
        
        return None
    
    def get_holidays_in_month(self, year: int, month: int) -> list[Holiday]:
        """Get all holidays in a specific month."""
        holidays = self._get_builtin_holidays(year)
        return [h for h in holidays if h.date.month == month]
    
    def format_upcoming(self, holidays: list[Holiday]) -> str:
        """Format holidays for display."""
        if not holidays:
            return "No upcoming holidays in the next week."
        
        lines = []
        for holiday in holidays:
            lines.append(holiday.summary())
        
        return "\n".join(lines)