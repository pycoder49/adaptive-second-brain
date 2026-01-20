from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session
from typing import List
import logging

from ..schemas import chat_schemas
from database.database import get_db

from core.services import chat_service

from core.services.errors.chat_errors import (
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Chat"],
)


"""
Need methods for:
- Getting all conversations
- Getting all messages in a conversation
- Getting a single conversation by ID

- Creating a new conversation
- Adding a message to a conversation
"""

@router.get("/conversations")
def get_conversations(db: Session = Depends(get_db)) -> List[chat_schemas.Conversation]:
    """
    Retrieves all conversations for the authenticated user

    :param db: Database session dependency

    :return: List of conversations
    """
    logger.info(f"Inside get_conversations endpoint")

    conversations = chat_service.get_all_conversations(db)
    return conversations

