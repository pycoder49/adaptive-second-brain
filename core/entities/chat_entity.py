"""
Database entities for Chat functionality
"""

from dataclasses import dataclass

@dataclass
class ChatRetrieve:
    id: int
    user_id: int
    title: str
    created_at: str