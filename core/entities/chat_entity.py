"""
Database entities for Chat functionality
"""

from dataclasses import dataclass
import enum


class Role(enum.Enum):
    USER = "user"
    AI = "ai"


@dataclass
class ChatCreate:
    user_id: int
    title: str


@dataclass
class ChatRetrieve(ChatCreate):
    id: int
    created_at: str


@dataclass
class MessageRetrieve:
    id: int
    chat_id: int
    role: str
    content: str
    created_at: str