from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    APP_NAME: str = "VeriServ"
    DEBUG: bool = False
    SECRET_KEY: str = "CAMBIA_ESTO_EN_PRODUCCION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7
    DATABASE_URL: str = "postgresql://user:password@localhost/veriserv"
    ALLOWED_ORIGINS: List[str] = ["http://localhost:5173"]
    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""
    class Config:
        env_file = ".env"

settings = Settings()
