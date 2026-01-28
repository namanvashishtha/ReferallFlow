from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    PROJECT_NAME: str = "ReferralForge"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"
    
    DATABASE_URL: str
    SQLALCHEMY_ECHO: bool = False
    
    AUTH0_DOMAIN: str
    AUTH0_CLIENT_ID: str
    AUTH0_CLIENT_SECRET: str
    AUTH0_API_AUDIENCE: str
    AUTH0_CALLBACK_URL: str
    
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    ENCRYPTION_KEY: str
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    HUNTER_IO_API_KEY: str = ""
    SENDGRID_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    # Hugging Face Inference API
    HF_MCP_URL: str = "https://api-inference.huggingface.co/models"
    HF_MCP_TOKEN: str = ""
    HF_MODEL_ID: str = "mistralai/Mistral-7B-Instruct-v0.3"

    # Rate limiting and scraping
    RATE_LIMIT_PER_MINUTE: int = 60
    SCRAPER_CONCURRENCY: int = 3
    PROXY_LIST: List[str] = []

    # SMTP / Email settings
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = ""

    # Logging
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
