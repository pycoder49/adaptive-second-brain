# services for authentication
# calls on the db_access layer to fetch information from the database
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import datetime
import logging

from ..entities import user_entity as user_entity   
from config.settings import settings
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


def authenticate_user(email: str, password: str, db: Session) -> dict:
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
    user_entity_obj = get_user_by_email(email, db)

    if user_entity_obj is None: # user not found
        logger.info("User not found with this email")
        raise UserNotFoundException()
    
    # if found, we verify the password
    # get the hashed password from the user entity object
    hashed_password = user_entity_obj.hashed_password
    if not verify_password(password, hashed_password):
        logger.info("Password verification failed")
        raise InvalidCredentialsException()
    
    return {
        "user_id": user_entity_obj.id,
        "email": user_entity_obj.email,
    }


def register_user(
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        db: Session,
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
    existing_user = get_user_by_email(email, db)
    if existing_user:
        logger.info("User already exists with this email")
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
    user = create_user(user_entity_obj, db)

    return {
        "user_id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "email": user.email,
    }


def create_access_token(data: dict) -> str:
    """
    Creates a JWT access token for the given user data

    :param data: Dictionary containing user data to encode in the token
    :return: JWT access token as a string
    """
    logger.info("Inside auth_service.create_access_token()")

    to_encode = data.copy()
    expires = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expires})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        settings.ALGORITHM,
    )

    return encoded_jwt


def verify_access_token(token: str) -> dict:
    """
    Verifies a JWT access token and returns the decoded data
    
    :param token: JWT access token as a string
    :return: Decoded token data as a dictionary
    """
    logger.info("Inside auth_service.verify_access_token()")

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = payload.get("user_id")
        email = payload.get("email")

        if user_id is None or email is None:
            logger.error("Invalid token payload")
            raise InvalidCredentialsException()
        
        logger.info("JWT token verified successfully")
        return {
            "user_id": user_id,
            "email": email,
        }
    except JWTError:
        logger.error("JWT verification failed")
        raise InvalidCredentialsException()
    

def get_current_user(token: str, db: Session) -> dict:
    """
    Gets the current authenticated user from the JWT token

    :param token: JWT access token as a string
    :param db: Database session
    :return: UserRetrieve entity object of the current user
    """
    logger.info("Inside auth_service.get_current_user()")

    # verifying the token
    payload = verify_access_token(token)
    user_email = payload["email"]

    user = get_user_by_email(user_email, db)
    if user is None:
        logger.error("User not found for the given token")
        raise UserNotFoundException()

    return {
        "id": user.id,
        "email": user.email,
    }
    
    