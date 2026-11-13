"""
User Model
Represents a user in the system
"""

from beanie import Document, Indexed
from datetime import datetime
from typing import Optional
from pydantic import EmailStr, Field


class User(Document):
    """User document for MongoDB"""
    
    username: str = Indexed(unique=True)
    email: EmailStr = Indexed(unique=True)
    hashed_password: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        name = "users"
        indexes = [
            "username",
            "email"
        ]
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "email": "john@example.com",
                "hashed_password": "hashed_password_here",
                "full_name": "John Doe",
                "is_active": True
            }
        }
