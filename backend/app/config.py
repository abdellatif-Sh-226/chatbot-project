"""
Application configuration.

Loads environment variables and provides typed settings
for database, JWT, AI API, and general app configuration.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App metadata
    APP_NAME: str = "Smart Library Management System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # MySQL database connection details
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "library_chatbot"

    # JWT authentication settings
    JWT_SECRET_KEY: str = "change-this-to-a-strong-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # AI chatbot API (Google Gemini recommended)
    AI_API_KEY: Optional[str] = None
    AI_MODEL: str = "gemini-2.0-flash"

    @property
    def DATABASE_URL(self) -> str:
        """Build the MySQL connection URL for SQLAlchemy."""
        return (
            f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )

    model_config = {"env_file": ".env", "case_sensitive": True}


settings = Settings()
