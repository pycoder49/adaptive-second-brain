from sqlalchemy.orm import Session
from typing import List
import datetime
import logging

from database.db_access import chat_access
from database.db_access import document_access
from database import models
from core.entities import chat_entity
from core.RAG.main import query_rag


logger = logging.getLogger(__name__)


def create_chat(user_id: int, db: Session) -> dict:
    new_chat = chat_access.create_chat(user_id, db)

    return {
        "id": new_chat.id,
        "user_id": new_chat.user_id,
        "title": new_chat.title,
        "created_at": new_chat.created_at,
    }


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


def get_all_messages(chat_id: int, db: Session) -> List[dict]:
    logger.info("Fetching all messages for chat from the data access layer")
    messages: List[chat_entity.MessageRetrieve] = chat_access.get_messages_for_chat(chat_id, db)

    message_list: List[dict] = [
        {
            "id": message.id,
            "chat_id": message.chat_id,
            "role": message.role,
            "content": message.content,
            "parent_message_id": message.parent_message_id,
            "created_at": message.created_at,
        }
        for message in messages
    ]
    return message_list


def add_message_to_chat(chat_id: int, role: str, content: str, db: Session) -> dict:
    message = chat_access.create_message(chat_id, role, content, db)
    return {
        "id": message.id,
        "chat_id": message.chat_id,
        "role": message.role.value if hasattr(message.role, 'value') else message.role,
        "content": message.content,
        "parent_message_id": message.parent_message_id,
        "created_at": message.created_at,
    }


def send_message(chat_id: int, user_id: int, user_message: str, document_ids: List[int], db: Session) -> dict:
    logger.info(f"Processing message for chat {chat_id}")

    # Save user message
    add_message_to_chat(chat_id, "user", user_message, db)

    # Link documents to chat if provided
    if document_ids:
        chat_access.link_documents_to_chat(chat_id, document_ids, db)

    # Get all document IDs linked to this chat
    linked_doc_ids = chat_access.get_document_ids_for_chat(chat_id, db)

    if not linked_doc_ids:
        ai_response = "No documents are linked to this chat. Please upload and attach documents first."
    else:
        # Run RAG
        ai_response = query_rag(user_message, linked_doc_ids, db)

    # Save AI response
    ai_msg = add_message_to_chat(chat_id, "ai", ai_response, db)

    return ai_msg
