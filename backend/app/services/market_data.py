import yfinance as yf
import requests
from typing import Dict, List, Optional
from datetime import datetime, date
import logging

logger = logging.getLogger(__name__)

class MarketDataService:
    
    def __init__(self):
        self.amfi_base_url = "https://www.amfiindia.com"
    
    async def get_live_stock_prices(self, tickers: List[str]) -> Dict[str, Dict]:
        if not tickers:
            return {}
        valid_tickers = list(set([t for t in tickers if t]))
        if not valid_tickers:
            return {}
        tickers_str = " ".join(valid_tickers)
        data = yf.download(tickers_str, period="2d", interval="1d", group_by="ticker", progress=False)
        results = {}
        if len(valid_tickers) == 1:
            ticker = valid_tickers[0]
            if not data.empty and len(data) >= 2:
                current_price = data['Close'].iloc[-1]
                previous_price = data['Close'].iloc[-2]
                change_percent = ((current_price - previous_price) / previous_price) * 100
                results[ticker] = {
                    'price': float(current_price),
                    'previous_price': float(previous_price),
                    'change_percent': float(change_percent),
                    'volume': float(data['Volume'].iloc[-1]) if 'Volume' in data else 0,
                    'timestamp': datetime.now()
                }
        else:
            for ticker in valid_tickers:
                try:
                    ticker_data = data[ticker]
                    if not ticker_data.empty and len(ticker_data) >= 2:
                        current_price = ticker_data['Close'].iloc[-1]
                        previous_price = ticker_data['Close'].iloc[-2]
                        change_percent = ((current_price - previous_price) / previous_price) * 100
                        results[ticker] = {
                            'price': float(current_price),
                            'previous_price': float(previous_price),
                            'change_percent': float(change_percent),
                            'volume': float(ticker_data['Volume'].iloc[-1]) if 'Volume' in ticker_data else 0,
                            'timestamp': datetime.now()
                        }
                except Exception as e:
                    logger.error(f"Error fetching data for ticker {ticker}: {str(e)}")
                    results[ticker] = None
        return results
    
    async def get_nav_from_amfi(self, scheme_code: str, nav_date: date = None) -> Optional[float]:
        if nav_date is None:
            nav_date = date.today()
        date_str = nav_date.strftime("%d-%m-%Y")
        url = f"{self.amfi_base_url}/spages/NAVAll.txt"
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            lines = response.text.split('\n')
            for line in lines:
                if scheme_code in line:
                    parts = line.split(';')
                    if len(parts) >= 5:
                        nav_value = parts[4].strip()
                        try:
                            return float(nav_value)
                        except ValueError:
                            continue
            logger.warning(f"NAV not found for scheme code {scheme_code} on date {date_str}")
            return None
        except Exception as e:
            logger.error(f"Error fetching NAV from AMFI: {str(e)}")
            return None
    
    async def calculate_portfolio_nav(self, holdings: List[Dict], previous_nav: float) -> float:
        if not holdings:
            return previous_nav
        tickers = [h.get('ticker') for h in holdings if h.get('ticker')]
        if not tickers:
            return previous_nav
        price_data = await self.get_live_stock_prices(tickers)
        total_weight = 0
        weighted_return = 0
        for holding in holdings:
            ticker = holding.get('ticker')
            weight = holding.get('percentage_to_nav', 0) / 100
            if ticker and ticker in price_data and price_data[ticker]:
                change_percent = price_data[ticker]['change_percent']
                weighted_return += weight * (change_percent / 100)
                total_weight += weight
        if total_weight > 0:
            estimated_nav = previous_nav * (1 + weighted_return)
            return max(estimated_nav, 0)
        return previous_nav