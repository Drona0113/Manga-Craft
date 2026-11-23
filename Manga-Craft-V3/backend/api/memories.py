"""
Memory API Endpoints
Handles memory CRUD operations and search
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime
import logging
from models import Project, ProjectMemory, User
from schemas.memory import (
    MemoryCreate,
    MemoryUpdate,
    MemoryResponse,
    MemoryListResponse
)
from auth.auth_utils import get_current_user

router = APIRouter(prefix="/memories", tags=["memories"])
logger = logging.getLogger(__name__)


@router.post("/", response_model=MemoryResponse, status_code=201)
async def create_memory(
    memory_data: MemoryCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new memory
    
    POST /memories/
    Body: { "project_id": "...", "type": "character", "title": "...", "content": "...", "tags": [...] }
    """
    
    # Verify project ownership
    project = await Project.get(memory_data.project_id)
    if not project or project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Create memory
    new_memory = ProjectMemory(
        project_id=memory_data.project_id,
        user_id=str(current_user.id),
        type=memory_data.type,
        title=memory_data.title,
        content=memory_data.content,
        tags=memory_data.tags
    )
    
    await new_memory.insert()
    
    return MemoryResponse(
        id=str(new_memory.id),
        project_id=new_memory.project_id,
        user_id=new_memory.user_id,
        type=new_memory.type,
        title=new_memory.title,
        content=new_memory.content,
        tags=new_memory.tags,
        created_at=new_memory.created_at.isoformat(),
        updated_at=new_memory.updated_at.isoformat()
    )


@router.get("/", response_model=MemoryListResponse)
async def list_memories(
    project_id: str,
    memory_type: str | None = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    List memories for a project with optional type filter
    
    GET /memories/?project_id=...&type=character&skip=0&limit=50
    """
    
    # Verify project ownership
    project = await Project.get(project_id)
    if not project or project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Build query
    query = {"project_id": project_id}
    if memory_type:
        query["type"] = memory_type
    
    # Fetch memories with pagination
    memories = await ProjectMemory.find(query).sort("-updated_at").skip(skip).limit(limit).to_list()
    
    # Get total count
    total = await ProjectMemory.find(query).count()
    
    return MemoryListResponse(
        memories=[
            MemoryResponse(
                id=str(mem.id),
                project_id=mem.project_id,
                user_id=mem.user_id,
                type=mem.type,
                title=mem.title,
                content=mem.content,
                tags=mem.tags,
                created_at=mem.created_at.isoformat(),
                updated_at=mem.updated_at.isoformat()
            )
            for mem in memories
        ],
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )


@router.get("/{memory_id}", response_model=MemoryResponse)
async def get_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific memory
    
    GET /memories/{id}
    """
    
    memory = await ProjectMemory.get(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # Verify ownership
    if memory.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this memory")
    
    return MemoryResponse(
        id=str(memory.id),
        project_id=memory.project_id,
        user_id=memory.user_id,
        type=memory.type,
        title=memory.title,
        content=memory.content,
        tags=memory.tags,
        created_at=memory.created_at.isoformat(),
        updated_at=memory.updated_at.isoformat()
    )


@router.put("/{memory_id}", response_model=MemoryResponse)
async def update_memory(
    memory_id: str,
    memory_data: MemoryUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Update a memory
    
    PUT /memories/{id}
    Body: { "type": "...", "title": "...", "content": "...", "tags": [...] }
    """
    
    memory = await ProjectMemory.get(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # Verify ownership
    if memory.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this memory")
    
    # Update fields
    if memory_data.type is not None:
        memory.type = memory_data.type
    if memory_data.title is not None:
        memory.title = memory_data.title
    if memory_data.content is not None:
        memory.content = memory_data.content
    if memory_data.tags is not None:
        memory.tags = memory_data.tags
    
    memory.updated_at = datetime.utcnow()
    await memory.save()
    
    return MemoryResponse(
        id=str(memory.id),
        project_id=memory.project_id,
        user_id=memory.user_id,
        type=memory.type,
        title=memory.title,
        content=memory.content,
        tags=memory.tags,
        created_at=memory.created_at.isoformat(),
        updated_at=memory.updated_at.isoformat()
    )


@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a memory
    
    DELETE /memories/{id}
    """
    
    memory = await ProjectMemory.get(memory_id)
    if not memory:
        raise HTTPException(status_code=404, detail="Memory not found")
    
    # Verify ownership
    if memory.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this memory")
    
    await memory.delete()
    
    return {"message": "Memory deleted"}


@router.get("/search/", response_model=MemoryListResponse)
async def search_memories(
    project_id: str = Query(...),
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    Search memories by title, content, or tags
    
    GET /memories/search/?project_id=...&query=...&skip=0&limit=50
    """
    
    # Verify project ownership
    project = await Project.get(project_id)
    if not project or project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Build search query (case-insensitive)
    search_query = {
        "project_id": project_id,
        "$or": [
            {"title": {"$regex": query, "$options": "i"}},
            {"content": {"$regex": query, "$options": "i"}},
            {"tags": {"$regex": query, "$options": "i"}}
        ]
    }
    
    # Fetch memories with pagination
    memories = await ProjectMemory.find(search_query).sort("-updated_at").skip(skip).limit(limit).to_list()
    
    # Get total count
    total = await ProjectMemory.find(search_query).count()
    
    return MemoryListResponse(
        memories=[
            MemoryResponse(
                id=str(mem.id),
                project_id=mem.project_id,
                user_id=mem.user_id,
                type=mem.type,
                title=mem.title,
                content=mem.content,
                tags=mem.tags,
                created_at=mem.created_at.isoformat(),
                updated_at=mem.updated_at.isoformat()
            )
            for mem in memories
        ],
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )
