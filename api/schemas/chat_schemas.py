from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Chat(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime


class ChatResponse(Chat):
    pass


class Message(BaseModel):
    id: int
    chat_id: int
    chunk_ids: Optional[List[int]]
    role: str
    content: str
    created_at: datetime