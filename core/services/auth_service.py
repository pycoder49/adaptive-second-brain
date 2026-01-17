# services for authentication
# calls on the db_access layer to fetch information from the database
from sqlalchemy.orm import Session

from ..entities import user as user_entity
from database.db_access.user_access import get_user_by_email
from ..utils.utils import verify_password
from .errors.errors import InvalidCredentialsException, UserNotFoundException

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

    # this method needs to call the db_access layer to verify user credentials

    # expects a User object from db_access layer
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

    
    
    