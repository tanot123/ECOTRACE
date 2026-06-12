from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRY_MINUTES: int = 1440
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.0-flash"
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]
    SEED_DATA: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
