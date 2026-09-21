from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import time
import logging

logger = logging.getLogger("nova.tools")


class BaseTool(ABC):
    """Abstract base class for all NOVA agent tools."""

    name: str
    description: str
    parameters: Dict[str, Any]
    requires_confirmation: bool = False

    @abstractmethod
    async def execute(self, **kwargs) -> Any:
        """Execute tool logic and return JSON-serializable result."""
        pass

    def to_schema(self) -> Dict[str, Any]:
        """Convert tool definition to standard schema."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters,
            "requires_confirmation": self.requires_confirmation,
        }


class ToolRegistry:
    """Registry managing available agent tools."""

    def __init__(self):
        self._tools: Dict[str, BaseTool] = {}

    def register(self, tool: BaseTool):
        self._tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Optional[BaseTool]:
        return self._tools.get(name)

    def list_tools(self) -> List[Dict[str, Any]]:
        return [tool.to_schema() for tool in self._tools.values()]

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        tool = self.get(name)
        if not tool:
            return {"status": "error", "error": f"Tool '{name}' not found."}

        start_time = time.time()
        try:
            result = await tool.execute(**arguments)
            latency = (time.time() - start_time) * 1000
            return {
                "status": "completed",
                "tool": name,
                "result": result,
                "latency_ms": round(latency, 2),
            }
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            logger.error(f"Error executing tool {name}: {e}", exc_info=True)
            return {
                "status": "failed",
                "tool": name,
                "error": str(e),
                "latency_ms": round(latency, 2),
            }
