"""
Project Memory Model
Stores character profiles, story elements, locations, and other project context
"""

from beanie import Document, Indexed
from datetime import datetime
from pydantic import Field
from typing import Optional, List


class ProjectMemory(Document):
    """
    Project Memory - stores contextual information about a manga project
    
    Types:
    - character: Character profiles, relationships, development
    - story: Plot points, arcs, events, summaries
    - location: Settings, world building, geography
    - note: General notes, ideas, references
    - other: Custom memory types
    """
    
    # Project association
    project_id: str = Indexed()
    user_id: str = Indexed()
    
    # Memory content
    type: str = Indexed()  # character, story, location, note, other
    title: str
    content: str
    tags: List[str] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "project_memories"
        indexes = [
            "project_id",
            "user_id",
            "type",
            "tags",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "type": "character",
                "title": "Main Protagonist",
                "content": "A young volleyball player with determination...",
                "tags": ["protagonist", "sports", "high-school"],
                "created_at": "2026-11-18T10:00:00Z",
                "updated_at": "2026-11-18T10:00:00Z"
            }
        }
