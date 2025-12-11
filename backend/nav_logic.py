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

def get_latest_nav(scheme_code, limit=1):
    """
    Fetches the latest official NAV from mfapi.in
    Returns a list of dicts (up to `limit`).
    """
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "SUCCESS":
                nav_data = data["data"]
                if nav_data:
                    # Get the most recent NAVs
                    recent = nav_data[:limit]
                    results = []
                    for item in recent:
                         results.append({
                            "date": item["date"],
                            "nav": float(item["nav"]),
                            "meta": data["meta"]
                         })
                    return results if limit > 1 else results[0]
    except Exception as e:
        print(f"Error fetching NAV for {scheme_code}: {e}")
    return [] if limit > 1 else None

def get_nav_at_date(scheme_code, target_date_str):
    """
    Fetches NAV for a specific date (DD-MM-YYYY).
    If exact date is missing (weekend/holiday), returns the last available NAV.
    Returns: tuple (nav_value, actual_date_str) or None
    """
    try:
        url = f"https://api.mfapi.in/mf/{scheme_code}"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "SUCCESS":
                nav_data = data["data"]
                
                # Parse target date
                try:
                    target_date = datetime.strptime(target_date_str, "%d-%m-%Y")
                except ValueError:
                    # Try YYYY-MM-DD fallback just in case
                     target_date = datetime.strptime(target_date_str, "%Y-%m-%d")

                # Iterate to find the first date <= target_date
                # API data is sorted by date DESC (newest first)
                for entry in nav_data:
                    entry_date_str = entry["date"]
                    entry_nav = float(entry["nav"])
                    
                    try:
                        entry_date = datetime.strptime(entry_date_str, "%d-%m-%Y")
                        
                        if entry_date <= target_date:
                            # Found the nearest valid date
                            if entry_date != target_date:
                                # Optional: log if needed
                                pass
                            return (entry_nav, entry_date_str)
                            
                    except ValueError:
                        continue

    except Exception as e:
        print(f"Error fetching historical NAV: {e}")            
    return None

