from sqlalchemy.orm import Session
import logging

from core.entities import user as user_entity
from database import models

"""
Docstring for database.db_access.user_access.py

This module contains methods to access the database for 
"""

logger = logging.getLogger(__name__)


def get_user_by_email(db: Session, email: str) -> user_entity.UserRetrieve | None:
    """
    Gets a user row by their email address

    returns a User entity object
    """
    logger.info("Inside user_access.get_user_by_email()")
    
    user_row = db.query(models.User).filter(models.User.email == email).first()

    if user_row is None: # user not found
        return None
    
    return user_entity.UserRetrieve(
        id=user_row.id,
        email=user_row.email,
        hashed_password=user_row.hashed_password,
    )


def create_user(db: Session, user_info: user_entity.UserCreate) -> user_entity.UserCreateResponse:
    """
    Creates a new user in the database

    :param user_info: UserCreate entity object containing user details
    :return: UserRetrieve entity object containing created user details
    """
    logger.info("Inside user_access.create_user()")
    # you can only be in this method if the user does not already exist
    # service layer makes sure of that

    # creating a new user entry
    new_user = models.User(
        first_name=user_info.first_name,
        last_name=user_info.last_name,
        email=user_info.email,
        hashed_password=user_info.hashed_password,
        created_at=user_info.created_at,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info("New user created in the database")

    return user_entity.UserCreateResponse(
        id=new_user.id,
        first_name=new_user.first_name,
        last_name=new_user.last_name,
        email=new_user.email,
    )