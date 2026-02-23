from sqlalchemy.orm import Session
from typing import List
import logging

from database.db_access import chat_access
from core.entities import chat_entity
from core.entities.chat_entity import Role
from core.RAG.rag_factory import get_rag_engine


logger = logging.getLogger(__name__)


# add a single chat for the current user
def create_chat(user_id: int, db: Session) -> dict:
    """
    Creates a new chat for the given user in the database.

    :param user_id: The ID of the user for whom the chat is being created
    :param db: Database session

    :return: dict respresenting the created chat
    """
    new_chat = chat_access.create_chat(user_id, db)

    return {
        "id": new_chat.id,
        "user_id": new_chat.user_id,
        "title": new_chat.title,
        "created_at": new_chat.created_at,
    }


# get all chats for the current user
def get_all_chats(user_id: int, db: Session) -> List[dict] | None:
    logger.info("Fetching all chats from the data access layer")
    all_chats: List[chat_entity.ChatRetrieve] = chat_access.get_chats_for_user(user_id, db)

    if not all_chats:
        logger.info("No chats found, returning 'None'")
        return None

    # found chats, returning as list of general dict objects
    chat_list: List[dict] = [
        {
            "id": chat.id,
            "user_id": chat.user_id,
            "title": chat.title,
            "created_at": chat.created_at,
        }
        for chat in all_chats
    ]
    return chat_list


# get a single chat by ID
def get_chat_by_id(chat_id: int, db: Session) -> dict | None:
    logger.info("Fetching chat by ID from the data access layer")
    chat: chat_entity.ChatRetrieve = chat_access.get_chat_data(chat_id, db)
    if not chat:
        return None

    return {
        "id": chat.id,
        "user_id": chat.user_id,
        "title": chat.title,
        "created_at": chat.created_at,
    }


# get all messages for a chat
def get_all_messages(chat_id: int, db: Session) -> List[dict]:
    logger.info("Fetching all messages for chat from the data access layer")
    messages: List[chat_entity.MessageRetrieve] = chat_access.get_messages_for_chat(chat_id, db)

    message_list: List[dict] = [
        {
            "id": message.id,
            "chat_id": message.chat_id,
            "role": message.role,
            "content": message.content,
            "created_at": message.created_at,
        }
        for message in messages
    ]
    return message_list


# get all messages for a chat
def post_message_to_chat(chat_id: int, user_id: int, content: str, db: Session) -> tuple[dict, dict]:
    logger.info("Posting message to chat via the data access layer")
    new_message: chat_entity.MessageRetrieve = chat_access.post_message_to_chat(
        chat_id = chat_id,
        role = Role.USER,
        content = content,
        db = db,
    )

    # sending message to the rag inference engine via the service layer
    rag_engine = get_rag_engine()
    rag_response: str = rag_engine.get_response(user_id=user_id, query=content)

    assistant_response = chat_access.post_message_to_chat(
        chat_id = chat_id,
        role = Role.AI,
        content = rag_response,
        db = db,
    )
    
    return {
        "id": new_message.id,
        "chat_id": new_message.chat_id,
        "role": new_message.role,
        "content": new_message.content,
        "created_at": new_message.created_at,
    }, {
        "id": assistant_response.id,
        "chat_id": assistant_response.chat_id,
        "role": assistant_response.role,
        "content": assistant_response.content,
        "created_at": assistant_response.created_at,
    }

