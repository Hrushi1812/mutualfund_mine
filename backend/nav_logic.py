import time
import requests
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

from db import get_holdings, save_holdings

def get_latest_nav(scheme_code):
    """
    Fetches the latest official NAV from mfapi.in
    """
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "SUCCESS":
                nav_data = data["data"]
                if nav_data:
                    # Get the most recent NAV
                    latest = nav_data[0]
                    return {
                        "date": latest["date"],
                        "nav": float(latest["nav"]),
                        "meta": data["meta"]
                    }
    except Exception as e:
        print(f"Error fetching NAV for {scheme_code}: {e}")
    return None

def get_ticker_from_isin(isin):
    """
    Resolves ISIN to Yahoo Finance Ticker
    """
    try:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={isin}&quotesCount=1&newsCount=0"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        data = r.json()
        if 'quotes' in data and len(data['quotes']) > 0:
            return data['quotes'][0]['symbol']
    except Exception as e:
        print(f"Failed to resolve ISIN {isin}: {e}")
    return None

def save_holdings_to_mongo(fund_name, excel_file, scheme_code=None):
    # 1. Read Excel without headers first to find the header row
    try:
        df_raw = pd.read_excel(excel_file.file, header=None)
    except Exception as e:
         return {"error": f"Failed to read Excel: {str(e)}"}

    # 2. Find the row that contains 'ISIN'
    header_idx = None
    for idx, row in df_raw.iterrows():
        # Check if 'ISIN' is in this row (case insensitive conversion for safety)
        row_str = row.astype(str).str.upper().tolist()
        if "ISIN" in row_str:
            header_idx = idx
            break
    
    if header_idx is None:
        return {"error": "Could not find 'ISIN' column header in the file."}
    
    # 3. Reload with correct header
    excel_file.file.seek(0)
    df = pd.read_excel(excel_file.file, header=header_idx)
    
    # 4. Normalize columns
    # We expect columns like "ISIN", "Name of the Instrument", "% to NAV"
    
    # Map typical columns to our standard names
    col_map = {}
    for col in df.columns:
        c = str(col).strip()
        if "ISIN" in c: col_map[col] = "ISIN"
        elif "Name" in c and "Instrument" in c: col_map[col] = "Name"
        elif "%" in c and "NAV" in c: col_map[col] = "Weight"
        elif "%" in c and "Asset" in c: col_map[col] = "Weight" # Backup
    
    df = df.rename(columns=col_map)
    
    # Basic Validation
    if "ISIN" not in df.columns or "Weight" not in df.columns:
        return {"error": f"Missing required columns. Found: {df.columns.tolist()}"}
    
    # 5. Filter valid rows (exclude sub-headers like "Equity...")
    # Valid ISINs usually start with "INE" or "INF" and are length 12
    df = df.dropna(subset=["ISIN"])
    df["ISIN"] = df["ISIN"].astype(str).str.strip()
    df = df[df["ISIN"].str.len() == 12] # Filter for valid ISIN length
    
    # 6. Map ISIN to Ticker
    # This can be slow loop. In production, we'd parallelize or cache.
    # For now, we loop.
    holdings_list = []
    
    for _, row in df.iterrows():
        isin = row["ISIN"]
        name = row.get("Name", "Unknown")
        weight = row["Weight"]
        
        # Try to resolve Ticker
        ticker = get_ticker_from_isin(isin)
        
        # Fallback: If ticker not found, maybe try appending .NS to name? (Risky)
        # Or just log it.
        # If we can't find ticker, we can't track it.
        
        if ticker:
            holdings_list.append({
                "ISIN": isin,
                "Name": name,
                "Symbol": ticker,
                "Weight": weight
            })
        else:
            print(f"Skipping {name} ({isin}): Could not resolve Ticker.")
            
    if not holdings_list:
        return {"error": "No valid holdings could be resolved to tickers."}

    # 7. Save to DB
    save_holdings(fund_name, holdings_list, scheme_code)

    return {
        "message": f"Holdings saved for {fund_name}",
        "count": len(holdings_list),
        "unresolved_count": len(df) - len(holdings_list)
    }


