from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class ChatCreate(BaseModel):
    id: int
    user_id: int
    title: str


class ChatResponse(ChatCreate):
    created_at: datetime


class Message(BaseModel):
    id: int
    role: str
    content: str
    parent_message_id: Optional[int] = None
    created_at: datetime


class MessageCreate(BaseModel):
    content: str
    document_ids: Optional[List[int]] = []


class MessageResponse(BaseModel):
    chat: ChatResponse
    messages: List[Message]

