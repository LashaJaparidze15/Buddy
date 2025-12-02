"""Completion model for tracking activity completion status."""

from datetime import datetime, date

from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.models.database import Base


class Completion(Base):
    """Tracks completion status of activities."""
    
    __tablename__ = "completions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), nullable=False)
    date = Column(Date, nullable=False)  # The date this completion record is for
    
    # Status: done, missed, partial, rescheduled
    status = Column(String(20), nullable=False)
    
    # Optional details
    completed_at = Column(DateTime, nullable=True)  # Actual completion time
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.now)
    
    # Relationship back to activity
    activity = relationship("Activity", back_populates="completions")
    
    def __repr__(self):
        return f"<Completion(activity_id={self.activity_id}, date={self.date}, status='{self.status}')>"