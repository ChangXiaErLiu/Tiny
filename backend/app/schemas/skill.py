"""Skill-related schemas."""
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime


class SkillExecutionEvent(BaseModel):
    """Event emitted during skill execution."""
    event_type: str
    skill: str
    status: str
    data: Optional[Dict[str, Any]] = None


class StreamEvent(BaseModel):
    """SSE stream event."""
    event: str = Field(..., description="Event name")
    data: Dict[str, Any] = Field(..., description="Event data")
