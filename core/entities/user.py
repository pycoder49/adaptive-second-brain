"""
Docstring for core.entities.user

This module defines the User db object used by services to interact with user data in the database
"""

from dataclasses import dataclass

@dataclass
class User:
    id: int
    email: str
    hashed_password: str
