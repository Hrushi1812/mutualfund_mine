from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Literal
from datetime import datetime
from enum import Enum

class HoldingItem(BaseModel):
    """Schema for a single stock holding within a fund."""
    ISIN: str
    Name: str
    Symbol: str
    Weight: float = Field(..., gt=0)

class SIPInstallment(BaseModel):
    date: str  # DD-MM-YYYY
    amount: float
    units: Optional[float] = None  # None = pending NAV allocation
    nav: Optional[float] = None
    nav_date: Optional[str] = None  # Which date's NAV was used for allocation
    status: Literal["PENDING", "PAID", "SKIPPED", "ASSUMED_PAID"] = "PENDING"
    allocation_status: Literal["PENDING_NAV", "ESTIMATED", "CONFIRMED"] = "PENDING_NAV"
    is_estimated: bool = False

class HoldingsDocument(BaseModel):
    """Schema for the 'holdings' collection in MongoDB."""
    fund_name: str
    user_id: str
    scheme_code: Optional[str] = None
    invested_amount: Optional[float] = None
    invested_date: Optional[str] = None # YYYY-MM-DD
    nickname: Optional[str] = None
    # Investment Details
    investment_type: Literal["lumpsum", "sip"] = "lumpsum"
    
    # SIP Specific Config
    sip_amount: Optional[float] = 0.0
    sip_start_date: Optional[str] = None
    sip_frequency: Optional[str] = "Monthly" # Monthly, Weekly, etc.
    sip_day: Optional[int] = None # Day of month for SIP
    
    # SIP Tracking
    manual_total_units: Optional[float] = 0.0 # User provided total units (static start balance)
    manual_invested_amount: Optional[float] = 0.0 # User provided invested amount from CAS (static)
    future_sip_units: float = 0.0 # Accumulated units from tracked installments
    sip_installments: List[SIPInstallment] = []
    
    holdings: List[HoldingItem]
    last_updated: bool = True # Legacy field, maybe change to datetime?
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserUpload(BaseModel):
    holding_id: str
    fund_name: str
    invested_date: Optional[str] = None
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)

class UserDocument(BaseModel):
    """Schema for the 'users' collection."""
    username: str
    email: EmailStr
    hashed_password: str
    uploads: List[UserUpload] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class SIPAction(BaseModel):
    date: str
    action: Literal["PAID", "SKIPPED"]

