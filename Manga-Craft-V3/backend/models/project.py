"""
Project Model
Represents a manga project in the system
"""

from beanie import Document, Indexed
from datetime import datetime
from typing import Optional
from pydantic import Field


class Project(Document):
    """Project document for MongoDB"""
    
    name: str = Indexed()
    description: Optional[str] = None
    user_id: str = Indexed()  # Foreign key to User
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "projects"
        indexes = [
            "name",
            "user_id"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "My Manga Story",
                "description": "A story about a young volleyball player",
                "user_id": "user_id_here"
            }
        }
