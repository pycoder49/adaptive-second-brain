from sqlalchemy.orm import Session
from typing import List
import datetime
import logging

from database.db_access import chat_access
from core.entities import chat_entity


logger = logging.getLogger(__name__)


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
    }


def get_all_chats(user_id: int, db: Session) -> List[dict] | None:
    logger.info("Inside chat_service.get_all_chats()")

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


def get_all_messages(db: Session, chat_id: int):
    pass


def get_chat_by_id(db: Session, chat_id: int):
    pass


def add_message_to_chat(db: Session, chat_id, role: str, content: str):
    pass
