from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime, date

class Holding(BaseModel):
    isin: str
    instrument_name: str
    industry: str
    quantity: float
    market_value_lakhs: float
    percentage_to_nav: float
    ticker: Optional[str] = None
    current_price: Optional[float] = None
    price_change_percent: Optional[float] = None

class PortfolioCreate(BaseModel):
    invested_amount: float
    investment_date: date
    scheme_code: Optional[str] = None
    scheme_name: Optional[str] = None

class Portfolio(BaseModel):
    id: Optional[str] = None
    user_id: str
    invested_amount: float
    investment_date: date
    nav_at_investment: Optional[float] = None
    units: Optional[float] = None
    current_nav: Optional[float] = None
    current_value: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percent: Optional[float] = None
    holdings: List[Holding] = []
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class NAVHistory(BaseModel):
    portfolio_id: str
    date: date
    nav: float
    current_value: float
    pnl: float
    pnl_percent: float

class PortfolioSummary(BaseModel):
    portfolio: Portfolio
    nav_history: List[NAVHistory]
    total_holdings: int
    top_sectors: Dict[str, float]
