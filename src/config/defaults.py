"""Default configuration values for Buddy."""

from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
LOGS_DIR = BASE_DIR / "logs"

# Database
DATABASE_NAME = "buddy.db"
DATABASE_PATH = DATA_DIR / DATABASE_NAME

# Schedule times (24-hour format)
DEFAULT_REPORT_TIME = "06:00"
DEFAULT_REVIEW_TIME = "21:00"

# Activity categories
CATEGORIES = [
    "Work",
    "Personal", 
    "Health",
    "Education",
    "Errands",
    "Social",
    "Finance",
    "Other",
]

# Recurrence options
RECURRENCE_OPTIONS = [
    "once",
    "daily",
    "weekdays",
    "weekends",
    "weekly",
    "custom",
]

# Activity completion statuses
COMPLETION_STATUSES = [
    "done",
    "missed",
    "partial",
    "rescheduled",
]

# Weather
DEFAULT_WEATHER_UNITS = "metric"  # "metric" (Celsius) or "imperial" (Fahrenheit)
DEFAULT_LOCATION = "London"

# Notifications
DEFAULT_PREP_TIME = 15  # minutes before activity to send reminder

# Display
DEFAULT_WEEK_START = "monday"  # or "sunday"
DATE_FORMAT = "%Y-%m-%d"
TIME_FORMAT = "%H:%M"
DATETIME_FORMAT = "%Y-%m-%d %H:%M"