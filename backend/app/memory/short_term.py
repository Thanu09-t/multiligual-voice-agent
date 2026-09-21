from typing import List, Dict, Any, Optional


class ShortTermMemoryManager:
    """
    Manages conversational context sliding window and summaries
    to prevent unlimited context bloat.
    """

    def __init__(self, max_recent_messages: int = 8):
        self.max_recent_messages = max_recent_messages

    def manage_context(
        self,
        messages: List[Dict[str, str]],
        existing_summary: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Splits messages into summarized context and recent active window.
        """
        if len(messages) <= self.max_recent_messages:
            return {
                "active_messages": messages,
                "summary": existing_summary,
            }

        # Overflow: older messages get summarized
        overflow_count = len(messages) - self.max_recent_messages
        older_messages = messages[:overflow_count]
        active_window = messages[overflow_count:]

        # Compact summary generation
        summary_points = []
        if existing_summary:
            summary_points.append(existing_summary)

        for m in older_messages:
            prefix = "User" if m.get("role") == "user" else "Agent"
            content = m.get("content", "")
            summary_points.append(f"{prefix}: {content[:80]}...")

        new_summary = " | ".join(summary_points)
        if len(new_summary) > 500:
            new_summary = new_summary[-500:]

        return {
            "active_messages": active_window,
            "summary": new_summary,
        }
