"""
Message Model
Represents an individual message in a conversation
"""

from beanie import Document, Indexed
from datetime import datetime
from typing import Optional, List
from pydantic import Field


class Message(Document):
    """Message document for MongoDB"""
    
    conversation_id: str = Indexed()  # Foreign key to Conversation
    role: str                          # "user" or "assistant"
    content: str                       # Message content
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Future extensibility (NOT implementing in V3.8):
    # attachments: List[str] = None  # File paths
    # metadata: dict = None           # AI metadata, structured outputs
    
    class Settings:
        name = "messages"
        indexes = [
            "conversation_id",
            "created_at"  # For message ordering
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": "conversation_id_here",
                "role": "user",
                "content": "Hello, AI!"
            }
        }
