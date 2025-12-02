"""Completion tracking for activities."""

from datetime import date, datetime
from typing import Optional
from sqlalchemy.orm import Session

from src.models import Activity, Completion, SessionLocal
from src.utils import validate_status, format_date


class CompletionManager:
    """Manages activity completion tracking."""
    
    def __init__(self, db: Optional[Session] = None):
        """Initialize with optional database session."""
        self.db = db or SessionLocal()
    
    def mark(
        self,
        activity_id: int,
        status: str,
        target_date: Optional[date] = None,
        notes: Optional[str] = None,
    ) -> Optional[Completion]:
        """Mark an activity with a completion status."""
        # Validate status
        validated_status = validate_status(status)
        
        # Default to today
        if target_date is None:
            target_date = date.today()
        
        # Check if activity exists
        activity = self.db.query(Activity).filter(Activity.id == activity_id).first()
        if not activity:
            return None
        
        # Check if completion record already exists for this date
        existing = (
            self.db.query(Completion)
            .filter(Completion.activity_id == activity_id)
            .filter(Completion.date == target_date)
            .first()
        )
        
        if existing:
            # Update existing record
            existing.status = validated_status
            existing.notes = notes if notes else existing.notes
            if validated_status == "done":
                existing.completed_at = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            return existing
        
        # Create new completion record
        completion = Completion(
            activity_id=activity_id,
            date=target_date,
            status=validated_status,
            completed_at=datetime.now() if validated_status == "done" else None,
            notes=notes,
        )
        
        self.db.add(completion)
        self.db.commit()
        self.db.refresh(completion)
        
        return completion
    
    def get_for_date(self, target_date: Optional[date] = None) -> list[Completion]:
        """Get all completions for a specific date."""
        if target_date is None:
            target_date = date.today()
        
        return (
            self.db.query(Completion)
            .filter(Completion.date == target_date)
            .all()
        )
    
    def get_for_activity(
        self,
        activity_id: int,
        limit: int = 30
    ) -> list[Completion]:
        """Get completion history for an activity."""
        return (
            self.db.query(Completion)
            .filter(Completion.activity_id == activity_id)
            .order_by(Completion.date.desc())
            .limit(limit)
            .all()
        )
    
    def get_completion_status(
        self,
        activity_id: int,
        target_date: Optional[date] = None
    ) -> Optional[str]:
        """Get completion status for activity on a date."""
        if target_date is None:
            target_date = date.today()
        
        completion = (
            self.db.query(Completion)
            .filter(Completion.activity_id == activity_id)
            .filter(Completion.date == target_date)
            .first()
        )
        
        return completion.status if completion else None
    
    def get_stats(
        self,
        start_date: date,
        end_date: date
    ) -> dict:
        """Get completion statistics for a date range."""
        completions = (
            self.db.query(Completion)
            .filter(Completion.date >= start_date)
            .filter(Completion.date <= end_date)
            .all()
        )
        
        total = len(completions)
        if total == 0:
            return {
                "total": 0,
                "done": 0,
                "missed": 0,
                "partial": 0,
                "rescheduled": 0,
                "completion_rate": 0.0,
            }
        
        done = sum(1 for c in completions if c.status == "done")
        missed = sum(1 for c in completions if c.status == "missed")
        partial = sum(1 for c in completions if c.status == "partial")
        rescheduled = sum(1 for c in completions if c.status == "rescheduled")
        
        # Count done + partial as "completed" for rate
        completion_rate = ((done + partial * 0.5) / total) * 100
        
        return {
            "total": total,
            "done": done,
            "missed": missed,
            "partial": partial,
            "rescheduled": rescheduled,
            "completion_rate": round(completion_rate, 1),
        }
    
    def get_streak(self, activity_id: int) -> int:
        """Calculate current streak for an activity."""
        completions = (
            self.db.query(Completion)
            .filter(Completion.activity_id == activity_id)
            .filter(Completion.status == "done")
            .order_by(Completion.date.desc())
            .all()
        )
        
        if not completions:
            return 0
        
        streak = 0
        expected_date = date.today()
        
        for completion in completions:
            if completion.date == expected_date:
                streak += 1
                expected_date = expected_date.replace(day=expected_date.day - 1)
            elif completion.date < expected_date:
                # Gap in streak
                break
        
        return streak
    
    def close(self):
        """Close database session."""
        self.db.close()