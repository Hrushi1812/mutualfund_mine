import pandas as pd
import csv
import requests
from io import StringIO
from bson import ObjectId
from db import holdings_collection
from typing import List, Optional

from datetime import datetime
from utils.common import NSE_HEADERS, NSE_CSV_URL
from utils.date_utils import format_date_for_api
from core.logging import get_logger

logger = get_logger("HoldingsService")

session = requests.Session()
session.headers.update(NSE_HEADERS)

def load_nse_csv():
    """Downloads and caches the NSE Equity Master List (CSV)."""
    url = NSE_CSV_URL
    try:
        r = session.get(url, timeout=20)
        f = StringIO(r.text)
        return list(csv.DictReader(f))
    except Exception as e:
        logger.error(f"Error downloading NSE CSV: {e}")
        return []

def isin_to_symbol_nse(isin, nse_table=None):
    """Resolves ISIN to NSE Symbol."""
    if not nse_table:
        nse_table = load_nse_csv()
    if not nse_table: return None
    
    headers = nse_table[0].keys()
    isin_col = next((col for col in headers if "isin" in col.lower().replace(" ", "")), None)
    symbol_col = next((col for col in headers if col.lower().strip() in ["symbol", "tradingsymbol", "sc_symbol"]), None)
    
    if not symbol_col: # Fallback
         symbol_col = next((col for col in headers if "symbol" in col.lower()), None)

    if not isin_col or not symbol_col: return None

    for row in nse_table:
        if row.get(isin_col, "").strip() == isin:
            return row.get(symbol_col)
    return None

def search_scheme_code(query):
    try:
        url = f"https://api.mfapi.in/mf/search?q={query}"
        response = requests.get(url)
        if response.status_code == 200:
             data = response.json()
             if data and len(data) > 0:
                 return str(data[0]["schemeCode"])
    except Exception as e:
        logger.warning(f"Search error for '{query}': {e}")
    return None

# --- Main Service Class ---

