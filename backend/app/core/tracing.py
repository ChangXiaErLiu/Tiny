"""Request tracing system for debugging and monitoring."""
import uuid
import time
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from contextvars import ContextVar
from threading import Lock

logger = logging.getLogger(__name__)

_current_trace_id: ContextVar[Optional[str]] = ContextVar('current_trace_id', default=None)


@dataclass
class TraceStep:
    """A single step in a trace."""
    step_id: str
    name: str
    start_time: float
    end_time: Optional[float] = None
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    success: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            'step_id': self.step_id,
            'name': self.name,
            'start_time': self.start_time,
            'start_time_str': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': self.end_time,
            'duration_ms': (self.end_time - self.start_time) * 1000 if self.end_time else None,
            'data': self.data,
            'error': self.error,
            'success': self.success
        }


@dataclass
class RequestTrace:
    """Complete trace of a request."""
    trace_id: str
    request_id: str
    start_time: float
    end_time: Optional[float] = None
    steps: List[TraceStep] = field(default_factory=list)
    request_data: Optional[Dict[str, Any]] = None
    final_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'trace_id': self.trace_id,
            'request_id': self.request_id,
            'start_time': self.start_time,
            'start_time_str': datetime.fromtimestamp(self.start_time).isoformat(),
            'end_time': self.end_time,
            'duration_ms': (self.end_time - self.start_time) * 1000 if self.end_time else None,
            'steps': [s.to_dict() for s in self.steps],
            'request_data': self.request_data,
            'final_result': self.final_result,
            'error': self.error
        }


class TraceStore:
    """In-memory store for request traces."""

    def __init__(self, max_traces: int = 100, retention_hours: int = 24):
        self._traces: Dict[str, RequestTrace] = {}
        self._lock = Lock()
        self._max_traces = max_traces
        self._retention_hours = retention_hours

    def add_trace(self, trace: RequestTrace):
        """Add a new trace to the store."""
        with self._lock:
            self._cleanup_old_traces()
            self._traces[trace.trace_id] = trace
            logger.debug(f"Stored trace {trace.trace_id}, total traces: {len(self._traces)}")

    def get_trace(self, trace_id: str) -> Optional[RequestTrace]:
        """Get a trace by ID."""
        with self._lock:
            return self._traces.get(trace_id)

    def get_recent_traces(self, limit: int = 20) -> List[RequestTrace]:
        """Get recent traces."""
        with self._lock:
            traces = sorted(self._traces.values(), key=lambda t: t.start_time, reverse=True)
            return traces[:limit]

    def list_trace_ids(self, limit: int = 50) -> List[Dict[str, Any]]:
        """List trace IDs with basic info."""
        with self._lock:
            traces = sorted(self._traces.values(), key=lambda t: t.start_time, reverse=True)
            return [
                {
                    'trace_id': t.trace_id,
                    'request_id': t.request_id,
                    'start_time_str': datetime.fromtimestamp(t.start_time).isoformat(),
                    'duration_ms': (t.end_time - t.start_time) * 1000 if t.end_time else None,
                    'error': t.error,
                    'step_count': len(t.steps)
                }
                for t in traces[:limit]
            ]

    def _cleanup_old_traces(self):
        """Remove old traces beyond retention period."""
        cutoff = time.time() - (self._retention_hours * 3600)
        to_remove = [tid for tid, t in self._traces.items() if t.start_time < cutoff]
        for tid in to_remove:
            del self._traces[tid]

        if len(self._traces) > self._max_traces:
            sorted_traces = sorted(self._traces.items(), key=lambda x: x[1].start_time)
            for tid, _ in sorted_traces[:len(self._traces) - self._max_traces]:
                del self._traces[tid]


_trace_store = TraceStore()


class RequestTracer:
    """Context manager for tracing a request."""

    def __init__(self, request_id: str, request_data: Optional[Dict[str, Any]] = None):
        self.trace_id = str(uuid.uuid4())[:8]
        self.request_id = request_id
        self.request_data = request_data
        self.trace = RequestTrace(
            trace_id=self.trace_id,
            request_id=request_id,
            start_time=time.time(),
            request_data=request_data
        )
        self._step_counter = 0
        self._current_step: Optional[TraceStep] = None

    def __enter__(self):
        _current_trace_id.set(self.trace_id)
        logger.info(f"[{self.trace_id}] Request started: {self.request_id}")
        if self.request_data:
            logger.info(f"[{self.trace_id}] Request data: {json.dumps(self.request_data, ensure_ascii=False)[:500]}")
        _trace_store.add_trace(self.trace)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        _current_trace_id.set(None)
        self.trace.end_time = time.time()

        if exc_type:
            self.trace.error = f"{exc_type.__name__}: {exc_val}"
            logger.error(f"[{self.trace_id}] Request failed: {self.trace.error}")

        logger.info(f"[{self.trace_id}] Request ended, duration: {(self.trace.end_time - self.trace.start_time) * 1000:.2f}ms")
        return False

    def begin_step(self, name: str, data: Optional[Dict[str, Any]] = None) -> str:
        """Begin a new step in the trace."""
        self._step_counter += 1
        step_id = f"step_{self._step_counter}"
        self._current_step = TraceStep(
            step_id=step_id,
            name=name,
            start_time=time.time(),
            data=data
        )
        logger.info(f"[{self.trace_id}] → {name}" + (f" | {json.dumps(data, ensure_ascii=False)[:200]}" if data else ""))
        return step_id

    def end_step(self, step_id: str, data: Optional[Dict[str, Any]] = None, error: Optional[str] = None):
        """End the current step."""
        if self._current_step and self._current_step.step_id == step_id:
            self._current_step.end_time = time.time()
            self._current_step.data = data
            if error:
                self._current_step.error = error
                self._current_step.success = False
                logger.warning(f"[{self.trace_id}] ✗ {self._current_step.name}: {error}")
            else:
                logger.info(f"[{self.trace_id}] ✓ {self._current_step.name} ({(self._current_step.end_time - self._current_step.start_time) * 1000:.2f}ms)")
            self.trace.steps.append(self._current_step)
            self._current_step = None

    def set_result(self, result: Dict[str, Any]):
        """Set the final result."""
        self.trace.final_result = result
        logger.debug(f"[{self.trace_id}] Result: {json.dumps(result, ensure_ascii=False)[:300]}")

    def get_trace_id(self) -> str:
        """Get the current trace ID."""
        return self.trace_id


def get_tracer() -> Optional[RequestTracer]:
    """Get the current tracer if exists."""
    trace_id = _current_trace_id.get()
    if trace_id:
        return _trace_store.get_trace(trace_id)
    return None


def get_trace_store() -> TraceStore:
    """Get the global trace store."""
    return _trace_store


def log_step(name: str, data: Optional[Dict[str, Any]] = None):
    """Log a simple step without full tracing context."""
    trace_id = _current_trace_id.get()
    if trace_id:
        logger.info(f"[{trace_id}] {name}" + (f" | {json.dumps(data, ensure_ascii=False)[:200]}" if data else ""))
    else:
        logger.info(f"{name}" + (f" | {json.dumps(data, ensure_ascii=False)[:200]}" if data else ""))
