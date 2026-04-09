"""Response models."""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class BaseResponse(BaseModel):
    """Base response model."""
    code: int = Field(200, description="Response code")
    message: str = Field("success", description="Response message")


class SkillManifestResponse(BaseModel):
    """Skill manifest for listing."""
    name: str
    version: str
    description: str
    parameters: Dict[str, Any]
    timeout: int = 5000
    retry: int = 3


class SkillListResponse(BaseResponse):
    """Response for skill list endpoint."""
    skills: List[SkillManifestResponse]


class SkillInvokeResponse(BaseResponse):
    """Response for skill invocation."""
    skill: str
    status: str
    result: Optional[Dict[str, Any]] = None
    execution_time_ms: float = 0.0


class ServiceStatus(BaseModel):
    """Individual service status."""
    status: str
    latency_ms: Optional[float] = None


class HealthResponse(BaseResponse):
    """Health check response."""
    status: str = Field("healthy", description="Overall health status")
    version: str = Field("1.0.0", description="API version")
    services: Dict[str, str] = Field(default_factory=dict, description="Service statuses")


class UsageInfo(BaseModel):
    """Token usage information."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatResponse(BaseModel):
    """Non-streaming chat response."""
    session_id: str
    content: str
    skill_results: Dict[str, Any] = Field(default_factory=dict)
    usage: UsageInfo = Field(default_factory=UsageInfo)
