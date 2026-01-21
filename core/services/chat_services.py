from sqlalchemy.orm import Session
from typing import List
import datetime
import logging

from api.schemas import chat_schemas
from database.db_access import chat_access
from core.entities import chat_entity


logger = logging.getLogger(__name__)


def get_all_chats(user_id: int, db: Session) -> List[chat_schemas.ChatResponse] | None:
    logger.info("Inside chat_service.get_all_chats()")

    logger.info("Fetching all chats from the data access layer")
    all_chats: List[chat_entity.ChatRetrieve] = chat_access.get_chats_for_user(user_id, db)

    if not all_chats:
        logger.info("No chats found, returning 'None'")
        return None

    chat_response_list: List[chat_schemas.ChatResponse] = [
        chat_schemas.ChatResponse(
            id = chat.id,
            user_id = chat.user_id,
            title = chat.title,
            created_at = chat.created_at,
        )
        for chat in all_chats
    ]
    return chat_response_list


def get_all_messages(db: Session, chat_id: int):
    pass


def get_chat_by_id(db: Session, chat_id: int):
    pass


def create_chat(db: Session, user_id: int, title: str) -> chat_schemas.Chat:
    pass


def add_message_to_chat(db: Session, chat_id, role: str, content: str):
    pass