def estimate_nav(fund_name, investment, input_date=None):
    """
    Estimator V2:
    - Fetches holdings from DB
    - Fetches Official NAV from API (using stored scheme_code)
    - calculated Real-time change
    """
    doc = get_holdings(fund_name)
    if not doc or "holdings" not in doc:
        return {"error": "Fund not found. Please upload holdings first."}
    
    holdings = doc["holdings"]
    scheme_code = doc.get("scheme_code")
    
    if not scheme_code:
        return {"error": "Scheme Code not found. Please re-upload with Scheme Code."}

    # 1. Get Base NAV
    nav_data = get_latest_nav(scheme_code)
    if not nav_data:
        return {"error": "Could not fetch official NAV. Check internet or Scheme Code."}
    
    prev_nav = nav_data["nav"]
    nav_date = nav_data["date"] # String DD-MM-YYYY

    # 2. Batch Download Live Prices
    symbols = [h["Symbol"] for h in holdings]
    
def get_nav_at_date(scheme_code, target_date_str):
    """
    Fetches NAV for a specific date (DD-MM-YYYY)
    """
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "SUCCESS":
                nav_data = data["data"]
                # Linear search or Dictionary lookup (more efficient)
                # API returns list sorted by date desc usually.
                for entry in nav_data:
                    if entry["date"] == target_date_str:
                        return float(entry["nav"])
    except Exception as e:
        print(f"Error fetching historical NAV: {e}")
    return None

def estimate_nav(fund_name, investment, input_date=None):
    """
    Estimator V3:
    - Fetches holdings from DB
    - Fetches Base NAV (Yesterday) for Estimation
    - Fetches Historical NAV (Investment Date) for Unit Calculation
    - calculated Real-time change
    """
    doc = get_holdings(fund_name)
    if not doc or "holdings" not in doc:
        return {"error": "Fund not found. Please upload holdings first."}
    
    holdings = doc["holdings"]
    scheme_code = doc.get("scheme_code")
    
    if not scheme_code:
        return {"error": "Scheme Code not found. Please re-upload with Scheme Code."}

    # 1. Get Base NAV (for today's projection)
    nav_data = get_latest_nav(scheme_code)
    if not nav_data:
        return {"error": "Could not fetch official NAV. Check internet or Scheme Code."}
    
    base_nav = nav_data["nav"]
    base_nav_date = nav_data["date"] # String DD-MM-YYYY

    # 2. Batch Download Live Prices
    symbols = [h["Symbol"] for h in holdings]
    
    try:
        tickers_str = " ".join(symbols)
        data = yf.download(tickers_str, period="5d", progress=False)
        closes = data["Close"]
    except Exception as e:
        return {"error": f"Failed to fetch stock data: {str(e)}"}

    total_weighted_return = 0.0
    
    # 3. Calculate Portfolio Change
    for h in holdings:
        sym = h["Symbol"]
        weight = h["Weight"]
        pct_change = 0.0
        try:
            if isinstance(closes, pd.DataFrame) and sym in closes.columns:
                series = closes[sym].dropna()
            elif isinstance(closes, pd.Series) and symbols[0] == sym:
                series = closes.dropna()
            else:
                series = []

            if len(series) >= 2:
                prev_close = float(series.iloc[-2])
                last_price = float(series.iloc[-1])
                pct_change = ((last_price - prev_close) / prev_close) * 100
        except Exception:
            pct_change = 0.0
            
        total_weighted_return += (weight * pct_change) / 100
        
    # 4. Final Estimation of NAV
    estimated_nav = base_nav * (1 + total_weighted_return / 100)
    
    # 5. Units Calculation
    purchase_nav = base_nav 
    note = "Assuming fresh investment (Yesterday's NAV)."
    
    if input_date:
        # Expected format: YYYY-MM-DD from frontend, but API needs DD-MM-YYYY
        try:
            d_obj = datetime.strptime(input_date, "%Y-%m-%d")
            api_date_str = d_obj.strftime("%d-%m-%Y")
            
            hist_nav = get_nav_at_date(scheme_code, api_date_str)
            if hist_nav:
                purchase_nav = hist_nav
                note = f"Units calculated using NAV on {api_date_str} (₹{purchase_nav})"
            else:
                note = f"NAV not found for {api_date_str}. Used Base NAV."
        except Exception as e:
            note = f"Date error: {e}. Used Base NAV."

    units = investment / purchase_nav
    current_value = units * estimated_nav
    pnl = current_value - investment
    pnl_pct = (pnl / investment) * 100

    return {
        "fund_name": fund_name,
        "base_nav_date": base_nav_date,
        "base_nav": base_nav,
        "estimated_nav": round(estimated_nav, 4),
        "day_change_pct": round(total_weighted_return, 2),
        "units": round(units, 2),
        "est_value": round(current_value, 2),
        "pnl": round(pnl, 2),
        "pnl_percentage": round(pnl_pct, 2),
        "Note": note
    }

