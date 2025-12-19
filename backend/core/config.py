import os
from dotenv import load_dotenv

load_dotenv()

# Detect environment: production if RENDER or PRODUCTION env var is set
IS_PRODUCTION = os.getenv("RENDER") or os.getenv("PRODUCTION") or os.getenv("ENV") == "production"

class Settings:
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    MONGO_DB: str = os.getenv("MONGO_DB", "mutual_funds")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    # Default to localhost for development, can be overridden by env var (comma separated)
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    
    # Fyers API Configuration
    FYERS_APP_ID: str = os.getenv("FYERS_APP_ID", "DXGLWQ4E2O-100")
    FYERS_SECRET_KEY: str = os.getenv("FYERS_SECRET_KEY", "")  # <-- SET THIS IN .env FILE
    
    # Auto-detect redirect URI based on environment
    FYERS_REDIRECT_URI: str = os.getenv(
        "FYERS_REDIRECT_URI",
        "https://mutualfund-tracker.onrender.com/api/fyers/callback" if IS_PRODUCTION 
        else "http://localhost:8000/api/fyers/callback"
    )

settings = Settings()
