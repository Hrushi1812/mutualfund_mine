from datetime import datetime, date
import time
import requests
from services.holdings_service import holdings_service, session
from utils.date_utils import is_market_open, get_current_ist_time, is_trading_day, get_previous_business_day, format_date_for_api, parse_date_from_str, MARKET_OPEN_TIME
from utils.common import NSE_API_URL

class NavService:
    @staticmethod
    def get_live_price_change(symbol):
        """Fetches live P-Change from NSE."""
        try:
            r = session.get(NSE_API_URL, params={"symbol": symbol}, timeout=5)
            if "application/json" not in r.headers.get("Content-Type", ""): return None
            data = r.json()
            return float(data["priceInfo"]["pChange"])
        except: return None

    @staticmethod
    def get_latest_nav(scheme_code, limit=1):
        try:
            url = f"https://api.mfapi.in/mf/{scheme_code}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "SUCCESS":
                    nav_data = data["data"]
                    if nav_data:
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

    @staticmethod
    def get_nav_at_date(scheme_code, target_date_str):
        """
        Robustly finds NAV for a target date. 
        If date x is missing, it searches backwards for the nearest previous NAV.
        """
        try:
            url = f"https://api.mfapi.in/mf/{scheme_code}"
            response = requests.get(url) 
            if response.status_code != 200: return None
            
            data = response.json()
            if data.get("status") != "SUCCESS": return None

            target_date = parse_date_from_str(target_date_str)
            nav_data = data["data"]
            
            # nav_data is sorted DESC (newest first)
            for entry in nav_data:
                try:
                    entry_date = datetime.strptime(entry["date"], "%d-%m-%Y")
                    # If we found a date ON or BEFORE target
                    if entry_date <= target_date:
                        return (float(entry["nav"]), entry["date"])
                except ValueError: continue
                
        except Exception as e:
            print(f"Error fetching historical NAV: {e}")            
        return None

    @staticmethod
    def calculate_pnl(fund_id, user_id, investment=None, input_date=None):
        doc = holdings_service.get_holdings(fund_id, user_id)
        if not doc: return {"error": "Fund not found."}
        
        fund_name = doc.get("fund_name", "Unknown Fund")
        scheme_code = doc.get("scheme_code")
        if not scheme_code: return {"error": "Scheme Code missing for this fund."}

        # --- 1. Determine Effective Date & NAV Logic ---
        # Goal: Find the "Current" NAV. 
        # If Market Open: Estimate Live NAV.
        # If Market Closed (Evening): Expect Close NAV (might not be out yet).
        # If Weekend: Expect Friday's NAV.
        
        now = get_current_ist_time()
        market_open = is_market_open(now)
        today_is_trading = is_trading_day(now)
        
        # Fetch Top 5 NAVs to be safe
        recent_navs = NavService.get_latest_nav(scheme_code, limit=5)
        if not recent_navs: return {"error": "Could not fetch NAV history."}
        
        latest_official = recent_navs[0]
        latest_nav_val = latest_official["nav"]
        latest_nav_date_str = latest_official["date"]
        
        # Check if latest NAV is fresh (Today's)
        try:
            latest_nav_date = datetime.strptime(latest_nav_date_str, "%d-%m-%Y").date()
        except:
            latest_nav_date = date(2000, 1, 1)

        # Decide if we should estimate
        should_estimate = False
        
        if market_open:
            should_estimate = True
        elif today_is_trading and (latest_nav_date < now.date()):
            # Market Closed, but valid trading day and official NAV is not out yet.
            if now.time() >= MARKET_OPEN_TIME:
                 should_estimate = True
        
        # Calculate P&L baseline
        current_nav = latest_nav_val
        is_live_estimated = False
        live_note = ""

        # TRY LIVE ESTIMATION
        if should_estimate and doc.get("holdings"):
            holdings = doc["holdings"]
            total_prod = 0.0
            total_wt = 0.0
            stocks_checked = 0
            
            for stock in holdings:
                sym = stock.get("Symbol")
                wt = stock.get("Weight", 0)
                if sym and wt > 0:
                    pct = NavService.get_live_price_change(sym)
                    if pct is not None:
                        total_prod += (wt * pct)
                        total_wt += wt
                        stocks_checked += 1
            
            if total_wt > 0.5: # At least 0.5 weight checked
                # Assuming weight is 5.5 for 5.5%
                portfolio_change_pct = total_prod / total_wt
                estimated_nav = latest_nav_val * (1 + (portfolio_change_pct / 100))
                
                current_nav = estimated_nav
                is_live_estimated = True
                
                status_label = "Live Est" if market_open else "Est Close"
                live_note = f" | {status_label}: {current_nav:.4f} ({portfolio_change_pct:+.2f}%)"

        # --- 2. Historical NAV (Purchase Price) ---
        if not investment:
            investment = float(doc.get("invested_amount", 0))
        if not input_date:
            input_date = doc.get("invested_date")

        purchase_nav = current_nav # Default
        purchase_note = "Used Current NAV"

        if input_date:
            try:
                hist_res = NavService.get_nav_at_date(scheme_code, input_date)
                if hist_res:
                    purchase_nav, actual_date_str = hist_res
                    if actual_date_str != format_date_for_api(parse_date_from_str(input_date)):
                         purchase_note = f"NAV on {actual_date_str} (adj)"
                    else:
                         purchase_note = f"NAV on {actual_date_str}"
            except Exception: pass

        # --- 3. Compute Metrics ---
        if purchase_nav == 0: purchase_nav = 1 # prevent div/0
        
        units = investment / purchase_nav
        current_value = units * current_nav
        total_pnl = current_value - investment
        total_pnl_pct = (total_pnl / investment) * 100 if investment > 0 else 0

        # Day PnL
        # Valid Day Change = Current NAV - Previous Business Day Close
        # We need to find the "Reference Close"
        
        reference_nav = latest_nav_val # Default
        
        # If we are live, reference is the latest official close (basically yesterday)
        if is_live_estimated:
            reference_nav = latest_nav_val
        else:
            # If we are NOT live, we are looking at an Official NAV.
            # We want change from the *day before* that official NAV.
            # recent_navs[0] is Today (or latest), recent_navs[1] is Previous.
             if len(recent_navs) > 1:
                 reference_nav = recent_navs[1]["nav"]
        
        day_pnl = (current_nav - reference_nav) * units
        day_pnl_pct = ((current_nav - reference_nav) / reference_nav) * 100 if reference_nav > 0 else 0
        
        final_note = purchase_note + (live_note if is_live_estimated else f" | Official: {latest_nav_date_str}")

        return {
            "fund_id": fund_id,
            "fund_name": fund_name,
            "invested_amount": investment,
            "invested_date": input_date,
            "units": round(units, 4),
            "purchase_nav": purchase_nav,
            "current_nav": round(current_nav, 4),
            "current_value": round(current_value, 2),
            "pnl": round(total_pnl, 2),
            "pnl_pct": round(total_pnl_pct, 2),
            "day_pnl": round(day_pnl, 2),
            "day_pnl_pct": round(day_pnl_pct, 2),
            "last_updated": "Live" if is_live_estimated else latest_nav_date_str,
            "note": final_note,
            "nickname": doc.get("nickname")
        }

nav_service = NavService()
