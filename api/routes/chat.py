from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session
from typing import List, Union
import logging

from ..schemas import chat_schemas, auth_schemas
from database.database import get_db

from core.services import chat_services
from api.routes.auth import get_current_user


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chats"],
)


"""
Need methods for:
- Getting all chats
- Getting all messages in a chat
- Getting a single chat by ID

- Creating a new chat
- Adding a message to a chat
"""


@router.get("/", response_model=List[chat_schemas.ChatResponse])
def get_chats(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieves all conversations for the authenticated user

    :param user: The authenticated user object
    :param db: Database session dependency

    :return: List of chat meta data
    """
    logger.info(f"Inside get_chats endpoint")

    logger.info("Fetching all chats from the service layer")
    chats: List[dict] = chat_services.get_all_chats(user["id"], db)

    if not chats:
        logger.info("No conversations found, returning empty list")
        return []
    
    # convert list of dict to list of ChatResponse schemas
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


# creates a new chat
@router.post("/", response_model=chat_schemas.ChatResponse)
def create_chat(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Creates a new conversation for the authenticated user

    :param user: The authenticated user object
    :param db: Database session dependency

    :return: The created chat object
    """
    logger.info(f"Inside create_chat endpoint")

    logger.info("Creating a new chat in the service layer")
    new_chat = chat_services.create_chat(user["id"], db)
    # object containing the meta data of the newly created chat

    return chat_schemas.ChatResponse(
        id = new_chat.get("id"),
        user_id = new_chat.get("user_id"),
        title = new_chat.get("title"),
    )
