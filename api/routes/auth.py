from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session

from ..schemas import schemas
from database.database import get_db

from core.services import auth_service
from core.services.errors.errors import InvalidCredentialsException, UserNotFoundException


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
    # call the auth_service layer within code (business) layer to authenticate user
    email = user_credentials.email
    password = user_credentials.password

    try:
        user_info = auth_service.authenticate_user(db, email, password)
        # expects a dict or error
    except (InvalidCredentialsException, UserNotFoundException) as e:
        raise HTTPException(status_code=401, detail=e.message)
    
    return user_info
