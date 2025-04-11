
import os
from pydantic import BaseSettings, PostgresDsn
from typing import Optional
from dotenv import load_dotenv

load_dotenv()  # Load .env file

class Settings(BaseSettings):
    API_V1_STR: str = "/api"
    PROJECT_NAME: str = "Proteus.lab API"
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "insecure-secret-key-for-dev-only")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    DATABASE_URL: Optional[PostgresDsn] = os.getenv("DATABASE_URL")
    
    # CORS settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]

    # File upload settings
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50 MB
    ALLOWED_EXTENSIONS: list = [".stl", ".obj", ".3mf"]
    
    # Email settings
    EMAIL_ENABLED: bool = os.getenv("EMAIL_ENABLED", "False").lower() in ("true", "1", "t")
    EMAIL_SENDER: str = os.getenv("EMAIL_SENDER", "noreply@proteuslab.com")
    SMTP_SERVER: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() in ("true", "1", "t")
    
    # Frontend URL for links in emails
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")
    
    # Google Drive integration
    GDRIVE_ENABLED: bool = os.getenv("GDRIVE_ENABLED", "False").lower() in ("true", "1", "t")
    GDRIVE_FOLDER_ID: str = os.getenv("GDRIVE_FOLDER_ID", "")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
