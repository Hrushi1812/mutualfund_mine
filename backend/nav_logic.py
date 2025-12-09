from datetime import datetime, timedelta
import pandas as pd
import requests
import csv
import time
from io import StringIO

from db import get_holdings, save_holdings

# ---------------- NSE SESSION SETUP ----------------
NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json,text/html,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/"
}

session = requests.Session()
session.headers.update(NSE_HEADERS)

# ---------------- NSE HELPERS ----------------

def load_nse_csv():
    """
    Downloads and caches the NSE Equity Master List (CSV).
    """
    url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    try:
        r = session.get(url, timeout=20)
        # r.raise_for_status() # Optional: raise if 404/500
        f = StringIO(r.text)
        return list(csv.DictReader(f))
    except Exception as e:
        print(f"Error downloading NSE CSV: {e}")
        return []

def isin_to_symbol_nse(isin, nse_table=None):
    """
    Resolves ISIN to NSE Symbol using the Master CSV.
    Auto-detects columns for robustness.
    """
    if not nse_table:
        # If table not passed, load it on demand (caching recommended in prod)
        nse_table = load_nse_csv()
        
    if not nse_table:
        return None

    # Auto-detect headers from the first row keys
    headers = nse_table[0].keys()
    
    isin_col = None
    symbol_col = None

    for col in headers:
        key = col.strip().lower().replace(" ", "")
        if "isin" in key:
            isin_col = col
        if key in ["symbol", "tradingsymbol", "sc_symbol"]:
            symbol_col = col

    # Fallback for symbol
    if not symbol_col:
        for col in headers:
            if "symbol" in col.lower():
                symbol_col = col
                
    if not isin_col or not symbol_col:
        print(f"Column detection failed. Found: {list(headers)}")
        return None

    # Search
    for row in nse_table:
        if row.get(isin_col, "").strip() == isin:
            return row.get(symbol_col)
            
    return None

def get_live_price_change(symbol):
    """
    Fetches the live percent change from NSE.
    Returns float (e.g. 1.25 for +1.25%) or None.
    """
    base = "https://www.nseindia.com"
    api = base + "/api/quote-equity"

    try:
        # Prime cookies
        session.get(base, timeout=5)
        # time.sleep(0.5) # Short pause

        r = session.get(api, params={"symbol": symbol}, timeout=10)
        
        if "application/json" not in r.headers.get("Content-Type", ""):
            return None # Blocked or invalid response
            
        data = r.json()
        return float(data["priceInfo"]["pChange"])
    except Exception as e:
        # print(f"Error fetching price for {symbol}: {e}")
        return None

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

def calculate_pnl(fund_name, investment, input_date):
    """
    Calculates P&L based on Investment Amount and Date.
    """
    doc = get_holdings(fund_name)
    if not doc:
        return {"error": "Fund not found."}
    
    scheme_code = doc.get("scheme_code")
    if not scheme_code:
        # Try to infer scheme code if missing (optional future step)
        return {"error": "Scheme Code missing for this fund."}

    # 1. Get Official NAV (Yesterday's Close)
    current_data = get_latest_nav(scheme_code)
    if not current_data:
        return {"error": "Could not fetch current official NAV."}
    
    official_nav = current_data["nav"]
    nav_date = current_data["date"]
    current_nav = official_nav # Default
    
    # ---------------- LIVE NAV ESTIMATION ----------------
    live_nav_note = ""
    is_live = False
    
    # Check if we have holdings to verify against
    holdings_doc = get_holdings(fund_name)
    if holdings_doc and "holdings" in holdings_doc:
        holdings = holdings_doc["holdings"]
        
        total_pchange_contribution = 0.0
        total_weight_checked = 0.0
        stocks_checked = 0
        
        # We need a session cache for speed, already global `session`
        
        print(f"Calculating Live NAV for {fund_name} with {len(holdings)} holdings...")
        
        for stock in holdings:
            symbol = stock.get("Symbol")
            weight = stock.get("Weight", 0)
            
            if symbol and weight > 0:
                pct = get_live_price_change(symbol)
                if pct is not None:
                    # Weight is usually in %, e.g. 5.5 for 5.5%
                    # Contribution = 5.5 * 1.2% = 6.6
                    total_pchange_contribution += (weight * pct)
                    total_weight_checked += weight
                    stocks_checked += 1
                # Small delay to be polite to NSE
                # time.sleep(0.05) 
        
        # If we successfully checked a significant portion of portfolio (e.g. > 50% weight)
        if total_weight_checked > 50:
             # Normalize contribution if total weight < 100 (e.g. cash component)
             # Portfolio Change % = Sum(Weight * StockChange) / TotalWeight
             portfolio_change = total_pchange_contribution / total_weight_checked
             
             # Live NAV = Official NAV * (1 + Change%)
             live_nav = official_nav * (1 + (portfolio_change / 100.0))
             
             current_nav = live_nav
             is_live = True
             live_nav_note = f" | Live Est: {current_nav:.4f} ({portfolio_change:+.2f}%) based on {stocks_checked} stocks"
             print(live_nav_note)
        else:
             print(f"Skipping Live NAV: Only checked {total_weight_checked}% weight")

    # -----------------------------------------------------

    # 2. Get Historical NAV (Purchase Price)
    purchase_nav = current_nav # Default fallback for purchase if date missing
    purchase_note = "Used Current NAV"

    if input_date:
        try:
            # Input YYYY-MM-DD -> API DD-MM-YYYY
            d_obj = datetime.strptime(input_date, "%Y-%m-%d")
            api_date_str = d_obj.strftime("%d-%m-%Y")
            
            hist_nav = get_nav_at_date(scheme_code, api_date_str)
            if hist_nav:
                purchase_nav = hist_nav
                purchase_note = f"NAV on {api_date_str}"
            else:
                 purchase_note = f"NAV missing for {api_date_str}"
        except Exception as e:
            print(f"Date parse error: {e}")

    # 3. Calculate
    units = float(investment) / purchase_nav
    current_value = units * current_nav
    pnl = current_value - float(investment)
    pnl_pct = (pnl / float(investment)) * 100
    
    final_note = purchase_note + (live_nav_note if is_live else f" | Official NAV ({nav_date})")

    return {
        "fund_name": fund_name,
        "invested_amount": investment,
        "invested_date": input_date,
        "units": round(units, 4),
        "purchase_nav": purchase_nav,
        "current_nav": round(current_nav, 4),
        "current_value": round(current_value, 2),
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "last_updated": "Live" if is_live else nav_date,
        "note": final_note
    }

def search_scheme_code(query):
    """
    Searches for a Scheme Code by name if not provided.
    """
    try:
        url = f"https://api.mfapi.in/mf/search?q={query}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data and len(data) > 0:
                # Return the first match's schemeCode
                return str(data[0]["schemeCode"])
    except Exception as e:
        print(f"Search error: {e}")
    return None

def get_ticker_from_isin(isin):
    """
    Deprecated: Use isin_to_symbol_nse instead.
    Kept for backward compatibility if needed, but updated to use NSE logic.
    """
    return isin_to_symbol_nse(isin)

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
        # Try to resolve Ticker (pass table if optimized)
        # For now, we load CSV once per file upload? 
        # Better: load CSV once outside the loop
        if 'nse_table_cache' not in locals():
             nse_table_cache = load_nse_csv()
             
        ticker = isin_to_symbol_nse(isin, nse_table=nse_table_cache)
        
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