class HoldingsService:
    @staticmethod
    def _is_portfolio_stale(upload_date: datetime) -> bool:
        """
        Determines if a portfolio is stale based on SEBI's 10-day monthly disclosure rule.
        Rule: On the 11th of Month M, we expect an upload from Month M.
        """
        if not upload_date: return True
        
        now = datetime.utcnow() # Using UTC for consistency
        cutoff_day = 10
        
        if now.day > cutoff_day:
            # Past the 10th: Must have upload from CURRENT month
            return not (upload_date.month == now.month and upload_date.year == now.year)
        else:
            # Before the 10th: Upload from CURRENT OR PREVIOUS month is fine
            # Check if upload is from current month
            if upload_date.month == now.month and upload_date.year == now.year:
                return False
                
            # Check if upload is from previous month
            first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            last_month_end = first_of_this_month - timedelta(days=1)
            
            return not (upload_date.month == last_month_end.month and upload_date.year == last_month_end.year)

    @staticmethod
    def list_funds(user_id):
        cursor = holdings_collection.find({"user_id": user_id}, {"fund_name": 1, "invested_amount": 1, "invested_date": 1, "scheme_code": 1, "nickname": 1, "created_at": 1})
        funds = []
        for doc in cursor:
            created_at = doc.get("created_at")
            is_stale = HoldingsService._is_portfolio_stale(created_at)
            
            funds.append({
                "id": str(doc["_id"]),
                "fund_name": doc.get("fund_name"),
                "invested_amount": doc.get("invested_amount"),
                "invested_date": doc.get("invested_date"),
                "scheme_code": doc.get("scheme_code"),
                "nickname": doc.get("nickname"),
                "is_stale": is_stale,
                "created_at": format_date_for_api(created_at) if created_at else None
            })
        return funds

    @staticmethod
    def get_holdings(fund_id_str, user_id):
        try:
            doc = holdings_collection.find_one({"_id": ObjectId(fund_id_str)})
            if doc and doc.get("user_id") == user_id:
                # Add stale status to single view as well if needed
                doc["is_stale"] = HoldingsService._is_portfolio_stale(doc.get("created_at"))
                return doc
            return None
        except:
            return None

    @staticmethod
    def delete_fund(fund_id_str, user_id):
        try:
            res = holdings_collection.delete_one({"_id": ObjectId(fund_id_str), "user_id": user_id})
            return res.deleted_count > 0
        except:
            return False

    @staticmethod
    def process_and_save_holdings(fund_name, excel_file, user_id, scheme_code=None, invested_amount=None, invested_date=None, nickname=None):
        # 1. Read Excel
        try:
            df_raw = pd.read_excel(excel_file.file, header=None)
        except Exception as e:
            return {"error": f"Failed to read Excel: {str(e)}"}

        # 2. Find Header (Robust)
        header_idx = None
        
        # Scan first 50 rows only to find the header
        # We look for a row that contains BOTH "ISIN" and some form of "NAME"/ "DESCRIPTION"
        for idx, row in df_raw.head(50).iterrows():
            row_str = row.astype(str).str.upper().tolist()
            
            has_isin = any(x.strip() in ["ISIN", "ISIN CODE", "ISIN NO"] for x in row_str if isinstance(x, str))
            has_name = any(x.strip() in ["SCHEME NAME", "FUND NAME", "DESCRIPTION", "NAME", "SCHEME"] for x in row_str if isinstance(x, str))
            
            if has_isin and has_name:
                header_idx = idx
                break
        
        if header_idx is None:
             # Fallback: Just look for ISIN if we strictly need it
             for idx, row in df_raw.head(50).iterrows():
                 row_str = row.astype(str).str.upper().tolist()
                 if any("ISIN" in x for x in row_str if isinstance(x, str)):
                     header_idx = idx
                     break
        
        if header_idx is None:
            return {"error": "Could not detect header row. Ensure file has 'ISIN' and 'Scheme Name' columns."}

        excel_file.file.seek(0)
        df = pd.read_excel(excel_file.file, header=header_idx)

        # 3. Normalize Columns
        col_map = {}
        for col in df.columns:
            c = str(col).strip().upper()
            if "ISIN" in c: col_map[col] = "ISIN"
            elif "NAME" in c and "INSTRUMENT" in c: col_map[col] = "Name"
            elif "%" in c and ("NAV" in c or "ASSET" in c): col_map[col] = "Weight"
        
        df = df.rename(columns=col_map)
        
        if "ISIN" not in df.columns or "Weight" not in df.columns:
             return {"error": f"Missing columns. Found: {df.columns.tolist()}"}
        
        # 4. Clean Data
        df = df.dropna(subset=["ISIN"])
        df["ISIN"] = df["ISIN"].astype(str).str.strip().str.upper()
        df = df[df["ISIN"].str.match(r'^[A-Z0-9]{12}$', na=False)]
        df = df.drop_duplicates(subset=["ISIN"], keep="first")
        
        def clean_weight(val):
            try:
                if pd.isna(val): return 0.0
                s = str(val).strip().replace("%", "")
                return float(s)
            except: return 0.0
            
        df["Weight"] = df["Weight"].apply(clean_weight)

        # 5. Resolve Tickers
        nse_source = load_nse_csv()
        holdings_list = []
        unresolved = []

        for _, row in df.iterrows():
            isin = row["ISIN"]
            name = row.get("Name", "Unknown")
            weight = float(row["Weight"])
            if weight <= 0: continue
            
            ticker = isin_to_symbol_nse(isin, nse_table=nse_source)
            if ticker:
                holdings_list.append({"ISIN": isin, "Name": name, "Symbol": ticker, "Weight": weight})
            else:
                unresolved.append(f"{name} ({isin})")
        
        if not holdings_list:
            return {"error": "No valid holdings resolved."}

        # 5.5 Auto-lookup Scheme Code if missing
        if not scheme_code:
            logger.info(f"Scheme code not provided for '{fund_name}'. Attempting auto-lookup...")
            code = search_scheme_code(fund_name)
            if code:
                scheme_code = code
                logger.info(f"Found scheme code: {scheme_code}")
            else:
                logger.warning(f"Could not find scheme code for '{fund_name}'")

        # 6. Save to DB (Strict Schema)
        from models.db_schemas import HoldingsDocument, HoldingItem
        from datetime import datetime
        
        # Validated List
        validated_holdings = []
        for h in holdings_list:
             validated_holdings.append(HoldingItem(**h))

        doc_data = {
            "fund_name": fund_name,
            "user_id": user_id,
            "scheme_code": scheme_code,
            "invested_amount": invested_amount,
            "invested_date": invested_date,
            "nickname": nickname,
            "holdings": validated_holdings,
            "last_updated": True,
            "created_at": datetime.utcnow()
        }
        
        # Validate entire document
        # If this fails, it means we have bad internal data logic
        try:
             doc_model = HoldingsDocument(**doc_data)
        except Exception as e:
             return {"error": f"Schema Validation Failed: {e}"}

        # Upsert
        query = {
            "fund_name": fund_name,
            "user_id": user_id,
            "invested_amount": invested_amount,
            "invested_date": invested_date
        }
        # Dump model to dict for Mongo
        holdings_collection.update_one(query, {"$set": doc_model.dict()}, upsert=True)
        
        # Fetch the ID
        saved_doc = holdings_collection.find_one(query)
        saved_id = str(saved_doc["_id"]) if saved_doc else None

        return {
            "message": f"Holdings saved for {fund_name}",
            "count": len(holdings_list),
            "unresolved_count": len(unresolved),
            "id": saved_id
        }

holdings_service = HoldingsService()
