from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import logging

from ..schemas import chat_schemas
from core.services import chat_services

from database.database import get_db
from api.routes.auth import get_current_user


logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/chat",
    tags=["Chats"],
)


"""
Need methods for:
- Getting all chats
- Getting all messages in a chat
- Getting a single chat by ID

- Creating a new chat
- Adding a message to a chat
"""


"""
Endpoints for chat management
"""
@router.get("/", response_model=List[chat_schemas.ChatResponse])
def get_chats(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Retrieves all conversations for the authenticated user

    :param user: The authenticated user object
    :param db: Database session dependency

    :return: List of chat meta data
    """
    logger.info("Fetching all chats from the service layer")
    chats: List[dict] = chat_services.get_all_chats(user["id"], db)

    if not chats:
        logger.info("No conversations found, returning empty list")
        return []
    
    # convert list of dict to list of ChatResponse schemas
    chats = [
        chat_schemas.ChatResponse(
            id=chat.get("id"),
            user_id=chat.get("user_id"),    
            title=chat.get("title"),
            created_at=chat.get("created_at"),
        )
        for chat in chats
    ]
    return chats


# creates a new chat
@router.post("/", response_model=chat_schemas.ChatCreate)
def create_chat(user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Creates a new conversation for the authenticated user

    :param user: The authenticated user object
    :param db: Database session dependency

    :return: The created chat object
    """
    logger.info("Creating a new chat in the service layer")
    new_chat = chat_services.create_chat(user["id"], db)
    # object containing the meta data of the newly created chat

    response = chat_schemas.ChatResponse(
        id = new_chat.get("id"),
        user_id = new_chat.get("user_id"),
        title = new_chat.get("title"),
        created_at = new_chat.get("created_at"),
    )
    return response


"""
Endpoints for message management
# """

# retrieves all messages for a specific chat
@router.get("/{chat_id}", response_model=chat_schemas.MessageResponse)
def get_all_messages_for_chat(
    chat_id: int,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves all messages for a specific chat

    :param chat_id: The ID of the chat whose messages are being retrieved
    :param user: The authenticated user object
    :param db: Database session dependency

    :return: List of messages in the chat
    """
    logger.info(f"Retrieving all messages for chat ID {chat_id} from the service layer")
    # authentication via get_current_user dependency (done)
    # check if the chat exists
    chat = chat_services.get_chat_by_id(chat_id, db)
    if not chat:
        logger.error(f"Chat with ID {chat_id} not found")
        raise HTTPException(status_code=404, detail="Chat not found")

    # check if the user has access to the chat
    if chat.get("user_id") != user["id"]:
        logger.error(f"User {user['id']} is unauthorized to access chat {chat_id}")
        raise HTTPException(status_code=403, detail="Unauthorized access to chat")
    
    # fetch chat meta data from the service layer
    # chat data is already fetched above in the variable: chat

    # fetch all messages for the chat from the service layer
    all_messages: List[dict] = chat_services.get_all_messages(chat_id, db)

    # construct and return the response object
    chat_response = chat_schemas.ChatResponse(
        id = chat.get("id"),
        user_id = chat.get("user_id"),
        title = chat.get("title"),
        created_at = chat.get("created_at"),
    )
    user_messages = [
        chat_schemas.Message(
            id = message.get("id"),
            role = message.get("role"),
            content = message.get("content"),
            created_at = message.get("created_at"),
        )
        for message in all_messages
    ]

    # returning the assistant response in the response object
    return chat_schemas.MessageResponse(
        chat = chat_response,
        messages = user_messages,
    )


# post a new message to a specific chat
@router.post("/{chat_id}/message", response_model=List[chat_schemas.Message])
def post_message_to_chat(
    chat_id: int,
    message: chat_schemas.MessageCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Posts a new message to a specific chat
    
    :param chat_id: The ID of the chat to which the message is being posted
    :param content: The content of the message being posted as a string
    :param user: The authenticated user object
    :param db: Database session dependency

    :return: The created message object
    """
    logger.info(f"Posting a new message to chat ID {chat_id} from the service layer")

    # authentication via get_current_user dependency (done)
    # check if the chat exists -- could be optimized later so we don't havee to make multiple checks every time
    chat = chat_services.get_chat_by_id(chat_id, db)
    if not chat:
        logger.error(f"Chat with ID {chat_id} not found")
        raise HTTPException(status_code=404, detail="Chat not found")
    
    # check if the user has access to the chat
    if chat.get("user_id") != user["id"]:
        logger.error(f"User {user['id']} is unauthorized to access chat {chat_id}")
        raise HTTPException(status_code=403, detail="Unauthorized access to chat")

    # Add the message to the db via the service layer
    new_message = chat_services.post_message_to_chat(
        chat_id = chat_id,
        role = "user",
        content = message.content,
        db = db,
    )

    # sending message to the rag inference engine via the service layer
    rag_response: str
    rag_response = "This is a placeholder response for now"
    # rag_response = rag_inference_engine.get_response(content)

    # adding the assistnat response to the db via the service layer
    assistant_response = chat_services.post_message_to_chat(
        chat_id = chat_id,
        role = "ai",
        content = rag_response,
        db = db,
    )

    # returning the assistant response in the response object
    return [
        chat_schemas.Message(
            id = new_message.get("id"),
            role = new_message.get("role"),
            content = new_message.get("content"),
            created_at = new_message.get("created_at"),
        ),
        chat_schemas.Message(
            id = assistant_response.get("id"),
            role = assistant_response.get("role"),
            content = assistant_response.get("content"),
            created_at = assistant_response.get("created_at"),
        )
    ]
