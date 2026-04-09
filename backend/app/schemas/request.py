"""Request models."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any


class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., min_length=1, description="User message")
    session_id: Optional[str] = Field(None, description="Session ID for continuity")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context")


class SkillInvokeRequest(BaseModel):
    """Skill invocation request model."""
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Skill parameters")


class HealthCheckRequest(BaseModel):
    """Health check request model."""
    pass
