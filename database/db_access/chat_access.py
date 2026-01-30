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

    if not all_chats:
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

def create_chat(user_id: int, db: Session) -> chat_entity.ChatRetrieve:
    """
    Creates a new chat entry in the database for the given user

    :param user_id: The ID of the user for whom the chat is being created
    :param db: Database session
    :return: ChatRetrieve entity representing the created chat
    """
    logger.info("Inside chat_access.create_chat()")

    # create a new chat entry
    new_chat = models.Chat(
        user_id = user_id,
        title = "New Chat",
    )

    # add and commit to the database
    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    # convert and return as ChatRetrieve entity
    created_chat = chat_entity.ChatRetrieve(
        id = new_chat.id,
        user_id = new_chat.user_id,
        title = new_chat.title,
        created_at = new_chat.created_at,
    )
    return created_chat
