"""
Projects API
Basic CRUD operations for projects
"""

from fastapi import APIRouter, HTTPException, Depends
from models import Project, User, Conversation, Message
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
            "messages_deleted": total_messages_deleted
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
