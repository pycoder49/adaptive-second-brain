"""
Database entities for Chat functionality
"""

from dataclasses import dataclass


@dataclass
class ChatCreate:
    user_id: int
    title: str


@dataclass
class ChatRetrieve(ChatCreate):
    id: int
    created_at: str