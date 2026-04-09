"""Agent core with LLM-based skill understanding and dispatching."""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, AsyncIterator
from enum import Enum
import time
import uuid
import logging

logger = logging.getLogger(__name__)


class IntentType(Enum):
    """Enumeration of intent types determined by LLM."""
    WEATHER_QUERY = "weather_query"
    TRAVEL_PLAN = "travel_plan"
    COMBINED = "combined"
    GENERAL = "general_chat"
    UNKNOWN = "unknown"


@dataclass
class Intent:
    """Represents a parsed user intent with LLM understanding."""
    type: IntentType
    confidence: float
    parameters: Dict[str, Any] = field(default_factory=dict)
    target_skills: List[str] = field(default_factory=list)
    reasoning: str = ""
    raw_input: str = ""


@dataclass
class SkillExecution:
    """Represents a skill execution request."""
    skill_name: str
    parameters: Dict[str, Any]
    references: Dict[str, str] = field(default_factory=dict)
    script_interpretation: str = ""


@dataclass
class AgentResponse:
    """Response from agent."""
    session_id: str
    content: str
    skill_results: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    usage: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "content": self.content,
            "skill_results": self.skill_results,
            "metadata": self.metadata,
            "usage": self.usage
        }


@dataclass
class StreamEvent:
    """Event for streaming responses."""
    event_type: str
    data: Dict[str, Any]
    
    def to_sse_data(self) -> str:
        return f"event: {self.event_type}\ndata: {self.data}\n\n"


class BaseAgent(ABC):
    """Abstract base class for declarative skill-based agents."""
    
    def __init__(self, name: str = "base_agent"):
        self.name = name
        self.sessions: Dict[str, Dict] = {}
    
    @abstractmethod
    async def understand_intent(
        self, 
        user_input: str, 
        available_skills: List[Dict[str, Any]]
    ) -> Intent:
        """Use LLM to understand user intent from natural language."""
        pass
    
    @abstractmethod
    async def prepare_skill_execution(
        self,
        intent: Intent,
        skill_manifests: Dict[str, Dict[str, Any]]
    ) -> List[SkillExecution]:
        """Prepare skill execution parameters based on intent and skill docs."""
        pass
    
    @abstractmethod
    async def generate_response(
        self,
        intent: Intent,
        skill_results: Dict[str, Any]
    ) -> str:
        """Generate natural language response from skill results."""
        pass
    
    def create_session(self) -> str:
        """Create a new chat session."""
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created_at": time.time(),
            "history": []
        }
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def add_to_history(self, session_id: str, role: str, content: str) -> None:
        """Add message to session history."""
        if session_id in self.sessions:
            self.sessions[session_id]["history"].append({
                "role": role,
                "content": content,
                "timestamp": time.time()
            })
