from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import List
from app.services.excel_parser import ExcelParser
from app.services.ticker_mapping import TickerMapper
from app.services.portfolio_service import PortfolioService
from app.models.portfolio import PortfolioCreate, Portfolio
from app.database import get_database
from bson import ObjectId
import asyncio

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Dummy get_current_user dependency for example (replace with real auth)
async def get_current_user(token: str = Depends(oauth2_scheme)):
    # TODO: decode token and get user info
    # For now, return a dummy user id
    return {"id": "user123"}

@router.post("/upload", summary="Upload AMC disclosure Excel/CSV file")
async def upload_amc_file(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    content = await file.read()
    holdings = await ExcelParser.parse_amc_disclosure(content, file.filename)
    
    # Map ISINs to tickers
    isins = [h['isin'] for h in holdings]
    mapper = TickerMapper()
    isin_to_ticker = await mapper.bulk_map_isins(isins)
    
    # Add ticker info to holdings
    for h in holdings:
        h['ticker'] = isin_to_ticker.get(h['isin'])
    
    return holdings

@router.post("/", summary="Create a new portfolio")
async def create_portfolio(
    portfolio_data: PortfolioCreate,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    service = PortfolioService(db)
    portfolio = await service.create_portfolio(
        user_id=current_user['id'],
        invested_amount=portfolio_data.invested_amount,
        investment_date=portfolio_data.investment_date,
        scheme_code=portfolio_data.scheme_code,
        scheme_name=portfolio_data.scheme_name,
        holdings=portfolio_data.holdings if hasattr(portfolio_data, 'holdings') else []
    )
    return {"portfolio_id": str(portfolio.inserted_id)}

@router.get("/{portfolio_id}", response_model=Portfolio, summary="Get portfolio details")
async def get_portfolio(
    portfolio_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    service = PortfolioService(db)
    portfolio = await service.get_portfolio(portfolio_id, current_user['id'])
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio

@router.get("/{portfolio_id}/refresh", summary="Refresh portfolio prices and NAV")
async def refresh_portfolio(
    portfolio_id: str,
    current_user: dict = Depends(get_current_user),
    db=Depends(get_database)
):
    service = PortfolioService(db)
    updated_portfolio = await service.refresh_portfolio(portfolio_id, current_user['id'])
    if not updated_portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found or update failed")
    return updated_portfolio