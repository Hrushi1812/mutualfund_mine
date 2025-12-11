from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

class HoldingItem(BaseModel):
    """Schema for a single stock holding within a fund."""
    ISIN: str
    Name: str
    Symbol: str
    Weight: float = Field(..., gt=0)

class HoldingsDocument(BaseModel):
    """Schema for the 'holdings' collection in MongoDB."""
    fund_name: str
    user_id: str
    scheme_code: Optional[str] = None
    invested_amount: Optional[float] = None
    invested_date: Optional[str] = None # YYYY-MM-DD
    nickname: Optional[str] = None
    holdings: List[HoldingItem]
    last_updated: bool = True # Legacy field, maybe change to datetime?
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserDocument(BaseModel):
    """Schema for the 'users' collection."""
    username: str
    email: EmailStr
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
