"""
Conversation API Endpoints
Handles conversation and message CRUD operations
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from datetime import datetime
import logging
from models import Project, Conversation, Message, User
from schemas.conversation import (
    ConversationCreate,
    ConversationUpdate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    MessagesListResponse
)
from auth.auth_utils import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("/", response_model=ConversationResponse, status_code=201)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a new conversation
    
    POST /conversations
    Body: { "project_id": "...", "title": "..." }
    """
    
    # Verify project ownership
    project = await Project.get(conversation_data.project_id)
    if not project or project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Create conversation
    new_conversation = Conversation(
        project_id=conversation_data.project_id,
        user_id=str(current_user.id),
        title=conversation_data.title
    )
    
    await new_conversation.insert()
    
    return ConversationResponse(
        id=str(new_conversation.id),
        project_id=new_conversation.project_id,
        user_id=new_conversation.user_id,
        title=new_conversation.title,
        created_at=new_conversation.created_at.isoformat(),
        updated_at=new_conversation.updated_at.isoformat()
    )


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    project_id: str = Query(...),
    current_user: User = Depends(get_current_user)
):
    """
    List all conversations for a project
    
    GET /conversations?project_id={id}
    """
    
    # Verify project ownership
    project = await Project.get(project_id)
    if not project or project.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this project")
    
    # Get conversations sorted by updated_at DESC (most recent first)
    conversations = await Conversation.find(
        {"project_id": project_id, "user_id": str(current_user.id)}
    ).sort("-updated_at").to_list()
    
    return [
        ConversationResponse(
            id=str(conv.id),
            project_id=conv.project_id,
            user_id=conv.user_id,
            title=conv.title,
            created_at=conv.created_at.isoformat(),
            updated_at=conv.updated_at.isoformat()
        )
        for conv in conversations
    ]


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get a specific conversation
    
    GET /conversations/{id}
    """
    
    conversation = await Conversation.get(conversation_id)
    if not conversation or conversation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    return ConversationResponse(
        id=str(conversation.id),
        project_id=conversation.project_id,
        user_id=conversation.user_id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat()
    )


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: str,
    conversation_data: ConversationUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Rename a conversation
    
    PUT /conversations/{id}
    Body: { "title": "..." }
    """
    
    conversation = await Conversation.get(conversation_id)
    if not conversation or conversation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    conversation.title = conversation_data.title
    conversation.updated_at = datetime.utcnow()
    await conversation.save()
    
    return ConversationResponse(
        id=str(conversation.id),
        project_id=conversation.project_id,
        user_id=conversation.user_id,
        title=conversation.title,
        created_at=conversation.created_at.isoformat(),
        updated_at=conversation.updated_at.isoformat()
    )


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Delete a conversation with explicit message cascade
    
    DELETE /conversations/{id}
    """
    
    # Verify ownership
    conversation = await Conversation.get(conversation_id)
    if not conversation or conversation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    messages_deleted = 0
    conversation_deleted = False
    
    try:
        # Step 1: Delete all messages
        delete_result = await Message.find_many({"conversation_id": conversation_id}).delete()
        messages_deleted = delete_result.deleted_count
        
        # Step 2: Delete conversation
        await conversation.delete()
        conversation_deleted = True
        
        return {
            "message": "Conversation deleted",
            "messages_deleted": messages_deleted,
            "conversation_deleted": True
        }
        
    except Exception as e:
        # Log the exception
        logger.error(f"Failed to delete conversation {conversation_id}: {str(e)}")
        
        # Report partial state accurately
        if not conversation_deleted and messages_deleted > 0:
            # Messages deleted but conversation preserved
            raise HTTPException(
                status_code=500,
                detail={
                    "message": "Conversation document preserved after message deletion failure",
                    "messages_deleted": messages_deleted,
                    "conversation_deleted": False,
                    "conversation_id": conversation_id,
                    "error": str(e)
                }
            )
        else:
            # General failure (no messages deleted or conversation preserved with no deletion)
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete conversation: {str(e)}. Conversation preserved."
            )


@router.get("/{conversation_id}/messages", response_model=MessagesListResponse)
async def get_messages(
    conversation_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """
    Get messages for a conversation with offset-based pagination
    
    GET /conversations/{id}/messages?skip=0&limit=50
    """
    
    # Verify ownership
    conversation = await Conversation.get(conversation_id)
    if not conversation or conversation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Paginated retrieval (offset-based) - chronological order (oldest first)
    messages = await Message.find(
        {"conversation_id": conversation_id}
    ).sort("created_at").skip(skip).limit(limit).to_list()
    
    # Get total count
    total = await Message.find({"conversation_id": conversation_id}).count()
    
    return MessagesListResponse(
        messages=[
            MessageResponse(
                id=str(msg.id),
                conversation_id=msg.conversation_id,
                role=msg.role,
                content=msg.content,
                created_at=msg.created_at.isoformat()
            )
            for msg in messages
        ],
        total=total,
        skip=skip,
        limit=limit,
        has_more=skip + limit < total
    )


@router.post("/messages", response_model=MessageResponse, status_code=201)
async def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """
    Create a user message (assistant messages created by AI service in V3.11)
    
    POST /messages
    Body: { "conversation_id": "...", "role": "user", "content": "..." }
    """
    
    # Verify conversation ownership
    conversation = await Conversation.get(message_data.conversation_id)
    if not conversation or conversation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")
    
    # Create message
    new_message = Message(
        conversation_id=message_data.conversation_id,
        role=message_data.role,
        content=message_data.content
    )
    
    await new_message.insert()
    
    # Update conversation.updated_at
    conversation.updated_at = datetime.utcnow()
    await conversation.save()
    
    return MessageResponse(
        id=str(new_message.id),
        conversation_id=new_message.conversation_id,
        role=new_message.role,
        content=new_message.content,
        created_at=new_message.created_at.isoformat()
    )


async def create_assistant_message_internal(conversation_id: str, content: str):
    """
    Internal function to create assistant messages (for V3.11 AI service)
    NOT exposed as a public API endpoint
    """
    conversation = await Conversation.get(conversation_id)
    if not conversation:
        raise ValueError("Conversation not found")
    
    new_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=content.strip()
    )
    await new_message.insert()
    
    conversation.updated_at = datetime.utcnow()
    await conversation.save()
    
    return new_message
