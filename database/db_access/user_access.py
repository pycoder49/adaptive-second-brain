from sqlalchemy.orm import Session

from core.entities import user as user_entity
from database import models

"""
Docstring for database.db_access.user_access.py

This module contains methods to access the database for 
"""

def get_user_by_email(db: Session, email: str) -> user_entity.Uzser | None:
    """
    Gets a user row by their email address

    returns a User entity object
    """
    user_row = db.query(models.User).filter(models.User.email == email).first()

    if user_row is None: # user not found
        return None
    
    return user_entity.User(
        id=user_row.id,
        email=user_row.email,
        hashed_password=user_row.hashed_password,
    )