def calculate_pnl(fund_id, user_id, investment=None, input_date=None):
    """
    Calculates P&L based on Investment Amount and Date.
    """
    doc = get_holdings(fund_id, user_id)
    if not doc:
        return {"error": "Fund not found."}
    
    fund_name = doc.get("fund_name", "Unknown Fund")
    
    scheme_code = doc.get("scheme_code")
    if not scheme_code:
        # Try to infer scheme code if missing (optional future step)
        return {"error": "Scheme Code missing for this fund."}

    # 1. Get Official NAV (Yesterday's Close + Previous)
    recent_navs = get_latest_nav(scheme_code, limit=2)
    
    if not recent_navs or len(recent_navs) == 0:
        return {"error": "Could not fetch current official NAV."}
    
    current_data = recent_navs[0]
    prev_official_data = recent_navs[1] if len(recent_navs) > 1 else None
    
    official_nav = current_data["nav"]
    nav_date = current_data["date"]
    current_nav = official_nav # Default
    
    # Use stored values if not provided
    if not investment or not input_date:
        if not doc.get("invested_amount") or not doc.get("invested_date"):
             return {"error": "Investment details not found. Please re-upload portfolio."}
        investment = float(doc.get("invested_amount"))
        input_date = doc.get("invested_date")
    
    # ---------------- LIVE NAV ESTIMATION ----------------
    live_nav_note = ""
    is_live = False
    
    # Check if we have holdings to verify against
    if doc and "holdings" in doc:
        holdings = doc["holdings"]
        
        total_pchange_contribution = 0.0
        total_weight_checked = 0.0
        stocks_checked = 0
        
        # We need a session cache for speed, already global `session`
        
        print(f"Calculating Live NAV for {fund_name} with {len(holdings)} holdings...")
        
        start_time = time.time()
        
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
        
        # If we successfully checked a significant portion of portfolio (e.g. > 0.5 weight)
        if total_weight_checked > 0.5:
             # Normalize contribution if total weight < 100 (e.g. cash component)
             # Portfolio Change % = Sum(Weight * StockChange) / TotalWeight
             portfolio_change = total_pchange_contribution / total_weight_checked
             
             # Live NAV = Official NAV * (1 + Change%)
             live_nav = official_nav * (1 + (portfolio_change / 100.0))
             
             current_nav = live_nav
             is_live = True
             elapsed = time.time() - start_time
             live_nav_note = f" | Live Est: {current_nav:.4f} ({portfolio_change:+.2f}%) based on {stocks_checked} stocks ({elapsed:.2f}s)"
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
            
            hist_result = get_nav_at_date(scheme_code, api_date_str)
            if hist_result:
                hist_nav, actual_date = hist_result
                purchase_nav = hist_nav
                if actual_date != api_date_str:
                     purchase_note = f"NAV on {actual_date} (adj from {api_date_str})"
                else:
                     purchase_note = f"NAV on {actual_date}"
            else:
                 purchase_note = f"NAV missing for {api_date_str}"
        except Exception as e:
            print(f"Date parse error: {e}")

    # 3. Calculate Total PnL
    units = float(investment) / purchase_nav
    current_value = units * current_nav
    pnl = current_value - float(investment)
    pnl_pct = (pnl / float(investment)) * 100
    
    # 4. Calculate Daily PnL
    # Logic:
    # - If Live: DayChange = LiveNAV - OfficialNAV(Yesterday)
    # - If Not Live: DayChange = OfficialNAV(Today) - OfficialNAV(Yesterday)
    #   (Note: If OfficialNAV(Today) is actually Yesterday's because today isn't out, 
    #    then we need OfficialNAV(Yesterday) - OfficialNAV(DayBefore))
    
    day_pnl = 0.0
    day_pnl_pct = 0.0
    
    # Reference NAV is the baseline to compare 'current_nav' against.
    # Usually it is the Previous Official Close.
    reference_nav_data = prev_official_data
    
    # Edge case: If current_data is NOT today (e.g. today is Monday, current_data is Friday), 
    # AND we are NOT live, then 'current_nav' is Friday's close.
    # We want Friday's Change -> Friday - Thursday.
    # So reference is indeed prev_official_data (Thursday).
    
    # Edge case: If we ARE live (Monday mid-day), current_nav is Live Est.
    # We compare against Friday's Close (current_data).
    
    reference_nav = 0.0
    
    if is_live:
        # Live Est vs Last Official Close
        reference_nav = official_nav
    else:
        # Latest Official vs Previous Official
        if prev_official_data:
            reference_nav = prev_official_data["nav"]
        else:
            reference_nav = official_nav # No history, 0 change
            
    if reference_nav > 0:
        day_change_per_unit = current_nav - reference_nav
        day_pnl = day_change_per_unit * units
        day_pnl_pct = (day_change_per_unit / reference_nav) * 100
        
    final_note = purchase_note + (live_nav_note if is_live else f" | Official NAV ({nav_date})")

    return {
        "fund_id": fund_id,
        "fund_name": fund_name,
        "invested_amount": investment,
        "invested_date": input_date,
        "units": round(units, 4),
        "purchase_nav": purchase_nav,
        "current_nav": round(current_nav, 4),
        "current_value": round(current_value, 2),
        "pnl": round(pnl, 2),
        "pnl_pct": round(pnl_pct, 2),
        "day_pnl": round(day_pnl, 2),
        "day_pnl_pct": round(day_pnl_pct, 2),
        "last_updated": "Live" if is_live else nav_date,
        "note": final_note,
        "nickname": doc.get("nickname")
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

def save_holdings_to_mongo(fund_name, excel_file, user_id, scheme_code=None, invested_amount=None, invested_date=None, nickname=None):
    # 1. Read Excel without headers first to find the header row
    try:
        # Read full file to find header
        df_raw = pd.read_excel(excel_file.file, header=None)
    except Exception as e:
         return {"error": f"Failed to read Excel: {str(e)}"}

    # 2. Find the row that contains 'ISIN'
    header_idx = None
    for idx, row in df_raw.iterrows():
        # Check if 'ISIN' is in this row (case insensitive conversion for safety)
        row_str = row.astype(str).str.upper().tolist()
        # Look for "ISIN" or "ISIN CODE" or "ISIN NO"
        # We check if any cell in the row *contains* "ISIN" as a distinct word or matches closely
        if any(x.strip() in ["ISIN", "ISIN CODE", "ISIN NO", "ISIN NUMBER"] for x in row_str if isinstance(x, str)):
            header_idx = idx
            break
    
    if header_idx is None:
        # Fallback: check if ANY cell contains "ISIN" substring
        for idx, row in df_raw.iterrows():
             row_str = row.astype(str).str.upper().tolist()
             if any("ISIN" in x for x in row_str if isinstance(x, str)):
                 header_idx = idx
                 break

    if header_idx is None:
        return {"error": "Could not find 'ISIN' column header in the file."}
    
    # 3. Reload with correct header
    excel_file.file.seek(0)
    df = pd.read_excel(excel_file.file, header=header_idx)
    
    # 4. Normalize columns
    col_map = {}
    for col in df.columns:
        c = str(col).strip()
        c_upper = c.upper()
        
        if "ISIN" in c_upper: 
            col_map[col] = "ISIN"
        elif "NAME" in c_upper and "INSTRUMENT" in c_upper: 
            col_map[col] = "Name"
        elif "%" in c and "NAV" in c: 
            col_map[col] = "Weight"
        elif "%" in c and "ASSET" in c_upper: 
            col_map[col] = "Weight" # Backup
    
    df = df.rename(columns=col_map)
    
    # Basic Validation
    if "ISIN" not in df.columns or "Weight" not in df.columns:
        return {"error": f"Missing required columns (ISIN, Weight). Found: {df.columns.tolist()}"}
    
    # 5. Clean and Filter Data
    
    # Drop rows where ISIN is NaN (removes headers/footers/empty lines)
    df = df.dropna(subset=["ISIN"])
    
    # Clean ISIN
    df["ISIN"] = df["ISIN"].astype(str).str.strip().str.upper()
    # Filter valid ISINs (Length 12 and alphanumeric)
    # Regex: ^[A-Z0-9]{12}$
    df = df[df["ISIN"].str.match(r'^[A-Z0-9]{12}$', na=False)]
    
    # Remove duplicates (keep first occurrence)
    df = df.drop_duplicates(subset=["ISIN"], keep="first")
    
    # Clean Weight
    # Convert "5.45%" string to 5.45 float
    def clean_weight(val):
        try:
            if pd.isna(val): return 0.0
            s = str(val).strip().replace("%", "")
            return float(s)
        except:
            return 0.0

    df["Weight"] = df["Weight"].apply(clean_weight)
    
    # 6. Map ISIN to Ticker
    # Optimization: Load NSE CSV once
    nse_source = load_nse_csv()
    
    holdings_list = []
    unresolved = []
    
    for _, row in df.iterrows():
        isin = row["ISIN"]
        name = row.get("Name", "Unknown")
        weight = float(row["Weight"])
        
        if weight <= 0:
            continue
            
        # Try to resolve Ticker using pre-loaded table
        ticker = isin_to_symbol_nse(isin, nse_table=nse_source)
        
        if ticker:
            holdings_list.append({
                "ISIN": isin,
                "Name": name,
                "Symbol": ticker,
                "Weight": weight
            })
        else:
            unresolved.append(f"{name} ({isin})")
            # print(f"Skipping {name} ({isin}): Could not resolve Ticker.")
            
    if not holdings_list:
         err_msg = "No valid holdings resolved."
         if unresolved:
             err_msg += f" Unresolved items: {', '.join(unresolved[:5])}..."
         return {"error": err_msg}

    # 7. Save to DB
    save_holdings(fund_name, holdings_list, user_id, scheme_code, invested_amount, invested_date, nickname)

    return {
        "message": f"Holdings saved for {fund_name}",
        "count": len(holdings_list),
        "unresolved_count": len(unresolved),
        "unresolved_samples": unresolved[:5]
    }





