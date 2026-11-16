"""
Authentication Schemas
Pydantic models for authentication requests and responses
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserRegister(BaseModel):
    """Schema for user registration"""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    username: str


class UserResponse(BaseModel):
    """Schema for user response (without password)"""
    id: str
    username: str
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: str
    
    class Config:
        from_attributes = True
