"""
MongoDB Database Configuration
Handles MongoDB connection and initialization
"""

from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: Optional[AsyncIOMotorClient] = None

    @classmethod
    async def connect(cls):
        """Connect to MongoDB"""
        if cls.client is None:
            mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
            cls.client = AsyncIOMotorClient(mongodb_url)
            print("Connected to MongoDB ✅")
            return cls.client

    @classmethod
    async def close(cls):
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            cls.client = None
            print("MongoDB connection closed")

    @classmethod
    async def init_models(cls, models):
        """Initialize Beanie models"""
        await init_beanie(database=cls.client.mangacraft, document_models=models)
        print("Beanie models initialized")
