"""
Projects API
Basic CRUD operations for projects
"""

from fastapi import APIRouter, HTTPException, Depends
from models import Project, User
from typing import List
from datetime import datetime
from auth.auth_utils import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project)
async def create_project(project: Project, current_user: User = Depends(get_current_user)):
    """Create a new project (requires authentication)"""
    project.user_id = str(current_user.id)
    await project.insert()
    return project


@router.get("/", response_model=List[Project])
async def list_projects(current_user: User = Depends(get_current_user)):
    """List all projects for the current user"""
    projects = await Project.find({"user_id": str(current_user.id)}).to_list()
    return projects


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Get a specific project by ID (requires authentication)"""
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project_data: dict, current_user: User = Depends(get_current_user)):
    """Update a project (requires authentication)"""
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    for field, value in project_data.items():
        if hasattr(project, field):
            setattr(project, field, value)
    
    project.updated_at = datetime.utcnow()
    await project.save()
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: str, current_user: User = Depends(get_current_user)):
    """Delete a project (requires authentication)"""
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    await project.delete()
    return {"message": "Project deleted successfully"}
