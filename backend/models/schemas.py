from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

# --- Auth Schemas ---
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# --- Application Schemas ---
class FundBase(BaseModel):
    fund_name: str
    scheme_code: Optional[str] = None
    invested_amount: Optional[float] = None
    invested_date: Optional[str] = None # Format: YYYY-MM-DD
    nickname: Optional[str] = None

class PortfolioAnalysisRequest(BaseModel):
    fund_id: str
    investment_amount: Optional[float] = None
    investment_date: Optional[str] = None # YYYY-MM-DD
