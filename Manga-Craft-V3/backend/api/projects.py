"""
Projects API
Basic CRUD operations for projects
"""

from fastapi import APIRouter, HTTPException, Depends
from models import Project, User, Conversation, Message, ProjectMemory, Panel
from typing import List
from datetime import datetime
import logging
from auth.auth_utils import get_current_user

logger = logging.getLogger(__name__)

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
    """
    Delete a project with explicit cascade deletion of conversations and messages
    
    DELETE /projects/{id}
    """
    
    # Verify ownership
    project = await Project.get(project_id)
    if not project or project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    try:
        # Get all conversations for this project
        conversations = await Conversation.find({"project_id": project_id}).to_list()
        
        # Get all memories for this project
        memories = await ProjectMemory.find({"project_id": project_id}).to_list()
        
        total_messages_deleted = 0
        successful_conversation_ids = []
        failed_deletions = []
        
        # Delete each conversation and its messages
        for conv in conversations:
            try:
                msg_result = await Message.find_many({"conversation_id": str(conv.id)}).delete()
                total_messages_deleted += msg_result.deleted_count
                await conv.delete()
                successful_conversation_ids.append(str(conv.id))
            except Exception as e:
                # If any deletion fails, stop and preserve project
                failed_deletions.append({
                    "conversation_id": str(conv.id),
                    "error": str(e)
                })
        
        # Delete all memories
        for mem in memories:
            try:
                await mem.delete()
            except Exception as e:
                # Log memory deletion failure but don't block project deletion
                logger.warning(f"Failed to delete memory {mem.id}: {str(e)}")
        
        # Delete all panels
        panels = await Panel.find({"project_id": project_id}).to_list()
        for panel in panels:
            try:
                # Delete file from disk
                from pathlib import Path
                file_path = Path(panel.file_path)
                if file_path.exists():
                    try:
                        file_path.unlink()
                    except Exception as e:
                        logger.warning(f"Failed to delete panel file {file_path}: {str(e)}")
                # Delete database record
                await panel.delete()
            except Exception as e:
                # Log panel deletion failure but don't block project deletion
                logger.warning(f"Failed to delete panel {panel.id}: {str(e)}")
        
        # If any deletions failed, do NOT delete the project
        if failed_deletions:
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Failed to cleanup some conversations. Project preserved.",
                    "successful_conversation_ids": successful_conversation_ids,
                    "failed_deletions": failed_deletions,
                    "total_conversations": len(conversations),
                    "successful_count": len(successful_conversation_ids),
                    "failed_count": len(failed_deletions)
                }
            )
        
        # Only delete project if all cleanups succeeded
        await project.delete()
        
        return {
            "message": "Project deleted",
            "conversations_deleted": len(conversations),
            "messages_deleted": total_messages_deleted,
            "memories_deleted": len(memories),
            "panels_deleted": len(panels)
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions (including our custom error above)
        raise
    except Exception as e:
        # Unexpected error - preserve project
        logger.error(f"Failed to delete project {project_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete project: {str(e)}. Project preserved."
        )
