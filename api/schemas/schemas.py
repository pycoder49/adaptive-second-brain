from pydantic.types import conint
from pydantic import BaseModel, EmailStr


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserRegister(UserLogin):
    pass # same as UserLogin for now
