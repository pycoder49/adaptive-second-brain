# services for authentication
# calls on the db_access layer to fetch information from the database
from sqlalchemy.orm import Session
import datetime
import logging

from ..entities import user as user_entity
from ..utils.utils import hash_password, verify_password

from database.db_access.user_access import (
    get_user_by_email,
    create_user,
)
from .errors.user_errors import (
    InvalidCredentialsException, 
    UserNotFoundException,
    UserAlreadyExistsException,
)


logger = logging.getLogger(__name__)


def authenticate_user(db: Session, email: str, password: str) -> dict:
    """
    Authenticates a user by verifying their email and password

    :param email: The user's email address
    :type email: str

    :param password: The user's password
    :type password: str

    :return: A dictionary containing user information if authentication is successful
    :rtype: dict
    """
    logger.info("Inside auth_service.authenticate_user()")

    # this method needs to call the db_access layer to verify user credentials

    # expects a UserRetrieve object from db_access layer
    logger.info("Calling get_user_by_email from user_access")
    user_entity_obj = get_user_by_email(db, email)

    if user_entity_obj is None: # user not found
        raise UserNotFoundException()
    
    # if found, we verify the password
    # get the hashed password from the user entity object
    hashed_password = user_entity_obj.hashed_password
    if not verify_password(password, hashed_password):
        raise InvalidCredentialsException()
    
    return {
        "user_id": user_entity_obj.id,
        "email": user_entity_obj.email,
    }


def register_user(
        db: Session,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
) -> dict:
    """
    Registers a new user in the system
    
    :param db: Database session
    :param first_name: First name
    :param last_name: Last name
    :param email: user email
    :param password: user password

    :return: Dictionary containing user information upon successful registration
    """
    logger.info("Inside auth_service.register_user()")

    # check if user already exists
    logger.info("Checking if user already exists")
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise UserAlreadyExistsException()

    # hashing the password
    hashed_password = hash_password(password)

    # create a UserCreate entity object
    user_entity_obj = user_entity.UserCreate(
        first_name=first_name,
        last_name=last_name,
        email=email,
        hashed_password=hashed_password,
        created_at=datetime.datetime.now(datetime.timezone.utc)
    )

    logger.info("Calling create_user from user_access")
    user = create_user(db, user_entity_obj)

    return {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
    }

    
    