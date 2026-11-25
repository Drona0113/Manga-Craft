"""
MangaCraft V3 - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from config.database import Database
from models import User, Project, Conversation, Message, ProjectMemory, Panel
from api import projects_router
from api.auth import router as auth_router
from api.conversations import router as conversations_router
from api.memories import router as memories_router
from api.panels import router as panels_router
from api.chat import router as chat_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    await Database.connect()
    await Database.init_models([User, Project, Conversation, Message, ProjectMemory, Panel])
    yield
    # Shutdown
    await Database.close()

app = FastAPI(
    title="MangaCraft V3 API",
    description="AI-powered manga creation workspace",
    version="3.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(projects_router)
app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(memories_router)
app.include_router(panels_router)
app.include_router(chat_router)

# Static file serving for panel images
app.mount("/panels", StaticFiles(directory="panels"), name="panels")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MangaCraft V3 API",
        "version": "3.0.0",
        "status": "development",
        "database": "MongoDB"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "database": "connected" if Database.client else "disconnected"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
