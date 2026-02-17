
from sqlalchemy.orm import Session
from typing import List
import logging

from database import models
from core.entities import chat_entity


logger = logging.getLogger(__name__)




def get_chats_for_user(user_id: int, db: Session) -> List[chat_entity.ChatRetrieve] | None:

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
    new_chat = models.Chat(
        user_id = user_id,
        title = "New Chat",
    )

    db.add(new_chat)
    db.commit()
    db.refresh(new_chat)

    created_chat = chat_entity.ChatRetrieve(
        id = new_chat.id,
        user_id = new_chat.user_id,
        title = new_chat.title,
        created_at = new_chat.created_at,
    )
    return created_chat




def get_messages_for_chat(chat_id: int, db: Session) -> List[chat_entity.MessageRetrieve]:
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
            parent_message_id = message.parent_message_id,
            created_at = message.created_at,
        )
        for message in messages
    ]
    return all_messages


def create_message(chat_id: int, role: str, content: str, db: Session) -> models.Message:
    logger.info(f"Creating {role} message in chat {chat_id}")
    role_enum = models.Role.USER if role == "user" else models.Role.AI
    new_message = models.Message(
        chat_id=chat_id,
        role=role_enum,
        content=content,
    )
    db.add(new_message)
    db.commit()
    db.refresh(new_message)
    return new_message


def link_documents_to_chat(chat_id: int, document_ids: list, db: Session) -> None:
    logger.info(f"Linking documents {document_ids} to chat {chat_id}")
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    if not chat:
        return

    existing_doc_ids = {doc.id for doc in chat.documents}
    for doc_id in document_ids:
        if doc_id not in existing_doc_ids:
            doc = db.query(models.Document).filter(models.Document.id == doc_id).first()
            if doc:
                chat.documents.append(doc)

    db.commit()


def get_document_ids_for_chat(chat_id: int, db: Session) -> list:
    chat = db.query(models.Chat).filter(models.Chat.id == chat_id).first()
    if not chat:
        return []
    return [doc.id for doc in chat.documents]