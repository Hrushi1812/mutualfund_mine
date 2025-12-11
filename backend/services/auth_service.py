from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from db import users_collection
from core.config import settings
from models.schemas import TokenData, UserCreate

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class AuthService:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def get_user(username: str):
        return users_collection.find_one({"username": username})

    @staticmethod
    def create_user(user: UserCreate):
        if AuthService.get_user(user.username):
            raise HTTPException(status_code=400, detail="Username already registered")
        
        hashed_password = AuthService.get_password_hash(user.password)
        new_user = {
            "username": user.username,
            "email": user.email,
            "hashed_password": hashed_password,
            "created_at": datetime.utcnow()
        }
        users_collection.insert_one(new_user)
        return new_user

    @staticmethod
    def authenticate_user(username, password):
        user = AuthService.get_user(username)
        if not user:
            return None
        if not AuthService.verify_password(password, user["hashed_password"]):
            return None
        return user

auth_service = AuthService()
