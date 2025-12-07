import yfinance as yf
import requests

def get_ticker_from_isin(isin):
    print(f"Resolving ISIN: {isin}...")
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={isin}&quotesCount=1&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        if 'quotes' in data and len(data['quotes']) > 0:
            return data['quotes'][0]['symbol']
    except Exception as e:
        print(f"Error: {e}")
    return None

def test_daily_change(isin):
    # 1. Resolve Ticker
    ticker = get_ticker_from_isin(isin)
    if not ticker:
        print("Could not resolve ticker.")
        return

    print(f"Found Ticker: {ticker}")

    # 2. Get Data
    print(f"Fetching data for {ticker}...")
    data = yf.download(ticker, period="5d", progress=False)
    
    if len(data) < 2:
        print("Not enough data.")
        return

    # Handle yfinance multi-index columns if needed, though single ticker usually simple
    closes = data["Close"]
    
    # Get last 2 closes (Handling series)
    if not closes.empty:
         # If it's a DataFrame (new yfinance might verify)
        val_yesterday = float(closes.iloc[-2])
        val_today = float(closes.iloc[-1])
        
        change = ((val_today - val_yesterday) / val_yesterday) * 100
        
        print(f"Yesterday Close: {val_yesterday}")
        print(f"Today/Live Price: {val_today}")
        print(f"Daily Change: {change:.2f}%")
        
# Test with HDFC Bank (from your image)
test_daily_change("INE040A01034")
