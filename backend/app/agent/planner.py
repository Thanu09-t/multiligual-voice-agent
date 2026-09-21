import re
import json
import logging
from typing import Dict, Any, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from app.tools import get_tool_registry
from app.database.models import ToolCall

logger = logging.getLogger("nova.planner")


class AgentPlanner:
    """
    Intelligent planner that understands user intent, decides when tools
    are necessary, manages confirmation gates, and executes tools.
    """

    def __init__(self, db: AsyncSession, user_id: Optional[str] = None):
        self.db = db
        self.user_id = user_id
        self.tool_registry = get_tool_registry(db=db, user_id=user_id)

    async def plan_and_execute(
        self,
        user_input: str,
        conversation_id: Optional[str] = None,
    ) -> Tuple[Optional[str], Optional[Dict[str, Any]], bool, Optional[str]]:
        """
        Returns:
            (tool_name, tool_result, awaiting_confirmation, confirmation_prompt)
        """
        text = user_input.strip()

        # 1. Calculator intent
        # Detect expressions like "25% of 840", "25 percent of 840", "what is 15 * 40", "calculate 120 / 4"
        calc_patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:%|percent)\s*(?:of)?\s*(\d+(?:\.\d+)?)",
            r"(?:what is|calculate|compute)\s+([0-9\.\+\-\*\/\(\)\s\^xX]|times|multiplied\s+by|plus|minus|divided\s+by|percent|%|of)+",
            r"([0-9\.]+\s*(?:[\+\-\*\/\^]|times|multiplied\s+by|plus|minus|divided\s+by)\s*[0-9\.]+)",
        ]
        for pat in calc_patterns:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                expr = m.group(0)
                # Strip leading "what is " or "calculate " or "compute "
                expr = re.sub(r"^(what is|calculate|compute)\s+", "", expr, flags=re.IGNORECASE).strip()
                res = await self._run_tool("calculator", {"expression": expr}, conversation_id)
                return "calculator", res, False, None

        # 2. Weather intent
        weather_match = re.search(r"weather\s+(?:in|for|at)?\s*([a-zA-Z\s]+)", text, re.IGNORECASE)
        if weather_match:
            location = weather_match.group(1).strip()
            # Clean trailing question marks or punctuation
            location = re.sub(r"[?!.]+$", "", location)
            res = await self._run_tool("weather", {"location": location}, conversation_id)
            return "weather", res, False, None

        # 3. Consequential action intent (e.g. send email/notification)
        send_match = re.search(r"(send\s+(?:an?\s+)?(?:email|notification|message))\s+(?:to\s+)?([^\s]+)\s+(?:saying|with)?\s*(.*)", text, re.IGNORECASE)
        if send_match:
            recipient = send_match.group(2)
            msg = send_match.group(3) or "Automated notification"
            confirmation_prompt = f"I'm ready to send this notification to {recipient}. Should I send it?"
            return "send_notification", {"recipient": recipient, "message": msg}, True, confirmation_prompt

        # 4. Filter conversational and self-referential queries that should never trigger web search
        conversational_patterns = [
            r"^(?:who\s+are\s+you|who\s+made\s+you|who\s+created\s+you)",
            r"^(?:what\s+is\s+your\s+name|what\s+can\s+you\s+do|what\s+are\s+you|what\s+do\s+you\s+do)",
            r"^(?:how\s+are\s+you|how\s+do\s+you\s+do|how\s+is\s+it\s+going|how's\s+it\s+going)",
            r"^(?:tell\s+me\s+about\s+yourself)",
            r"^(?:hello|hi|hey|good\s+morning|good\s+evening|good\s+afternoon)",
            r"^(?:thank\s+you|thanks|bye|goodbye)",
            r"^(?:what\s+time|what\s+is\s+the\s+time|what's\s+the\s+time)",
        ]
        for cpat in conversational_patterns:
            if re.search(cpat, text, re.IGNORECASE):
                return None, None, False, None

        # If query refers to the agent (you/your/yourself) and is not an explicit search command, skip web search
        if re.search(r"\b(you|your|yourself)\b", text, re.IGNORECASE) and not re.search(r"^(?:search|google|look\s+up|find\s+online)\b", text, re.IGNORECASE):
            return None, None, False, None

        # 5. Web Search intent — natural language factual queries
        search_patterns = [
            # Explicit search commands
            r"^(?:search\s+(?:for|the\s+web\s+for)?|google|look\s+up\s+online|browse\s+the\s+web\s+for|find\s+online)\s+(.*)",
            # Who/What/When/Where/How — factual & current event queries
            r"^(?:who\s+is|who\s+was|who\s+are)\s+(.+)",
            r"^(?:what\s+is|what\s+are|what\s+was|what\s+were)\s+(?:the\s+)?(.+?)\??$",
            r"^(?:when\s+(?:did|was|is|are))\s+(.+)",
            r"^(?:where\s+(?:is|was|are))\s+(.+)",
            r"^(?:how\s+(?:much|many|does|did|is|are|do))\s+(.+)",
            # News / current events
            r"^(?:latest|recent|current|today'?s?)\s+(?:news|updates?|events?|developments?)\s+(?:about|on|regarding)?\s*(.*)",
            r"^(?:news|updates?)\s+(?:about|on|regarding)\s+(.*)",
            r"^(?:what(?:'s|\s+is)\s+happening\s+(?:with|in|to))\s+(.*)",
            # Tell me about / explain / define
            r"^(?:tell\s+me\s+about|explain|describe|give\s+me\s+info\s+(?:about|on)|information\s+(?:about|on))\s+(.*)",
            r"^(?:define|what\s+does\s+.+?\s+mean|meaning\s+of)\s+(.*)",
            # Research / look up
            r"^(?:research|look\s+up|find\s+(?:info|information|details?)\s+(?:about|on))\s+(.*)",
            # Biography / career
            r"^(?:biography|career|achievements?|net\s+worth)\s+(?:of|for)?\s*(.*)",
            # Price / stock
            r"^(?:price|cost|stock\s+price|share\s+price)\s+(?:of|for)?\s*(.*)",
        ]

        for pattern in search_patterns:
            m = re.search(pattern, text, re.IGNORECASE)
            if m:
                query = m.group(1).strip().rstrip("?!.").strip()
                if not query:
                    query = text
                res = await self._run_tool("web_search", {"query": query}, conversation_id)
                return "web_search", res, False, None

        return None, None, False, None

    async def _run_tool(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        conversation_id: Optional[str],
    ) -> Dict[str, Any]:
        """Execute tool and persist record to database."""
        result = await self.tool_registry.execute_tool(tool_name, arguments)

        if conversation_id:
            try:
                tc = ToolCall(
                    conversation_id=conversation_id,
                    tool_name=tool_name,
                    input_arguments=arguments,
                    output_result=result.get("result"),
                    status=result.get("status", "completed"),
                    latency_ms=result.get("latency_ms"),
                    error_message=result.get("error"),
                )
                self.db.add(tc)
                await self.db.commit()
            except Exception as e:
                logger.error(f"Failed to record tool call: {e}")

        return result
