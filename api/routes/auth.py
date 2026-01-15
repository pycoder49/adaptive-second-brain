from fastapi import APIRouter, HTTPException, Depends, Response, status
from sqlalchemy.orm import Session

from ..schemas import schemas
from ...database import models
from ...database.database import get_db


router = APIRouter(tags=["authentication"])


@router.post("/login")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    # call the core (business) layer to authenticate user
    try:
        pass
    except Exception as e:
        pass