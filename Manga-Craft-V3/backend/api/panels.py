"""
Panel API Endpoints
Handles panel upload, listing, and deletion
"""

from fastapi import APIRouter, HTTPException, Depends, Query, UploadFile, File
from typing import List, Optional
from datetime import datetime
import os
import io
import logging
from pathlib import Path
from PIL import Image
from models import Project, Panel, User
from schemas.panel import (
    PanelCreate,
    PanelResponse,
    PanelListResponse,
    PanelUpdate
)
from auth.auth_utils import get_current_user

router = APIRouter(tags=["panels"])
logger = logging.getLogger(__name__)

# File upload constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_DIMENSION = 8000  # Max width/height in pixels
ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"]
PANELS_DIR = Path("panels")

# Ensure panels directory exists
PANELS_DIR.mkdir(exist_ok=True)


def to_panel_response(panel: Panel) -> PanelResponse:
    """Convert a Panel document into an API response"""
    return PanelResponse(
        id=str(panel.id),
        project_id=panel.project_id,
        user_id=panel.user_id,
        file_path=panel.file_path,
        file_name=panel.file_name,
        file_size=panel.file_size,
        file_type=panel.file_type,
        width=panel.width,
        height=panel.height,
        notes=panel.notes,
        created_at=panel.created_at.isoformat()
    )


@router.post("/projects/{project_id}/panels/upload", response_model=PanelResponse, status_code=201)
async def upload_panel(
    project_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload a panel image for a project
    
    POST /projects/{project_id}/panels/upload
    Body: multipart/form-data with file
    """
    
    # Verify project ownership
    project = await Project.get(project_id)
    if not project or project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Validate file type
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_TYPES)}"
        )
    
    # Read file content
    content = await file.read()
    
    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )
    
    # Validate image dimensions
    try:
        with Image.open(io.BytesIO(content)) as img:
            width, height = img.size
    except Exception:
        raise HTTPException(status_code=400, detail="Unable to read image file")
    
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise HTTPException(
            status_code=400,
            detail=f"Image too large. Maximum dimension: {MAX_DIMENSION}px"
        )
    
    # Create project directory
    project_dir = PANELS_DIR / project_id
    project_dir.mkdir(exist_ok=True)
    
    # Generate unique filename
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(file.filename).suffix or ".jpg"
    unique_filename = f"panel_{timestamp}{file_extension}"
    file_path = project_dir / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Store relative path in database
    relative_path = f"panels/{project_id}/{unique_filename}"
    
    # Create panel record
    new_panel = Panel(
        project_id=project_id,
        user_id=str(current_user.id),
        file_path=relative_path,
        file_name=file.filename,
        file_size=len(content),
        file_type=file.content_type,
        width=width,
        height=height
    )
    
    await new_panel.insert()
    
    return to_panel_response(new_panel)


@router.get("/projects/{project_id}/panels", response_model=PanelListResponse)
async def list_panels(
    project_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    List panels for a project with pagination
    
    GET /projects/{project_id}/panels?skip=0&limit=50
    """
    
    # Verify project ownership
    project = await Project.get(project_id)
    if not project or project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Build query
    query = {"project_id": project_id}
    
    # Fetch panels with pagination
    panels = await Panel.find(query).sort("-created_at").skip(skip).limit(limit).to_list()
    
    # Get total count
    total = await Panel.find(query).count()
    
    return PanelListResponse(
        panels=[to_panel_response(panel) for panel in panels],
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )


@router.get("/panels/{panel_id}", response_model=PanelResponse)
async def get_panel(
    panel_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a single panel by ID"""
    panel = await Panel.get(panel_id)
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    if panel.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this panel")
    return to_panel_response(panel)


@router.patch("/panels/{panel_id}", response_model=PanelResponse)
async def update_panel(
    panel_id: str,
    payload: PanelUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update editable panel fields (currently notes)"""
    panel = await Panel.get(panel_id)
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    if panel.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to update this panel")
    if payload.notes is not None:
        panel.notes = payload.notes
    await panel.save()
    return to_panel_response(panel)


@router.delete("/panels/{panel_id}")
async def delete_panel(
    panel_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a panel and its file
    
    DELETE /panels/{id}
    """
    
    panel = await Panel.get(panel_id)
    if not panel:
        raise HTTPException(status_code=404, detail="Panel not found")
    
    # Verify ownership
    if panel.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to delete this panel")
    
    # Delete file from disk
    file_path = Path(panel.file_path)
    if file_path.exists():
        try:
            file_path.unlink()
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}")
    
    # Delete database record
    await panel.delete()
    
    return {"message": "Panel deleted"}
