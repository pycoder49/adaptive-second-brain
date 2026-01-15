from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session

from ..schemas import schemas
from ...database import models
from ...database.database import get_db

from ...core.service.auth_service import authenticate_user


router = APIRouter(tags=["authentication"])


@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)) -> status:
    # call the core (business) layer to authenticate user
    is_valid = authenticate_user()