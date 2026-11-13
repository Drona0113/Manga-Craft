"""
Projects API
Basic CRUD operations for projects
"""

from fastapi import APIRouter, HTTPException
from models import Project
from typing import List
from datetime import datetime

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=Project)
async def create_project(project: Project):
    """Create a new project"""
    await project.insert()
    return project


@router.get("/", response_model=List[Project])
async def list_projects():
    """List all projects"""
    projects = await Project.find_all().to_list()
    return projects


@router.get("/{project_id}", response_model=Project)
async def get_project(project_id: str):
    """Get a specific project by ID"""
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=Project)
async def update_project(project_id: str, project_data: dict):
    """Update a project"""
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for field, value in project_data.items():
        if hasattr(project, field):
            setattr(project, field, value)
    
    project.updated_at = datetime.utcnow()
    await project.save()
    return project


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project"""
    project = await Project.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    await project.delete()
    return {"message": "Project deleted successfully"}
