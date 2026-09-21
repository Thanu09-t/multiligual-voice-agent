from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional


class AgentStatus(str, Enum):
    IDLE = "IDLE"
    LISTENING = "LISTENING"
    THINKING = "THINKING"
    USING_TOOL = "USING_TOOL"
    GENERATING = "GENERATING"
    SPEAKING = "SPEAKING"
    INTERRUPTED = "INTERRUPTED"
    ERROR = "ERROR"


@dataclass
class AgentState:
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    current_task: Optional[str] = None
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    relevant_memories: List[Dict[str, Any]] = field(default_factory=list)
    retrieved_documents: List[Dict[str, Any]] = field(default_factory=list)
    available_tools: List[str] = field(default_factory=list)
    active_tool: Optional[str] = None
    tool_results: List[Dict[str, Any]] = field(default_factory=list)
    awaiting_confirmation: bool = False
    confirmation_prompt: Optional[str] = None
    agent_status: AgentStatus = AgentStatus.IDLE
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "conversation_id": self.conversation_id,
            "current_task": self.current_task,
            "relevant_memories": self.relevant_memories,
            "retrieved_documents": self.retrieved_documents,
            "available_tools": self.available_tools,
            "active_tool": self.active_tool,
            "tool_results": self.tool_results,
            "awaiting_confirmation": self.awaiting_confirmation,
            "confirmation_prompt": self.confirmation_prompt,
            "agent_status": self.agent_status.value,
            "error_message": self.error_message,
        }
