"""
This module talks to the database models related to chat functionality
"""
from sqlalchemy.orm import Session
from typing import List
import logging

from database import models
from core.entities import chat_entity


logger = logging.getLogger(__name__)


def get_chats_for_user(user_id: int, db: Session) -> List[chat_entity.ChatRetrieve] | None:
    """
    Retrieves all conversations' metadata from the database, ordered by creation date descending.

    :param user_id: The ID of the user whose conversations are being retrieved
    :param db: Database session

    :return: List of ChatRetrieve entity objects
    """
    logger.info("Inside chat_access.get_chats_for_user()")

    all_chats = db.query(models.Chat)
    all_chats = all_chats.filter(models.Chat.user_id == user_id)
    all_chats = all_chats.order_by(models.Chat.created_at.desc()).all()

    if not chat_entities:
        logger.info("No chats found in the database")
        return None
                                             
    chat_entities: List[chat_entity.ChatRetrieve]
    chat_entities = [
        chat_entity.ChatRetrieve(
            id = chat.id,
            user_id = chat.user_id,
            title = chat.title,
            created_at = chat.created_at,
        )
        for chat in all_chats
    ]

    return chat_entities
    
