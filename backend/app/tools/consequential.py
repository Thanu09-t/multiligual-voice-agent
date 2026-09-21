from typing import Any, Dict
from app.tools.base import BaseTool


class SendNotificationTool(BaseTool):
    """Consequential action tool that requires explicit user confirmation before executing."""

    name = "send_notification"
    description = "Send an email or message notification. Consequential action requiring confirmation."
    parameters = {
        "type": "object",
        "properties": {
            "recipient": {
                "type": "string",
                "description": "Email address or contact identifier of the recipient.",
            },
            "message": {
                "type": "string",
                "description": "Content of the notification to transmit.",
            },
        },
        "required": ["recipient", "message"],
    }
    requires_confirmation = True

    async def execute(self, recipient: str, message: str, **kwargs) -> Any:
        # In a real environment, sends email/SMS
        return {
            "status": "sent",
            "recipient": recipient,
            "message": message,
            "timestamp": "now",
        }
