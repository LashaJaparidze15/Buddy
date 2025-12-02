"""Input validation functions."""

from src.config.defaults import CATEGORIES, RECURRENCE_OPTIONS, COMPLETION_STATUSES


def validate_category(category: str) -> str:
    """Validate and normalize category."""
    # Case-insensitive match
    category_lower = category.lower()
    for cat in CATEGORIES:
        if cat.lower() == category_lower:
            return cat
    
    valid = ", ".join(CATEGORIES)
    raise ValueError(f"Invalid category: '{category}'. Valid options: {valid}")


def validate_recurrence(recurrence: str) -> str:
    """Validate recurrence option."""
    recurrence_lower = recurrence.lower()
    if recurrence_lower in RECURRENCE_OPTIONS:
        return recurrence_lower
    
    valid = ", ".join(RECURRENCE_OPTIONS)
    raise ValueError(f"Invalid recurrence: '{recurrence}'. Valid options: {valid}")


def validate_status(status: str) -> str:
    """Validate completion status."""
    status_lower = status.lower()
    if status_lower in COMPLETION_STATUSES:
        return status_lower
    
    valid = ", ".join(COMPLETION_STATUSES)
    raise ValueError(f"Invalid status: '{status}'. Valid options: {valid}")


def validate_duration(duration: int) -> int:
    """Validate duration in minutes."""
    if duration < 1:
        raise ValueError("Duration must be at least 1 minute")
    if duration > 1440:  # 24 hours
        raise ValueError("Duration cannot exceed 24 hours (1440 minutes)")
    return duration


def validate_prep_time(prep_time: int) -> int:
    """Validate preparation time in minutes."""
    if prep_time < 0:
        raise ValueError("Preparation time cannot be negative")
    if prep_time > 180:  # 3 hours
        raise ValueError("Preparation time cannot exceed 3 hours (180 minutes)")
    return prep_time