from fastapi import APIRouter, HTTPException, Depends, Response, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
import logging

from ..schemas import user_schemas, auth_schemas
from database.database import get_db

from core.services import auth_services

from core.services.errors.user_errors import (
    InvalidCredentialsException, 
    UserNotFoundException,
    UserAlreadyExistsException
)

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

oauth_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/login", response_model=auth_schemas.TokenResponse)
def login(user_credentials: user_schemas.UserLogin, db: Session = Depends(get_db)):
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
        user_info = auth_services.authenticate_user(email, password, db)

        # creating the jwt access token
        logger.info("Creating access token for authenticated user")
        access_token = auth_services.create_access_token(
            data={
                "user_id": user_info["user_id"], 
                "email": user_info["email"],
            }
        )
    except (InvalidCredentialsException, UserNotFoundException) as e:
        logger.error("Authentication failed in login endpoint")
        raise HTTPException(status_code=401, detail=e.message, headers={"WWW-Authenticate": "Bearer"})
        # unauthorized error for invalid credentials

    logger.info("Access token created successfully")
    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/register",)
def register(user_details: user_schemas.UserRegister, db: Session = Depends(get_db)) -> dict:
    """
    Registers a new user in the system

    :param user_details: UserRegister schema object containing email and password
    :param db: Database session dependency

    :return: Dictionary containing user information upon successful registration
    """
    logger.info(f"Inside register endpoint")

    try:
        logger.info("Calling auth_service.register_user")
        user_info = auth_services.register_user(
            first_name = user_details.first_name,
            last_name = user_details.last_name,
            email = user_details.email,
            password = user_details.password,
            db = db,
        )
    except UserAlreadyExistsException as e:
        logger.error("UserAlreadyExistsException caught in register endpoint")
        raise HTTPException(status_code=409, detail=e.message)
        # conflict error for existing user
    
    logger.info("User registered successfully")
    return user_info


# Dependency for protected routes to get current user
def get_current_user(
        token: str = Depends(oauth_scheme),
        db: Session = Depends(get_db),
) -> dict:
    """
    Dependency to get current authenticated user from JWT token
    Use this in protected routes: current_user = Depends(get_current_user)
    
    :param token: JWT token from Authorization header
    :param db: Database session
    :return: User object
    """

    # verify token and get current user
    try:
        user = auth_services.get_current_user_from_token(token, db)
        return user
    except InvalidCredentialsException as e:
        logger.error("InvalidCredentialsException caught in get_current_user")
        raise HTTPException(status_code=401, detail=e.message, headers={"WWW-Authenticate": "Bearer"})
        
    
# route to test protected endpoint
@router.get("/me", response_model=user_schemas.UserResponse)
def read_me(current_user = Depends(get_current_user)):
    """
    Protected endpoint to get current authenticated user info

    :param current_user: Current authenticated user from dependency
    :return: Current user information
    """
    logger.info("Inside protected /me endpoint")
    return {
        "id": current_user["id"],
        "email": current_user["email"]
    }
