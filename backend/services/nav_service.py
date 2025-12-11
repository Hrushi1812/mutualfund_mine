from datetime import datetime
import time
import requests
from services.holdings_service import holdings_service, session

class NavService:
    @staticmethod
    def get_live_price_change(symbol):
        base = "https://www.nseindia.com"
        api = base + "/api/quote-equity"
        try:
            # Prime cookies if needed (session is shared)
            # session.get(base, timeout=5) 
            r = session.get(api, params={"symbol": symbol}, timeout=10)
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
        try:
            url = f"https://api.mfapi.in/mf/{scheme_code}"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "SUCCESS":
                    nav_data = data["data"]
                    try:
                        target_date = datetime.strptime(target_date_str, "%d-%m-%Y")
                    except ValueError:
                         target_date = datetime.strptime(target_date_str, "%Y-%m-%d")

                    for entry in nav_data:
                        entry_date_str = entry["date"]
                        try:
                            entry_date = datetime.strptime(entry_date_str, "%d-%m-%Y")
                            if entry_date <= target_date:
                                return (float(entry["nav"]), entry_date_str)
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

        # 1. Get Official NAV
        recent_navs = NavService.get_latest_nav(scheme_code, limit=2)
        if not recent_navs or len(recent_navs) == 0:
            return {"error": "Could not fetch current official NAV."}
        
        current_data = recent_navs[0]
        prev_official_data = recent_navs[1] if len(recent_navs) > 1 else None
        
        official_nav = current_data["nav"]
        nav_date = current_data["date"]
        current_nav = official_nav 
        
        # Use stored values if not provided
        if not investment or not input_date:
            if not doc.get("invested_amount") or not doc.get("invested_date"):
                 return {"error": "Investment details not found."}
            investment = float(doc.get("invested_amount"))
            input_date = doc.get("invested_date")
        
        # Live NAV Estimation
        live_nav_note = ""
        is_live = False
        
        if doc and "holdings" in doc:
            holdings = doc["holdings"]
            total_pchange_contribution = 0.0
            total_weight_checked = 0.0
            stocks_checked = 0
            
            # Check a few distinct holdings to see if market is moving? 
            # Simplified for speed: Check all if not too many, or sample?
            # Original logic checked all.
            for stock in holdings:
                symbol = stock.get("Symbol")
                weight = stock.get("Weight", 0)
                if symbol and weight > 0:
                    pct = NavService.get_live_price_change(symbol)
                    if pct is not None:
                        total_pchange_contribution += (weight * pct)
                        total_weight_checked += weight
                        stocks_checked += 1
            
            if total_weight_checked > 0.5:
                 portfolio_change = total_pchange_contribution / total_weight_checked
                 live_nav = official_nav * (1 + (portfolio_change / 100.0))
                 current_nav = live_nav
                 is_live = True
                 live_nav_note = f" | Live Est: {current_nav:.4f} ({portfolio_change:+.2f}%)"

        # Purchase NAV
        purchase_nav = current_nav
        purchase_note = "Used Current NAV"
        if input_date:
            try:
                # API format DD-MM-YYYY
                d_obj = datetime.strptime(input_date, "%Y-%m-%d")
                api_date_str = d_obj.strftime("%d-%m-%Y")
                hist_result = NavService.get_nav_at_date(scheme_code, api_date_str)
                if hist_result:
                    purchase_nav, actual_date = hist_result
                    if actual_date != api_date_str:
                         purchase_note = f"NAV on {actual_date} (adj from {api_date_str})"
                    else:
                         purchase_note = f"NAV on {actual_date}"
            except: pass

        # Calculations
        units = float(investment) / purchase_nav
        current_value = units * current_nav
        pnl = current_value - float(investment)
        pnl_pct = (pnl / float(investment)) * 100
        
        day_pnl = 0.0
        day_pnl_pct = 0.0
        
        reference_nav = prev_official_data["nav"] if prev_official_data else official_nav
        if is_live: reference_nav = official_nav
        
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

nav_service = NavService()
