from fastapi import APIRouter, HTTPException, Depends, Body
from sqlalchemy.orm import Session
from typing import List
import logging

from ..schemas import chat_schemas
from core.services import chat_services

from database.database import get_db
from api.routes.auth import get_current_user


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chats"],
)


"""
Endpoints for chat management
"""


# get all chats for the current user
@router.get("/", response_model=List[chat_schemas.ChatResponse])
def get_chats(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info("Fetching all chats from the service layer")
    chats: List[dict] = chat_services.get_all_chats(user["id"], db)

    if not chats:
        logger.info("No conversations found, returning empty list")
        return []
    
    chats = [
        chat_schemas.ChatResponse(
            id=chat.get("id"),
            user_id=chat.get("user_id"),    
            title=chat.get("title"),
            created_at=chat.get("created_at"),
        )
        for chat in chats
    ]
    return chats


@router.post("/", response_model=chat_schemas.ChatCreate)
def create_chat(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info("Creating a new chat in the service layer")
    new_chat = chat_services.create_chat(user["id"], db)

    response = chat_schemas.ChatResponse(
        id = new_chat.get("id"),
        user_id = new_chat.get("user_id"),
        title = new_chat.get("title"),
        created_at = new_chat.get("created_at"),
    )
    return response


@router.get("/{chat_id}", response_model=chat_schemas.MessageResponse)
def get_all_messages_for_chat(
    chat_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all messages for a specific chat.

    :param chat_id: The ID of the chat whose messages are being retrieved
    :param user: The authenticated user object
    :param db: Database session dependency
    :return: List of messages in the chat
    """
    logger.info(f"Retrieving all messages for chat ID {chat_id} from the service layer")

    chat = chat_services.get_chat_by_id(chat_id, db)
    if not chat:
        logger.error(f"Chat with ID {chat_id} not found")
        raise HTTPException(status_code=404, detail="Chat not found")

    if chat.get("user_id") != user["id"]:
        logger.error(f"User {user['id']} is unauthorized to access chat {chat_id}")
        raise HTTPException(status_code=403, detail="Unauthorized access to chat")

    all_messages: List[dict] = chat_services.get_all_messages(chat_id, db)

    # construct and return the response object
    chat_response = chat_schemas.ChatResponse(
        id = chat.get("id"),
        user_id = chat.get("user_id"),
        title = chat.get("title"),
        created_at = chat.get("created_at"),
    )
    user_messages = [
        chat_schemas.Message(
            id = message.get("id"),
            role = message.get("role"),
            content = message.get("content"),
            created_at = message.get("created_at"),
        )
        for message in all_messages
    ]

    return chat_schemas.MessageResponse(
        chat = chat_response,
        messages = user_messages,
    )


@router.post("/{chat_id}/message")
def send_message(
    chat_id: int,
    message: chat_schemas.MessageCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Posts a new message to a specific chat and gets an AI response.

    :param chat_id: The ID of the chat to which the message is being posted
    :param message: The message content and optional document_ids
    :param user: The authenticated user object
    :param db: Database session dependency
    :return: The AI response message
    """
    chat = chat_services.get_chat_by_id(chat_id, db)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    if chat.get("user_id") != user["id"]:
        raise HTTPException(status_code=403, detail="Unauthorized access to chat")

    logger.info(f"User {user['id']} sending message to chat {chat_id}")

    ai_response = chat_services.send_message(
        chat_id=chat_id,
        user_id=user["id"],
        user_message=message.content,
        document_ids=message.document_ids,
        db=db,
    )

    return ai_response
