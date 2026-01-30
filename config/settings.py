from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # database settings
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # JWT settings
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = "./.env"
    
settings = Settings()
