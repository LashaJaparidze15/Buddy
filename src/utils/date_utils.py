"""Date and time utility functions."""

from datetime import datetime, date, time, timedelta
from typing import Optional

from dateutil import parser


def parse_time(time_str: str) -> time:
    """Parse time string to time object.
    
    Accepts: "06:30", "6:30", "6:30am", "18:30", "6:30pm"
    """
    try:
        parsed = parser.parse(time_str)
        return parsed.time()
    except Exception:
        raise ValueError(f"Invalid time format: {time_str}. Use HH:MM (e.g., 06:30 or 6:30pm)")


def parse_date(date_str: str) -> date:
    """Parse date string to date object.
    
    Accepts: "2024-01-15", "Jan 15", "15/01/2024", "tomorrow", "today"
    """
    date_str = date_str.lower().strip()
    
    if date_str == "today":
        return date.today()
    elif date_str == "tomorrow":
        return date.today() + timedelta(days=1)
    elif date_str == "yesterday":
        return date.today() - timedelta(days=1)
    
    try:
        parsed = parser.parse(date_str)
        return parsed.date()
    except Exception:
        raise ValueError(f"Invalid date format: {date_str}")


def get_week_bounds(target_date: Optional[date] = None, week_start: str = "monday") -> tuple[date, date]:
    """Get start and end dates of the week containing target_date."""
    if target_date is None:
        target_date = date.today()
    
    # Monday = 0, Sunday = 6
    start_day = 0 if week_start.lower() == "monday" else 6
    
    days_since_start = (target_date.weekday() - start_day) % 7
    week_start_date = target_date - timedelta(days=days_since_start)
    week_end_date = week_start_date + timedelta(days=6)
    
    return week_start_date, week_end_date


def format_time(t: time) -> str:
    """Format time object to readable string."""
    return t.strftime("%H:%M")


def format_date(d: date) -> str:
    """Format date object to readable string."""
    return d.strftime("%a, %b %d")  # e.g., "Mon, Jan 15"


def format_datetime(dt: datetime) -> str:
    """Format datetime object to readable string."""
    return dt.strftime("%a, %b %d at %H:%M")


def is_weekday(d: date) -> bool:
    """Check if date is a weekday (Mon-Fri)."""
    return d.weekday() < 5


def is_weekend(d: date) -> bool:
    """Check if date is a weekend (Sat-Sun)."""
    return d.weekday() >= 5


def get_day_name(d: date) -> str:
    """Get lowercase day name."""
    return d.strftime("%A").lower()