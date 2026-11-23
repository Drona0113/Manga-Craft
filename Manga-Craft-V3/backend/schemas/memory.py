"""
Memory Schemas
Request and response models for memory operations
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime

# Valid memory types (from V2 + V3 additions)
MEMORY_TYPES = [
    "character",
    "story",
    "relationship",
    "design_decision",
    "art_style",
    "preference",
    "panel",
    "generated_reference",
    "character_reference",
    "other_asset",
    "location",  # V3 addition
    "note",  # V3 addition
]


class MemoryCreate(BaseModel):
    """Schema for creating a new memory"""
    project_id: str
    type: str = Field(..., description=f"Memory type: {', '.join(MEMORY_TYPES)}")
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: List[str] = Field(default_factory=list, max_length=20)


class MemoryUpdate(BaseModel):
    """Schema for updating a memory"""
    type: Optional[str] = None
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = Field(None, max_length=20)


class MemoryResponse(BaseModel):
    """Schema for memory response"""
    id: str
    project_id: str
    user_id: str
    type: str
    title: str
    content: str
    tags: List[str]
    created_at: str
    updated_at: str


class MemoryListResponse(BaseModel):
    """Schema for memory list response"""
    memories: List[MemoryResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
