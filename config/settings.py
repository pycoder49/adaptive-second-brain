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

    # RAG settings
    # Options: "placeholder" | "dev" | "production"
    RAG_IMPLEMENTATION: str

    # R2 storage settings
    ACCOUNT_KEY_ID: str
    SECRET_ACCESS_KEY: str
    S3_ENDPOINT_URL: str
    BUCKET_NAME: str

    
    # NOT ACCESSED
    ACCOUNT_API_TOKEN: Optional[str] = None

    class Config:
        env_file = "./.env"
    
    
settings = Settings()
