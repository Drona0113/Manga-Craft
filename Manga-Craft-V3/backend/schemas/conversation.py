"""
Conversation Schemas
Pydantic models for conversation and message requests and responses
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List


class ConversationCreate(BaseModel):
    """Schema for creating a conversation"""
    project_id: str
    title: str = Field(..., min_length=1, max_length=200)


class ConversationUpdate(BaseModel):
    """Schema for updating a conversation"""
    title: str = Field(..., min_length=1, max_length=200)


class ConversationResponse(BaseModel):
    """Schema for conversation response"""
    id: str
    project_id: str
    user_id: str
    title: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


class MessageCreate(BaseModel):
    """Schema for creating a message"""
    conversation_id: str
    role: str = Field(..., pattern="^(user)$")  # Only user messages in V3.8
    content: str = Field(..., min_length=1)
    
    @field_validator('content')
    @classmethod
    def content_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty or whitespace-only')
        return v.strip()


class MessageResponse(BaseModel):
    """Schema for message response"""
    id: str
    conversation_id: str
    role: str
    content: str
    created_at: str
    
    class Config:
        from_attributes = True


class MessagesListResponse(BaseModel):
    """Schema for paginated messages response"""
    messages: List[MessageResponse]
    total: int
    skip: int
    limit: int
    has_more: bool
