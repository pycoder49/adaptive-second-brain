"""
This module talks to the database models related to chat functionality
"""
from sqlalchemy.orm import Session
from typing import List
import logging

from database import models
from core.entities import chat_entity


logger = logging.getLogger(__name__)


"""
Methods for accessing chat-related data in the database
"""

def get_chats_for_user(user_id: int, db: Session) -> List[chat_entity.ChatRetrieve] | None:
    """
    Retrieves all conversations' metadata from the database, ordered by creation date descending.

    :param user_id: The ID of the user whose conversations are being retrieved
    :param db: Database session

    :return: List of ChatRetrieve entity objects
    """
    logger.info(f"Querying to db for all chats for user_id: {user_id}")
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


def get_chat_data(chat_id: int, db: Session) -> chat_entity.ChatRetrieve | None:
    """
    Retrieves a single chat's metadata from the database by chat ID

    :param chat_id: The ID of the chat being retrieved
    :param db: Database session

    :return: ChatRetrieve entity object if found, else None
    """
    logger.info(f"Querying to db for chat with id: {chat_id}")
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    if not chat:
        return None
    
    chat_entity_obj = chat_entity.ChatRetrieve(
        id = chat.id,
        user_id = chat.user_id,
        title = chat.title,
        created_at = chat.created_at,
    )
    return chat_entity_obj


def create_chat(user_id: int, db: Session) -> chat_entity.ChatRetrieve:
    """
    Creates a new chat entry in the database for the given user

    :param user_id: The ID of the user for whom the chat is being created
    :param db: Database session
    :return: ChatRetrieve entity representing the created chat
    """
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


"""
Methods for accessing message-related data in the database
"""

def get_messages_for_chat(chat_id: int, db: Session) -> List[chat_entity.MessageRetrieve]:
    """
    Gets all messages for a specific chat from the database

    :param chat_id: The ID of the chat whose messages are being retrieved
    :param db: Database session

    :return: List of MessageRetrieve entity objects
    """
    logger.info(f"Querying to db for all messages for chat_id: {chat_id}")

    messages = db.query(models.Message).filter(models.Message.chat_id == chat_id)
    messages = messages.order_by(models.Message.created_at.asc()).all()

    # convert the list of messages to the internal data types
    all_messages: List[chat_entity.MessageRetrieve] = [
        chat_entity.MessageRetrieve(
            id = message.id,
            chat_id = message.chat_id,
            role = message.role,
            content = message.content,
            created_at = message.created_at,
        )
        for message in messages
    ]
    return all_messages


def post_message_to_chat(chat_id: int, role: str, content: str, db: Session) -> chat_entity.MessageRetrieve:
    """
    Posts a new message to a specific chat in the database
    
    :param chat_id: The ID of the chat to which the message is being posted
    :param role: The role of the message sender (e.g., "user", "assistant")
    :param content: The content of the message being posted
    :param db: Database session

    :return: MessageRetrieve entity representing the newly posted message
    """
    logger.info("Creating new message entry in the database")
    message_entry = models.Message(
        chat_id = chat_id,
        role = role,
        content = content,
    )

    db.add(message_entry)
    db.commit()
    db.refresh(message_entry)

    new_message = chat_entity.MessageRetrieve(
        id = message_entry.id,
        chat_id = message_entry.chat_id,
        role = message_entry.role,
        content = message_entry.content,
        created_at = message_entry.created_at,
    )
    return new_message
