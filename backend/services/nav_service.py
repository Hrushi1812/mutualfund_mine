from datetime import datetime, date, timedelta
import time
import requests
from services.holdings_service import holdings_service, session
from utils.date_utils import (
    is_market_open,
    get_current_ist_time,
    is_trading_day,
    get_previous_business_day,
    format_date_for_api,
    parse_date_from_str,
    MARKET_OPEN_TIME,
)
from utils.common import NSE_API_URL
from core.logging import get_logger

logger = get_logger("NavService")


class NavService:
    @staticmethod
    def get_live_price_change(symbol):
        """Fetches live P-Change from NSE for a symbol (expected symbol format e.g. 'RELIANCE')."""
        try:
            r = session.get(NSE_API_URL, params={"symbol": symbol}, timeout=5)
            content_type = r.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                logger.debug(f"NSE returned non-json for {symbol}: {content_type}")
                return None
            data = r.json()
            # defensive access
            price_info = data.get("priceInfo") or {}
            p_change = price_info.get("pChange")
            return float(p_change) if p_change is not None else None
        except Exception as e:
            logger.debug(f"get_live_price_change({symbol}) failed: {e}")
            return None

    @staticmethod
    def get_latest_nav(scheme_code, limit=1):
        """
        Returns a list of latest NAV entries (newest first).
        Each entry: {"date": "DD-MM-YYYY", "nav": float, "meta": ...}
        Always returns a list (empty if none).
        """
        try:
            url = f"https://api.mfapi.in/mf/{scheme_code}"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get("status") == "SUCCESS":
                    nav_data = data.get("data") or []
                    if nav_data:
                        # nav_data is usually newest-first; slice defensively
                        recent = nav_data[:limit]
                        results = []
                        for item in recent:
                            try:
                                results.append(
                                    {
                                        "date": item["date"],
                                        "nav": float(item["nav"]),
                                        "meta": data.get("meta"),
                                    }
                                )
                            except Exception:
                                continue
                        return results
        except Exception as e:
            logger.error(f"Error fetching NAV for {scheme_code}: {e}")
        return []

    @staticmethod
    def get_nav_at_date(scheme_code, target_date_str):
        """
        Robustly finds NAV for a target date (DD-MM-YYYY / YYYY-MM-DD / DD/MM/YYYY).
        If the exact date is missing, it finds the nearest previous NAV.
        Returns (nav_float, nav_date_str) or None.
        """
        try:
            url = f"https://api.mfapi.in/mf/{scheme_code}"
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return None

            data = response.json()
            if data.get("status") != "SUCCESS":
                return None

            target_date = parse_date_from_str(target_date_str).date()
            nav_data = data.get("data") or []

            # iterate through nav_data (assumed newest-first); find first entry <= target_date
            for entry in nav_data:
                try:
                    entry_date = datetime.strptime(entry["date"], "%d-%m-%Y").date()
                    if entry_date <= target_date:
                        return (float(entry["nav"]), entry["date"])
                except Exception:
                    continue
        except Exception as e:
            logger.error(f"Error fetching historical NAV for {scheme_code} date {target_date_str}: {e}")
        return None

    @staticmethod
    def calculate_portfolio_change(holdings):
        """
        Calculates the weighted average percent change (intraday live) of the portfolio using parallel fetching.
        We expect holdings to have "Symbol" and "Weight" (either fraction 0..1 or percent like 5.5).
        Returns weighted pct change (e.g., 1.23 for +1.23%) or None if insufficient coverage.
        """
        import concurrent.futures

        total_prod = 0.0
        total_wt = 0.0
        stocks_checked = 0

        # Filter valid stocks first
        valid_stocks = [s for s in holdings if s.get("Symbol") and s.get("Weight", 0) > 0]
        total_stocks = len(valid_stocks)
        if total_stocks == 0:
            return None

        logger.info(f"Starting live price fetch for {total_stocks} stocks...")
        start_time = time.time()

        def fetch_price(stock):
            sym = stock.get("Symbol")
            # normalize weight to fraction
            wt = float(stock.get("Weight", 0) or 0)
            if wt > 1:
                wt = wt / 100.0
            pct = NavService.get_live_price_change(sym)
            return (wt, pct)

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_stock = {executor.submit(fetch_price, stock): stock for stock in valid_stocks}
            for future in concurrent.futures.as_completed(future_to_stock):
                try:
                    wt, pct = future.result()
                    if pct is not None:
                        total_prod += (wt * pct)
                        total_wt += wt
                        stocks_checked += 1
                except Exception as exc:
                    logger.error(f"Stock fetch generated an exception: {exc}")

        duration = time.time() - start_time
        logger.info(f"Live fetch completed in {duration:.2f}s. Valid: {stocks_checked}/{total_stocks}")

        # require at least 50% of portfolio weight coverage
        if total_wt >= 0.5:
            # normalized weighted average percent change
            return total_prod / total_wt
        return None

    @staticmethod
    def ensure_yf_symbol(sym):
        """Ensure a yfinance-friendly ticker (adds .NS if missing and symbol likely NSE)."""
        if sym.upper().endswith(".NS") or sym.upper().endswith(".BO"):
            return sym
        return f"{sym}.NS"

    @staticmethod
    def get_historical_portfolio_change(holdings, target_date):
        """
        Calculates weighted average percent change for a specific historical date (target_date - a date object).
        Uses yfinance to fetch historical close prices and computes pct change for target_date = (close[t] - close[t-1]) / close[t-1] * 100.
        Returns weighted pct (e.g., 1.23 for +1.23%) or None if insufficient coverage.
        """
        import yfinance as yf
        import pandas as pd

        valid_stocks = [s for s in holdings if s.get("Symbol") and s.get("Weight", 0) > 0]
        if not valid_stocks:
            return None

        # Prepare tickers
        tickers_map = {}
        for s in valid_stocks:
            sym = s["Symbol"]
            yf_sym = NavService.ensure_yf_symbol(sym)
            tickers_map[sym] = yf_sym
        tickers_list = list(set(tickers_map.values()))

        try:
            # Fetch small window around target_date to get close[t-1] and close[t]
            start_date = target_date - timedelta(days=7)
            end_date = target_date + timedelta(days=2)  # yfinance end is exclusive, be generous
            logger.info(f"Fetching historical data for {len(tickers_list)} stocks via yfinance between {start_date} and {end_date}")

            data = yf.download(tickers_list, start=start_date, end=end_date, progress=False, threads=True, group_by='column')
            if data is None or data.empty:
                logger.warning("yfinance returned empty data")
                return None

            # 'Close' may be a DataFrame or a MultiIndex DataFrame depending on tickers count
            if "Close" in data:
                close_df = data["Close"]
            else:
                # data itself might be a simple DataFrame of Close if one ticker
                close_df = data

            # Ensure index is datetime
            close_df.index = pd.to_datetime(close_df.index)

            # Calculate percent change per ticker: (Close[t] - Close[t-1]) / Close[t-1] * 100
            pct_df = close_df.pct_change() * 100

            # Normalize target_date to date
            if isinstance(target_date, str):
                t_date = pd.to_datetime(target_date).date()
            else:
                t_date = target_date

            # Find index row that matches target_date
            idx_loc = None
            for idx in pct_df.index:
                if idx.date() == t_date:
                    idx_loc = idx
                    break

            if idx_loc is None:
                logger.warning(f"No yfinance pct row found for target date {t_date}")
                return None

            total_prod = 0.0
            total_wt = 0.0
            stocks_checked = 0

            for stock in valid_stocks:
                sym = stock["Symbol"]
                wt = float(stock.get("Weight", 0) or 0)
                if wt > 1:
                    wt = wt / 100.0

                yf_sym = tickers_map.get(sym)
                # column names may be just yf_sym or a tuple depending on df shape; handle simple case
                if yf_sym in pct_df.columns:
                    val = pct_df.loc[idx_loc, yf_sym]
                else:
                    # try uppercase fallback
                    found_col = next((c for c in pct_df.columns if str(c).upper() == yf_sym.upper()), None)
                    val = pct_df.loc[idx_loc, found_col] if found_col is not None else None

                if val is not None and not pd.isna(val):
                    total_prod += wt * float(val)
                    total_wt += wt
                    stocks_checked += 1

            logger.info(f"Historical fetch complete. Valid: {stocks_checked}/{len(valid_stocks)}")

            if total_wt >= 0.5:
                return total_prod / total_wt
        except Exception as e:
            logger.error(f"yfinance history fetch failed: {e}")

        return None

    @staticmethod
    def calculate_pnl(fund_id, user_id, investment=None, input_date=None):
        """
        Main entry: returns NAV, units, PnL, day PnL etc using the robust decision tree:
         - Prefer Official D0
         - Else Estimate D0 if we have D0 prices (live)
         - Else Use Official D-1
         - Else Estimate D-1 using historical closes
         - Else fallback to D-2...
        """
        doc = holdings_service.get_holdings(fund_id, user_id)
        if not doc:
            return {"error": "Fund not found."}

        fund_name = doc.get("fund_name", "Unknown Fund")
        scheme_code = doc.get("scheme_code")
        if not scheme_code:
            return {"error": "Scheme Code missing for this fund."}

        # --- dates setup ---
        now = get_current_ist_time()
        d0_date = now.date()
        d0_str = format_date_for_api(d0_date)

        d_minus_1_date = get_previous_business_day(d0_date)
        d_minus_1_str = format_date_for_api(d_minus_1_date)

        d_minus_2_date = get_previous_business_day(d_minus_1_date)
        d_minus_2_str = format_date_for_api(d_minus_2_date)

        d_minus_3_date = get_previous_business_day(d_minus_2_date)
        d_minus_3_str = format_date_for_api(d_minus_3_date)

        # --- fetch official nav history ---
        recent_navs = NavService.get_latest_nav(scheme_code, limit=10)  # always list
        nav_map = {item["date"]: float(item["nav"]) for item in recent_navs} if recent_navs else {}

        official_d0 = nav_map.get(d0_str)
        official_d_minus_1 = nav_map.get(d_minus_1_str)
        official_d_minus_2 = nav_map.get(d_minus_2_str)
        official_d_minus_3 = nav_map.get(d_minus_3_str)

        # --- Determine if live data should be considered D0 or D-1 ---
        # We'll interpret live "D0" data only when:
        # 1. Today is a valid trading day (not weekend/holiday)
        # 2. Market has already opened (current time >= MARKET_OPEN_TIME)
        # If it's a trading day but before market open, live API might return old data or zeros, so we stick to D-1.
        # If it's a weekend/holiday, live API returns previous trading day's close, so it does NOT belong to "Today" (D0).
        
        # FIX: Check for stale D0 NAV (same as D-1) during market hours
        # This happens when API returns a "today" row but value hasn't updated from yesterday yet.
        if is_trading_day(now) and now.time() >= MARKET_OPEN_TIME:
             if official_d0 is not None and official_d_minus_1 is not None:
                 if official_d0 == official_d_minus_1:
                     logger.info(f"Detected stale D0 NAV for {scheme_code}: D0 matches D-1. Forcing estimation.")
                     official_d0 = None
                     
        data_is_d0 = False
        if is_trading_day(now) and now.time() >= MARKET_OPEN_TIME:
             data_is_d0 = True

        # --- Prepare Estimates ---
        estimated_d0 = None
        has_d0_prices = False

        estimated_d_minus_1 = None
        has_d_minus_1_prices = False

        # BRANCH A: Estimate D0 (Live/Intraday) - only if official D0 missing and we believe live data maps to D0
        if official_d0 is None and data_is_d0:
            port_change_d0 = NavService.calculate_portfolio_change(doc.get("holdings", []))
            if port_change_d0 is not None and official_d_minus_1 is not None:
                # port_change_d0 is percent (e.g., 1.23), official_d_minus_1 is NAV
                estimated_d0 = official_d_minus_1 * (1 + (port_change_d0 / 100.0))
                has_d0_prices = True

        # BRANCH B: Estimate D-1 (Historical Close) - only if official D-1 missing
        if official_d_minus_1 is None:
            port_change_d_minus_1 = NavService.get_historical_portfolio_change(doc.get("holdings", []), d_minus_1_date)
            if port_change_d_minus_1 is not None and official_d_minus_2 is not None:
                estimated_d_minus_1 = official_d_minus_2 * (1 + (port_change_d_minus_1 / 100.0))
                has_d_minus_1_prices = True

        # --- DECISION TREE EXECUTION ---
        current_nav = None
        day_pnl_val = 0.0
        reference_nav_for_day = None
        note = ""
        last_updated_str = ""
        is_live_estimated = False
        active_change_pct = None  # percent used in note

        if official_d0 is not None:
            # Case 1: Official NAV for D0 exists
            current_nav = official_d0
            last_updated_str = d0_str
            note = f"Official NAV ({d0_str})"

            # Reference for day PnL should be previous official (fallback search if missing)
            reference = official_d_minus_1 or official_d_minus_2
            if reference is None and recent_navs:
                for item in recent_navs:
                    if item["date"] != d0_str:
                        reference = float(item["nav"])
                        break
            if reference is not None:
                reference_nav_for_day = reference
                day_pnl_val = current_nav - reference_nav_for_day

        else:
            # Official D0 missing
            if has_d0_prices and estimated_d0 is not None:
                # Case 2: Estimate D0 using Live prices
                current_nav = estimated_d0
                is_live_estimated = True
                # active change percent relative to official D-1
                active_change_pct = ((estimated_d0 / official_d_minus_1 - 1) * 100) if official_d_minus_1 else None

                last_updated_str = "Live Est" if is_market_open(now) else "Est Close"
                note = f"Estimated ({last_updated_str})"

                # 1D = Estimated[D0] - Official[D-1] (official D-1 must exist)
                reference_nav_for_day = official_d_minus_1 or official_d_minus_2
                if reference_nav_for_day is not None:
                    day_pnl_val = current_nav - reference_nav_for_day

            else:
                # No D0 prices available
                if official_d_minus_1 is not None:
                    # Case 3: Use Official D-1
                    current_nav = official_d_minus_1
                    last_updated_str = d_minus_1_str
                    note = f"Official NAV ({d_minus_1_str})"

                    reference_nav_for_day = official_d_minus_2
                    if reference_nav_for_day is None and recent_navs:
                        for item in recent_navs:
                            if item["date"] not in (d0_str, d_minus_1_str):
                                reference_nav_for_day = float(item["nav"])
                                break
                    if reference_nav_for_day is not None:
                        day_pnl_val = current_nav - reference_nav_for_day

                else:
                    # Official D-1 missing
                    if has_d_minus_1_prices and estimated_d_minus_1 is not None:
                        # Case 4: Estimate D-1 using historical closes
                        current_nav = estimated_d_minus_1
                        is_live_estimated = True
                        active_change_pct = ((estimated_d_minus_1 / official_d_minus_2 - 1) * 100) if official_d_minus_2 else None

                        last_updated_str = f"Est {d_minus_1_str}"
                        note = f"Estimated NAV ({d_minus_1_str})"

                        reference_nav_for_day = official_d_minus_2
                        if reference_nav_for_day is not None:
                            day_pnl_val = current_nav - reference_nav_for_day

                    else:
                        # Case 5: Fallback to D-2
                        if official_d_minus_2 is not None:
                            current_nav = official_d_minus_2
                            last_updated_str = d_minus_2_str
                            note = f"Official NAV ({d_minus_2_str}) - D-1 Missing"

                            if official_d_minus_3 is not None:
                                reference_nav_for_day = official_d_minus_3
                                day_pnl_val = current_nav - reference_nav_for_day
                        else:
                            # Total Failure fallback
                            if recent_navs:
                                latest = recent_navs[0]
                                current_nav = float(latest["nav"])
                                last_updated_str = latest["date"]
                                note = f"Official NAV ({last_updated_str}) - Stale"
                            else:
                                return {"error": "No NAV data available."}

        # --- 2. Historical NAV (Purchase Price) ---
        if not investment:
            investment = float(doc.get("invested_amount", 0) or 0)
        if not input_date:
            input_date = doc.get("invested_date")

        purchase_nav = current_nav
        if input_date:
            try:
                hist_res = NavService.get_nav_at_date(scheme_code, input_date)
                if hist_res:
                    purchase_nav = hist_res[0]
            except Exception as e:
                logger.debug(f"Failed to fetch purchase NAV for {input_date}: {e}")

        # --- 3. Compute Metrics ---
        if not purchase_nav or purchase_nav == 0:
            logger.error("Invalid purchase_nav, cannot compute units")
            return {"error": "Invalid purchase NAV."}

        units = investment / purchase_nav if purchase_nav else 0
        current_value = units * current_nav if current_nav is not None else 0
        total_pnl = current_value - investment
        total_pnl_pct = (total_pnl / investment) * 100 if investment > 0 else 0

        day_pnl_amt = day_pnl_val * units if day_pnl_val and units is not None else 0

        # Compute day_pnl_pct from the stored reference_nav_for_day (safe)
        if reference_nav_for_day and reference_nav_for_day > 0:
            day_pnl_pct = (day_pnl_val / reference_nav_for_day) * 100
        else:
            day_pnl_pct = 0

        # Enhance note with percent change if estimated
        if is_live_estimated and active_change_pct is not None:
            note += f" ({active_change_pct:+.2f}%)"

        return {
            "fund_id": fund_id,
            "fund_name": fund_name,
            "invested_amount": investment,
            "invested_date": input_date,
            "units": round(units, 4),
            "purchase_nav": purchase_nav,
            "current_nav": round(current_nav, 4) if current_nav is not None else None,
            "current_value": round(current_value, 2),
            "pnl": round(total_pnl, 2),
            "pnl_pct": round(total_pnl_pct, 2),
            "day_pnl": round(day_pnl_amt, 2),
            "day_pnl_pct": round(day_pnl_pct, 2),
            "last_updated": last_updated_str,
            "note": note,
            "nickname": doc.get("nickname"),
        }


nav_service = NavService()
