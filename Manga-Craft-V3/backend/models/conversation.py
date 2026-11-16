"""
Conversation Model
Represents a conversation within a project
"""

from beanie import Document, Indexed
from datetime import datetime
from typing import Optional
from pydantic import Field


class Conversation(Document):
    """Conversation document for MongoDB"""
    
    project_id: str = Indexed()  # Foreign key to Project
    user_id: str = Indexed()     # Foreign key to User
    title: str                   # Conversation title
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "conversations"
        indexes = [
            "project_id",
            "user_id",
            "updated_at"  # For sorting by recency
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "project_id_here",
                "user_id": "user_id_here",
                "title": "My Conversation"
            }
        }
