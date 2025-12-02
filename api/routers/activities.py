"""Activities API endpoints."""

from datetime import date
from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.core import ActivityManager, CompletionManager
from src.utils import parse_date, parse_time

router = APIRouter()


# Request/Response Models
class ActivityCreate(BaseModel):
    title: str
    start_time: str
    category: str = "Other"
    description: Optional[str] = None
    duration: Optional[int] = None
    recurrence: str = "once"
    location: Optional[str] = None
    prep_time: int = 15
    is_outdoor: bool = False


class ActivityUpdate(BaseModel):
    title: Optional[str] = None
    start_time: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    duration: Optional[int] = None
    recurrence: Optional[str] = None
    location: Optional[str] = None
    prep_time: Optional[int] = None
    is_outdoor: Optional[bool] = None


class MarkComplete(BaseModel):
    status: str
    notes: Optional[str] = None
    date: Optional[str] = None


class ActivityResponse(BaseModel):
    id: int
    title: str
    start_time: str
    category: str
    description: Optional[str]
    duration: Optional[int]
    duration_formatted: str
    recurrence: str
    location: Optional[str]
    prep_time: int
    is_outdoor: bool
    is_active: bool

    class Config:
        from_attributes = True


def activity_to_response(activity) -> dict:
    """Convert Activity model to response dict."""
    return {
        "id": activity.id,
        "title": activity.title,
        "start_time": activity.start_time.strftime("%H:%M"),
        "category": activity.category,
        "description": activity.description,
        "duration": activity.duration,
        "duration_formatted": activity.duration_formatted,
        "recurrence": activity.recurrence,
        "location": activity.location,
        "prep_time": activity.prep_time,
        "is_outdoor": activity.is_outdoor,
        "is_active": activity.is_active,
    }


@router.get("")
def list_activities(
    date_str: Optional[str] = None,
    category: Optional[str] = None,
    week: bool = False,
    all: bool = False,
):
    """Get activities with optional filters."""
    manager = ActivityManager()
    
    try:
        if all:
            activities = manager.get_all(active_only=False)
        elif category:
            activities = manager.get_by_category(category)
        elif week:
            activities = manager.get_for_week()
        elif date_str:
            target = parse_date(date_str)
            activities = manager.get_for_date(target)
        else:
            activities = manager.get_for_today()
        
        return [activity_to_response(a) for a in activities]
    finally:
        manager.close()


@router.get("/{activity_id}")
def get_activity(activity_id: int):
    """Get a single activity by ID."""
    manager = ActivityManager()
    
    try:
        activity = manager.get_by_id(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        return activity_to_response(activity)
    finally:
        manager.close()


@router.post("")
def create_activity(data: ActivityCreate):
    """Create a new activity."""
    manager = ActivityManager()
    
    try:
        activity = manager.create(
            title=data.title,
            start_time=data.start_time,
            category=data.category,
            description=data.description,
            duration=data.duration,
            recurrence=data.recurrence,
            location=data.location,
            prep_time=data.prep_time,
            is_outdoor=data.is_outdoor,
        )
        return activity_to_response(activity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        manager.close()


@router.put("/{activity_id}")
def update_activity(activity_id: int, data: ActivityUpdate):
    """Update an existing activity."""
    manager = ActivityManager()
    
    try:
        activity = manager.update(
            activity_id=activity_id,
            title=data.title,
            start_time=data.start_time,
            category=data.category,
            description=data.description,
            duration=data.duration,
            recurrence=data.recurrence,
            location=data.location,
            prep_time=data.prep_time,
            is_outdoor=data.is_outdoor,
        )
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        return activity_to_response(activity)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        manager.close()


@router.delete("/{activity_id}")
def delete_activity(activity_id: int):
    """Delete an activity."""
    manager = ActivityManager()
    
    try:
        success = manager.delete(activity_id)
        if not success:
            raise HTTPException(status_code=404, detail="Activity not found")
        return {"message": "Activity deleted"}
    finally:
        manager.close()


@router.post("/{activity_id}/toggle")
def toggle_activity(activity_id: int):
    """Toggle activity active status."""
    manager = ActivityManager()
    
    try:
        activity = manager.toggle(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        return activity_to_response(activity)
    finally:
        manager.close()


@router.post("/{activity_id}/mark")
def mark_activity(activity_id: int, data: MarkComplete):
    """Mark activity as done/missed/partial/rescheduled."""
    manager = CompletionManager()
    activity_manager = ActivityManager()
    
    try:
        activity = activity_manager.get_by_id(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        target_date = parse_date(data.date) if data.date else None
        
        completion = manager.mark(
            activity_id=activity_id,
            status=data.status,
            target_date=target_date,
            notes=data.notes,
        )
        
        return {
            "activity_id": completion.activity_id,
            "date": str(completion.date),
            "status": completion.status,
            "notes": completion.notes,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        manager.close()
        activity_manager.close()


@router.get("/{activity_id}/history")
def get_activity_history(activity_id: int, limit: int = 10):
    """Get completion history for an activity."""
    manager = CompletionManager()
    activity_manager = ActivityManager()
    
    try:
        activity = activity_manager.get_by_id(activity_id)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")
        
        completions = manager.get_for_activity(activity_id, limit=limit)
        streak = manager.get_streak(activity_id)
        
        return {
            "activity": activity_to_response(activity),
            "streak": streak,
            "history": [
                {
                    "date": str(c.date),
                    "status": c.status,
                    "notes": c.notes,
                }
                for c in completions
            ],
        }
    finally:
        manager.close()
        activity_manager.close()