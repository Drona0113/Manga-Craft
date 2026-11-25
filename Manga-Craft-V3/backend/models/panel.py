"""
Panel Model
Stores uploaded manga panels for projects
"""

from beanie import Document, Indexed
from datetime import datetime
from pydantic import Field
from typing import Optional


class Panel(Document):
    """
    Panel - uploaded manga panel for a project
    
    Stores file metadata and path for uploaded panel images
    """
    
    # Project association
    project_id: str = Indexed()
    user_id: str = Indexed()
    
    # File metadata
    file_path: str  # Local file path (will migrate to object storage in V3.16)
    file_name: str
    file_size: int  # Size in bytes
    file_type: str  # MIME type (image/jpeg, image/png, etc.)
    width: Optional[int] = None   # Image width in pixels
    height: Optional[int] = None  # Image height in pixels
    notes: Optional[str] = None   # Optional creator notes for the panel
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "panels"
        indexes = [
            "project_id",
            "user_id",
            "created_at",
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "project_id": "507f1f77bcf86cd799439011",
                "user_id": "507f1f77bcf86cd799439012",
                "file_path": "panels/507f1f77bcf86cd799439011/panel_123.jpg",
                "file_name": "panel_123.jpg",
                "file_size": 524288,
                "file_type": "image/jpeg",
                "width": 1024,
                "height": 1536,
                "notes": "Opening splash panel",
                "created_at": "2026-11-25T10:00:00Z"
            }
        }
