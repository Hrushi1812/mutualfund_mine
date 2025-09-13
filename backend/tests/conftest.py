import pytest
import asyncio
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient
import os
from datetime import datetime, date
import pandas as pd

# Set test environment
os.environ["MONGODB_URL"] = "mongodb://localhost:27017"
os.environ["DATABASE_NAME"] = "mutual_fund_tracker_test"
os.environ["JWT_SECRET_KEY"] = "test-secret-key"

from app.main import app
from app.database import get_database

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    """FastAPI test client"""
    return TestClient(app)

@pytest.fixture
async def test_db():
    """Test database connection"""
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client["mutual_fund_tracker_test"]
    yield db
    # Cleanup after tests
    await client.drop_database("mutual_fund_tracker_test")
    client.close()

@pytest.fixture
def sample_holdings_data():
    """Sample holdings data for testing"""
    return [
        {
            "isin": "INE002A01018",
            "instrument_name": "Reliance Industries Ltd",
            "industry": "Oil & Gas",
            "quantity": 1000.0,
            "market_value_lakhs": 25.5,
            "percentage_to_nav": 15.2
        },
        {
            "isin": "INE009A01021",
            "instrument_name": "Infosys Ltd",
            "industry": "Information Technology",
            "quantity": 500.0,
            "market_value_lakhs": 18.3,
            "percentage_to_nav": 10.9
        },
        {
            "isin": "INE467B01029",
            "instrument_name": "Tata Consultancy Services Ltd",
            "industry": "Information Technology",
            "quantity": 300.0,
            "market_value_lakhs": 22.1,
            "percentage_to_nav": 13.2
        }
    ]

@pytest.fixture
def sample_excel_file():
    """Create a sample Excel file for testing"""
    data = {
        'ISIN': ['INE002A01018', 'INE009A01021', 'INE467B01029'],
        'Instrument Name': ['Reliance Industries Ltd', 'Infosys Ltd', 'Tata Consultancy Services Ltd'],
        'Industry': ['Oil & Gas', 'Information Technology', 'Information Technology'],
        'Quantity': [1000.0, 500.0, 300.0],
        'Market Value (lakhs)': [25.5, 18.3, 22.1],
        '% to NAV': [15.2, 10.9, 13.2]
    }
    df = pd.DataFrame(data)
    
    # Save to bytes
    import io
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return buffer.getvalue()

@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "name": "Test User",
        "email": "test@example.com",
        "password": "testpassword123"
    }

@pytest.fixture
def sample_portfolio_data():
    """Sample portfolio data for testing"""
    return {
        "invested_amount": 100000.0,
        "investment_date": date(2024, 1, 15),
        "scheme_code": "120503",
        "scheme_name": "Test Mutual Fund"
    }