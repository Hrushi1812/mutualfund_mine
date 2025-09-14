from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    mongodb_url: str = "mongodb://localhost:27017/mutual_fund_tracker"
    database_name: str = "mutual_fund_tracker"
    
    # JWT
    jwt_secret_key: str = "your-super-secret-jwt-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # API
    api_v1_str: str = "/api/v1"
    project_name: str = "Mutual Fund Tracker API"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Create settings instance
settings = Settings()

# Override CORS origins for production
if settings.environment == "production":
    settings.cors_origins = [
        "https://mutual-fund-tracker-frontend.onrender.com",
        "https://mutual-fund-tracker.onrender.com"
    ]
