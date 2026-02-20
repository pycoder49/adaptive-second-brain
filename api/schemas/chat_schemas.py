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
    created_at: datetime


class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    # object containing chat meta data and list of messages
    chat: ChatResponse
    messages: List[Message]

