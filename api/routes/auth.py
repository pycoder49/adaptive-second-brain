from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session
import logging

from ..schemas import schemas
from database.database import get_db

from core.services import auth_service

from core.services.errors.user_errors import (
    InvalidCredentialsException, 
    UserNotFoundException,
    UserAlreadyExistsException
)

logger = logging.getLogger(__name__)

router = APIRouter(
    tags=["Authentication"],
)


@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)) -> dict:
    """
    Authenticates a user and returns user information upon successful login
    
    :param user_credentials: UserLogin schema object containing email and password
    :param db: Database session dependency

    :return: Dictionary containing user information if authentication is successful
    """
    logger.info(f"Inside login endpoint")
    # call the auth_service layer within code (business) layer to authenticate user
    email = user_credentials.email
    password = user_credentials.password

    try:
        logger.info("Calling auth_service.authenticate_user")
        user_info = auth_service.authenticate_user(db, email, password)
        # expects a dict or error
    except (InvalidCredentialsException, UserNotFoundException) as e:
        raise HTTPException(status_code=401, detail=e.message)
    
    logger.info("User authenticated successfully -- logged in")
    return user_info


@router.post("/register",)
def register(user_details: schemas.UserRegister, db: Session = Depends(get_db)) -> dict:
    """
    Registers a new user in the system

    :param user_details: UserRegister schema object containing email and password
    :param db: Database session dependency

    :return: Dictionary containing user information upon successful registration
    """
    logger.info(f"Inside register endpoint")
    # calling the auth_service layer to take care of this operation
    first_name = user_details.first_name
    last_name = user_details.last_name
    email = user_details.email
    password = user_details.password

    try:
        logger.info("Calling auth_service.register_user")
        user_info = auth_service.register_user(
            db = db,
            first_name = first_name,
            last_name = last_name,
            email = email,
            password = password,
        )
    except UserAlreadyExistsException as e:
        raise HTTPException(status_code=409, detail=e.message)
        # conflict error for existing user
    
    logger.info("User registered successfully")
    return user_info