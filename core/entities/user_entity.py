"""
Docstring for core.entities.user

This module defines the User db object used by services to interact with user data in the database
"""

from dataclasses import dataclass

@dataclass
class UserRetrieve:
    id: int
    email: str
    hashed_password: str


@dataclass
class UserCreate:
    first_name: str
    last_name: str
    email: str
    hashed_password: str
    created_at: str


@dataclass
class UserCreateResponse:
    id: int
    first_name: str
    last_name: str
    email: str