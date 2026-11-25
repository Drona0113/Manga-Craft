"""
Chat Schemas
Request and response shapes for the AI chat endpoint.
"""

from pydantic import BaseModel, Field

class ChatRequest(BaseModel):
    """Body sent by the frontend when the user sends a message."""
    conversation_id: str
    content: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    """Returned after the AI replies."""
    user_message_id: str
    assistant_message_id: str
    assistant_content: str
