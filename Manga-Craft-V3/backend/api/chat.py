"""
Chat API
The AI chat endpoint: saves the user message, builds project context,
asks the AI for a reply, then saves and returns it.
"""

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import json
import logging

from models import Conversation, Message, User
from schemas.chat import ChatRequest, ChatResponse
from services.ai_service import generate_reply, stream_reply
from services.context_builder import build_project_context
from api.conversations import create_assistant_message_internal
from auth.auth_utils import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["chat"])

SYSTEM_PROMPT = (
    "You are MangaCraft, a helpful assistant for creating manga. "
    "Use the project context below to give specific, consistent advice. "
    "If the user asks about something not in the context, say so honestly."
)

# How many recent messages to include as "working memory".
# Older messages stay in the database but are left out of the prompt.
RECENT_MESSAGE_LIMIT = 20

@router.post("/", response_model=ChatResponse)
async def send_chat_message(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Send a message and receive an AI reply.

    POST /chat/
    Body: { "conversation_id": "...", "content": "..." }
    """
    conversation = await Conversation.get(payload.conversation_id)
    if not conversation or conversation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    # 1. Save the user's message
    user_message = Message(
        conversation_id=payload.conversation_id,
        role="user",
        content=payload.content.strip()
    )
    await user_message.insert()

    # 2. Build the project briefing (durable facts from Project Memory)
    context = await build_project_context(conversation.project_id)

    # 3. Load only the MOST RECENT messages as "working memory".
    #    Older messages stay in the DB but are kept out of the prompt so the
    #    context window does not fill up and dilute the important facts.
    recent = await Message.find(
        {"conversation_id": payload.conversation_id}
    ).sort("-created_at").limit(RECENT_MESSAGE_LIMIT).to_list()
    recent.reverse()  # query returned newest-first; flip to oldest-first

    ai_messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{context}"}]
    for message in recent:
        ai_messages.append({"role": message.role, "content": message.content})

    # 4. Ask the AI (tries each model until one responds)
    try:
        reply_text = await generate_reply(ai_messages)
    except Exception as error:
        logger.error("AI generation failed: %s", error)
        raise HTTPException(status_code=502, detail="The AI service is unavailable. Please try again.")

    # 5. Save the assistant's reply
    assistant_message = await create_assistant_message_internal(
        payload.conversation_id, reply_text
    )

    return ChatResponse(
        user_message_id=str(user_message.id),
        assistant_message_id=str(assistant_message.id),
        assistant_content=assistant_message.content
    )


def sse_event(data: dict) -> str:
    """Format one Server-Sent Event line (must end with a blank line)."""
    return f"data: {json.dumps(data)}\n\n"


async def stream_reply_events(conversation_id: str, user_message, ai_messages):
    """
    SSE generator: yields tokens as text, then saves the full reply at the end.
    """
    # Tell the browser the user message is saved so it can refresh the list.
    yield sse_event({"type": "start", "user_message_id": str(user_message.id)})

    collected = []
    try:
        async for token in stream_reply(ai_messages):
            collected.append(token)
            yield sse_event({"type": "token", "content": token})

        full_reply = "".join(collected).strip()
        assistant_message = await create_assistant_message_internal(
            conversation_id, full_reply
        )
        yield sse_event({
            "type": "done",
            "assistant_message_id": str(assistant_message.id),
        })
    except Exception as error:
        logger.error("AI streaming failed: %s", error)
        yield sse_event({
            "type": "error",
            "message": "The AI service is unavailable. Please try again.",
        })


@router.post("/stream")
async def stream_chat_message(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Stream an AI reply using Server-Sent Events.

    POST /chat/stream
    Body: { "conversation_id": "...", "content": "..." }
    """
    conversation = await Conversation.get(payload.conversation_id)
    if not conversation or conversation.user_id != str(current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to access this conversation")

    # 1. Save the user's message first (so it is not lost if streaming fails)
    user_message = Message(
        conversation_id=payload.conversation_id,
        role="user",
        content=payload.content.strip()
    )
    await user_message.insert()

    # 2. Build the project briefing and recent working memory
    context = await build_project_context(conversation.project_id)
    recent = await Message.find(
        {"conversation_id": payload.conversation_id}
    ).sort("-created_at").limit(RECENT_MESSAGE_LIMIT).to_list()
    recent.reverse()

    ai_messages = [{"role": "system", "content": f"{SYSTEM_PROMPT}\n\n{context}"}]
    for message in recent:
        ai_messages.append({"role": message.role, "content": message.content})

    return StreamingResponse(
        stream_reply_events(payload.conversation_id, user_message, ai_messages),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
