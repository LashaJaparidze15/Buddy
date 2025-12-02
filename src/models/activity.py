"""Activity model for storing planned activities."""

from datetime import datetime, time
from typing import Optional

from sqlalchemy import Column, Integer, String, Text, Time, Boolean, DateTime
from sqlalchemy.orm import relationship

from src.models.database import Base


class Activity(Base):
    """Represents a scheduled activity."""
    
    __tablename__ = "activities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False, default="Other")
    
    # Scheduling
    start_time = Column(Time, nullable=False)
    duration = Column(Integer, nullable=True)  # in minutes
    recurrence = Column(String(20), nullable=False, default="once")
    # For custom recurrence: comma-separated days (e.g., "mon,wed,fri")
    custom_days = Column(String(50), nullable=True)
    
    # Additional info
    location = Column(String(200), nullable=True)
    prep_time = Column(Integer, default=15)  # minutes before to remind
    is_outdoor = Column(Boolean, default=False)  # for weather suggestions
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship to completions
    completions = relationship("Completion", back_populates="activity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Activity(id={self.id}, title='{self.title}', time={self.start_time})>"
    
    @property
    def duration_formatted(self) -> str:
        """Return duration as human-readable string."""
        if not self.duration:
            return "N/A"
        hours, mins = divmod(self.duration, 60)
        if hours and mins:
            return f"{hours}h {mins}m"
        elif hours:
            return f"{hours}h"
        return f"{mins}m"