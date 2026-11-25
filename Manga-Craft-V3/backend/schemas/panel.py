"""
Panel Schemas
Request and response models for panel operations
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class PanelCreate(BaseModel):
    """Schema for creating a new panel (after file upload)"""
    project_id: str
    file_path: str
    file_name: str
    file_size: int = Field(..., gt=0, description="File size in bytes")
    file_type: str = Field(..., description="MIME type (image/jpeg, image/png, etc.)")


class PanelResponse(BaseModel):
    """Schema for panel response"""
    id: str
    project_id: str
    user_id: str
    file_path: str
    file_name: str
    file_size: int
    file_type: str
    width: Optional[int] = None
    height: Optional[int] = None
    notes: Optional[str] = None
    created_at: str


class PanelListResponse(BaseModel):
    """Schema for panel list response"""
    panels: List[PanelResponse]
    total: int
    skip: int
    limit: int
    has_more: bool


class PanelUpdate(BaseModel):
    """Schema for updating editable panel fields"""
    notes: Optional[str] = None
