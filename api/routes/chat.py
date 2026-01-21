from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session
from typing import List
import logging

from ..schemas import chat_schemas
from database.database import get_db

from core.services import chat_service


logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Chat"],
)


"""
Need methods for:
- Getting all chats
- Getting all messages in a chat
- Getting a single chat by ID

- Creating a new chat
- Adding a message to a chat
"""

@router.get("/chats/{user_id}")
def get_chats(user_id: int, db: Session = Depends(get_db)) -> List[chat_schemas.ChatResponse]:
    """
    Retrieves all conversations for the authenticated user

    :param user_id: The ID of the user whose conversations are being retrieved
    :param db: Database session dependency

    :return: List of chat meta data
    """
    logger.info(f"Inside get_chats endpoint")

    logger.info("Fetching all chats from the service layer")
    chats: List[chat_schemas.ChatResponse] = chat_service.get_all_chats(user_id, db)

    if not chats:
        logger.info("No conversations found, returning empty list")
        return []
    
    return chats