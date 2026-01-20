from pydantic.types import conint
from pydantic import BaseModel, EmailStr


"""
Schemas for user related requests and responses
"""

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(UserLogin):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
