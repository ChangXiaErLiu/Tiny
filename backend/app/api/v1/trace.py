"""Trace API endpoints for debugging and monitoring."""
from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel

from ...core.tracing import get_trace_store

router = APIRouter()


class TraceStepInfo(BaseModel):
    """Trace step information."""
    step_id: str
    name: str
    start_time: float
    start_time_str: str
    end_time: Optional[float]
    duration_ms: Optional[float]
    data: Optional[dict]
    error: Optional[str]
    success: bool


class TraceInfo(BaseModel):
    """Trace information."""
    trace_id: str
    request_id: str
    start_time: float
    start_time_str: str
    end_time: Optional[float]
    duration_ms: Optional[float]
    error: Optional[str]
    step_count: int


class TraceDetail(BaseModel):
    """Detailed trace with steps."""
    trace_id: str
    request_id: str
    start_time: float
    start_time_str: str
    end_time: Optional[float]
    duration_ms: Optional[float]
    steps: List[TraceStepInfo]
    request_data: Optional[dict]
    final_result: Optional[dict]
    error: Optional[str]


@router.get("/traces")
async def list_traces(limit: int = Query(default=20, ge=1, le=100)):
    """List recent trace IDs with basic info."""
    store = get_trace_store()
    traces = store.list_trace_ids(limit=limit)
    return {
        "count": len(traces),
        "traces": traces
    }


@router.get("/traces/{trace_id}")
async def get_trace(trace_id: str):
    """Get detailed trace by ID."""
    store = get_trace_store()
    trace = store.get_trace(trace_id)

    if not trace:
        return {"error": f"Trace {trace_id} not found"}

    return {
        "trace": trace.to_dict()
    }


@router.get("/traces/latest")
async def get_latest_trace():
    """Get the most recent trace."""
    store = get_trace_store()
    traces = store.get_recent_traces(limit=1)

    if not traces:
        return {"error": "No traces found"}

    return {
        "trace": traces[0].to_dict()
    }
