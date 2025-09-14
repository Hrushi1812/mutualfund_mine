import pytest
from unittest.mock import patch, MagicMock
from datetime import date, datetime
import pandas as pd
from app.services.market_data import MarketDataService

class TestMarketDataService:
    
    @pytest.mark.asyncio
    @patch('yfinance.download')
    async def test_get_live_stock_prices_single_ticker(self, mock_yf_download):
        """Test fetching live prices for single ticker"""
        # Mock yfinance response
        mock_data = pd.DataFrame({
            'Close': [2500.0, 2550.0],  # Previous and current price
            'Volume': [1000000, 1200000]
        })
        mock_yf_download.return_value = mock_data
        
        service = MarketDataService()
        tickers = ["RELIANCE.NS"]
        
        prices = await service.get_live_stock_prices(tickers)
        
        assert "RELIANCE.NS" in prices
        assert prices["RELIANCE.NS"]["price"] == 2550.0
        assert prices["RELIANCE.NS"]["previous_price"] == 2500.0
        assert prices["RELIANCE.NS"]["change_percent"] == 2.0  # (2550-2500)/2500 * 100
    
    @pytest.mark.asyncio
    @patch('yfinance.download')
    async def test_get_live_stock_prices_multiple_tickers(self, mock_yf_download):
        """Test fetching live prices for multiple tickers"""
        # Mock yfinance response for multiple tickers
        mock_data = pd.DataFrame({
            ('RELIANCE.NS', 'Close'): [2500.0, 2550.0],
            ('RELIANCE.NS', 'Volume'): [1000000, 1200000],
            ('INFY.NS', 'Close'): [1400.0, 1420.0],
            ('INFY.NS', 'Volume'): [800000, 900000]
        })
        mock_data.columns = pd.MultiIndex.from_tuples(mock_data.columns)
        mock_yf_download.return_value = mock_data
        
        service = MarketDataService()
        tickers = ["RELIANCE.NS", "INFY.NS"]
        
        prices = await service.get_live_stock_prices(tickers)
        
        assert len(prices) == 2
        assert "RELIANCE.NS" in prices
        assert "INFY.NS" in prices
        assert prices["RELIANCE.NS"]["price"] == 2550.0
        assert prices["INFY.NS"]["price"] == 1420.0
    
    @pytest.mark.asyncio
    async def test_get_live_stock_prices_empty_tickers(self):
        """Test fetching prices with empty ticker list"""
        service = MarketDataService()
        
        prices = await service.get_live_stock_prices([])
        assert prices == {}
        
        prices = await service.get_live_stock_prices([None, "", None])
        assert prices == {}
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_get_nav_from_amfi_success(self, mock_requests_get):
        """Test successful NAV fetch from AMFI"""
        # Mock AMFI response
        mock_response = MagicMock()
        mock_response.text = """
Scheme Code;ISIN Div Payout/ ISIN Growth;ISIN Div Reinvestment;Scheme Name;Net Asset Value;Date
120503;INE123A01012;INE123A01013;Test Mutual Fund;45.67;15-Jan-2024
120504;INE124A01012;INE124A01013;Another Fund;50.12;15-Jan-2024
"""
        mock_requests_get.return_value = mock_response

        service = MarketDataService()
        nav = await service.get_nav_from_amfi("120503")

        assert nav is not None
        assert nav["scheme_code"] == "120503"
        assert nav["scheme_name"] == "Test Mutual Fund"
        assert nav["nav"] == 45.67
        assert nav["date"] == "15-Jan-2024"