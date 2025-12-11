import pandas as pd
import csv
import requests
from io import StringIO
from bson import ObjectId
from db import holdings_collection
from typing import List, Optional

from datetime import datetime
from utils.common import NSE_HEADERS, NSE_CSV_URL

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
        print(f"Error downloading NSE CSV: {e}")
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
        print(f"Search error: {e}")
    return None

# --- Main Service Class ---

class HoldingsService:
    @staticmethod
    def list_funds(user_id):
        cursor = holdings_collection.find({"user_id": user_id}, {"fund_name": 1, "invested_amount": 1, "invested_date": 1, "scheme_code": 1, "nickname": 1})
        funds = []
        for doc in cursor:
            funds.append({
                "id": str(doc["_id"]),
                "fund_name": doc.get("fund_name"),
                "invested_amount": doc.get("invested_amount"),
                "invested_date": doc.get("invested_date"),
                "scheme_code": doc.get("scheme_code"),
                "nickname": doc.get("nickname")
            })
        return funds

    @staticmethod
    def get_holdings(fund_id_str, user_id):
        try:
            doc = holdings_collection.find_one({"_id": ObjectId(fund_id_str)})
            if doc and doc.get("user_id") == user_id:
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

        # 2. Find Header
        header_idx = None
        for idx, row in df_raw.iterrows():
            row_str = row.astype(str).str.upper().tolist()
            if any(x.strip() in ["ISIN", "ISIN CODE", "ISIN NO"] for x in row_str if isinstance(x, str)):
                header_idx = idx
                break
        
        if header_idx is None:
             # Fallback sloppy search
             for idx, row in df_raw.iterrows():
                 row_str = row.astype(str).str.upper().tolist()
                 if any("ISIN" in x for x in row_str if isinstance(x, str)):
                     header_idx = idx
                     break
        
        if header_idx is None:
            return {"error": "Could not find 'ISIN' column header."}

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

        # 6. Save to DB
        data = {
            "fund_name": fund_name,
            "holdings": holdings_list,
            "user_id": user_id,
            "last_updated": True
        }
        if scheme_code: data["scheme_code"] = scheme_code
        if invested_amount: data["invested_amount"] = invested_amount
        if invested_date: data["invested_date"] = invested_date
        if nickname: data["nickname"] = nickname
        
        query = {
            "fund_name": fund_name,
            "user_id": user_id,
            "invested_amount": invested_amount,
            "invested_date": invested_date
        }
        holdings_collection.update_one(query, {"$set": data}, upsert=True)
        
        return {
            "message": f"Holdings saved for {fund_name}",
            "count": len(holdings_list),
            "unresolved_count": len(unresolved)
        }

holdings_service = HoldingsService()
