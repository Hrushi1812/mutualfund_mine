import pytest
from app.services.portfolio_service import PortfolioService

@pytest.mark.asyncio
async def test_create_portfolio(test_db, sample_portfolio_data):
    """Test creating a new portfolio"""
    service = PortfolioService(test_db)
    portfolio_id = await service.create_portfolio(sample_portfolio_data)
    assert portfolio_id is not None

@pytest.mark.asyncio
async def test_get_portfolio_by_id(test_db, sample_portfolio_data):
    """Test retrieving a portfolio by ID"""
    service = PortfolioService(test_db)
    portfolio_id = await service.create_portfolio(sample_portfolio_data)
    portfolio = await service.get_portfolio_by_id(portfolio_id)
    assert portfolio is not None
    assert portfolio["scheme_code"] == sample_portfolio_data["scheme_code"]

@pytest.mark.asyncio
async def test_get_all_portfolios(test_db, sample_portfolio_data):
    """Test retrieving all portfolios"""
    service = PortfolioService(test_db)
    await service.create_portfolio(sample_portfolio_data)
    portfolios = await service.get_all_portfolios()
    assert isinstance(portfolios, list)
    assert len(portfolios) >= 1

@pytest.mark.asyncio
async def test_delete_portfolio(test_db, sample_portfolio_data):
    """Test deleting a portfolio"""
    service = PortfolioService(test_db)
    portfolio_id = await service.create_portfolio(sample_portfolio_data)
    result = await service.delete_portfolio(portfolio_id)
    assert result is True
    portfolio = await service.get_portfolio_by_id(portfolio_id)
    assert portfolio is None