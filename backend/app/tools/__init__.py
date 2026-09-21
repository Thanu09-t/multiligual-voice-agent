from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.tools.base import ToolRegistry
from app.tools.calculator import CalculatorTool
from app.tools.weather import WeatherTool
from app.tools.web_search import WebSearchTool
from app.tools.file_search import FileSearchTool
from app.tools.consequential import SendNotificationTool


def get_tool_registry(db: Optional[AsyncSession] = None, user_id: Optional[str] = None) -> ToolRegistry:
    registry = ToolRegistry()
    registry.register(CalculatorTool())
    registry.register(WeatherTool())
    registry.register(WebSearchTool())
    registry.register(SendNotificationTool())
    if db:
        registry.register(FileSearchTool(db=db, user_id=user_id))
    return registry
