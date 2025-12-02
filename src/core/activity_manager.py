"""Activity manager for CRUD operations."""

from datetime import date, time
from typing import Optional
from sqlalchemy.orm import Session

from src.models import Activity, Completion, SessionLocal
from src.utils import (
    parse_time,
    validate_category,
    validate_recurrence,
    validate_duration,
    validate_prep_time,
    is_weekday,
    is_weekend,
    get_day_name,
    get_week_bounds,
)


class ActivityManager:
    """Manages activity CRUD operations."""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize with optional database session."""
        self.db = db or SessionLocal()
    
    def create(
        self,
        title: str,
        start_time: str,
        category: str = "Other",
        description: Optional[str] = None,
        duration: Optional[int] = None,
        recurrence: str = "once",
        custom_days: Optional[str] = None,
        location: Optional[str] = None,
        prep_time: int = 15,
        is_outdoor: bool = False,
    ) -> Activity:
        """Create a new activity."""
        # Validate inputs
        parsed_time = parse_time(start_time)
        validated_category = validate_category(category)
        validated_recurrence = validate_recurrence(recurrence)
        
        if duration:
            duration = validate_duration(duration)
        if prep_time:
            prep_time = validate_prep_time(prep_time)
        
        # Create activity
        activity = Activity(
            title=title,
            description=description,
            category=validated_category,
            start_time=parsed_time,
            duration=duration,
            recurrence=validated_recurrence,
            custom_days=custom_days,
            location=location,
            prep_time=prep_time,
            is_outdoor=is_outdoor,
        )
        
        self.db.add(activity)
        self.db.commit()
        self.db.refresh(activity)
        
        return activity
    
    def get_by_id(self, activity_id: int) -> Optional[Activity]:
        """Get activity by ID."""
        return self.db.query(Activity).filter(Activity.id == activity_id).first()
    
    def get_all(self, active_only: bool = True) -> list[Activity]:
        """Get all activities."""
        query = self.db.query(Activity)
        if active_only:
            query = query.filter(Activity.is_active == True)
        return query.order_by(Activity.start_time).all()
    
    def get_by_category(self, category: str, active_only: bool = True) -> list[Activity]:
        """Get activities by category."""
        validated_category = validate_category(category)
        query = self.db.query(Activity).filter(Activity.category == validated_category)
        if active_only:
            query = query.filter(Activity.is_active == True)
        return query.order_by(Activity.start_time).all()
    
    def get_for_date(self, target_date: date) -> list[Activity]:
        """Get activities scheduled for a specific date."""
        all_activities = self.get_all(active_only=True)
        result = []
        
        for activity in all_activities:
            if self._is_scheduled_for_date(activity, target_date):
                result.append(activity)
        
        return sorted(result, key=lambda a: a.start_time)
    
    def get_for_today(self) -> list[Activity]:
        """Get today's activities."""
        return self.get_for_date(date.today())
    
    def get_for_week(self, target_date: Optional[date] = None) -> list[Activity]:
        """Get activities for the week containing target_date."""
        week_start, week_end = get_week_bounds(target_date)
        all_activities = self.get_all(active_only=True)
        result = []
        
        current = week_start
        while current <= week_end:
            for activity in all_activities:
                if self._is_scheduled_for_date(activity, current):
                    if activity not in result:
                        result.append(activity)
            current = current.replace(day=current.day + 1)
        
        return sorted(result, key=lambda a: a.start_time)
    
    def _is_scheduled_for_date(self, activity: Activity, target_date: date) -> bool:
        """Check if activity is scheduled for a specific date."""
        recurrence = activity.recurrence
        
        if recurrence == "daily":
            return True
        elif recurrence == "weekdays":
            return is_weekday(target_date)
        elif recurrence == "weekends":
            return is_weekend(target_date)
        elif recurrence == "weekly":
            # Same day of week as created
            return target_date.weekday() == activity.created_at.weekday()
        elif recurrence == "custom" and activity.custom_days:
            day_name = get_day_name(target_date)[:3]  # "mon", "tue", etc.
            return day_name in activity.custom_days.lower()
        elif recurrence == "once":
            # One-time activities: scheduled for creation date only
            return target_date == activity.created_at.date()
        
        return False
    
    def update(
        self,
        activity_id: int,
        title: Optional[str] = None,
        start_time: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        duration: Optional[int] = None,
        recurrence: Optional[str] = None,
        location: Optional[str] = None,
        prep_time: Optional[int] = None,
        is_outdoor: Optional[bool] = None,
    ) -> Optional[Activity]:
        """Update an existing activity."""
        activity = self.get_by_id(activity_id)
        if not activity:
            return None
        
        if title:
            activity.title = title
        if start_time:
            activity.start_time = parse_time(start_time)
        if category:
            activity.category = validate_category(category)
        if description is not None:
            activity.description = description
        if duration:
            activity.duration = validate_duration(duration)
        if recurrence:
            activity.recurrence = validate_recurrence(recurrence)
        if location is not None:
            activity.location = location
        if prep_time is not None:
            activity.prep_time = validate_prep_time(prep_time)
        if is_outdoor is not None:
            activity.is_outdoor = is_outdoor
        
        self.db.commit()
        self.db.refresh(activity)
        
        return activity
    
    def delete(self, activity_id: int) -> bool:
        """Delete an activity."""
        activity = self.get_by_id(activity_id)
        if not activity:
            return False
        
        self.db.delete(activity)
        self.db.commit()
        return True
    
    def toggle(self, activity_id: int) -> Optional[Activity]:
        """Toggle activity active status."""
        activity = self.get_by_id(activity_id)
        if not activity:
            return None
        
        activity.is_active = not activity.is_active
        self.db.commit()
        self.db.refresh(activity)
        
        return activity
    
    def search(self, query: str) -> list[Activity]:
        """Search activities by title or description."""
        search_term = f"%{query}%"
        return (
            self.db.query(Activity)
            .filter(
                (Activity.title.ilike(search_term)) | 
                (Activity.description.ilike(search_term))
            )
            .order_by(Activity.start_time)
            .all()
        )
    
    def close(self):
        """Close database session."""
        self.db.close()