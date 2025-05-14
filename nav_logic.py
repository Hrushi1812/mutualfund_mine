import pandas as pd
import yfinance as yf
import time
import random
from datetime import datetime
from db import save_holdings, get_holdings
import os


def save_holdings_to_mongo(fund_name, excel_file):
    df = pd.read_excel(excel_file.file)

    required_cols = ["Name of the Instrument", "% to NAV", "Symbol"]
    for col in required_cols:
        if col not in df.columns:
            return {"error": f"Excel missing required column: {col}"}

    df = df[required_cols].dropna()
    df["Symbol"] = df["Symbol"].astype(str).str.strip()

    holdings = df.to_dict(orient="records")
    save_holdings(fund_name, holdings)

    return {"message": f"Holdings saved for {fund_name}", "count": len(holdings)}


def estimate_nav(fund_name, prev_nav, investment):
    holdings = get_holdings(fund_name)
    if not holdings:
        return {"error": "Fund not found in DB. Upload holdings first."}

    df = pd.DataFrame(holdings)
    df["Daily Change (%)"] = 0.0

    for idx, row in df.iterrows():
        symbol = row["Symbol"]
        try:
            data = yf.download(symbol, period="5d", interval="1d", progress=False)
            if len(data) >= 2:
                closes = data["Close"].dropna()
                if len(closes) >= 2:
                    prev_close = float(closes.iloc[-2])
                    last_close = float(closes.iloc[-1])
                    pct_change = ((last_close - prev_close) / prev_close) * 100.0
                    df.at[idx, "Daily Change (%)"] = pct_change
        except:
            df.at[idx, "Daily Change (%)"] = 0.0

        time.sleep(0.3 + random.uniform(0, 0.3))

    df["Weighted Return"] = (df["% to NAV"] * df["Daily Change (%)"]) / 100
    total_return = df["Weighted Return"].sum()

    estimated_nav = prev_nav * (1 + total_return / 100)
    units = investment / prev_nav
    current_value = units * estimated_nav
    pnl = current_value - investment
    pnl_pct = (pnl / investment) * 100

    return {
        "fund_name": fund_name,
        "estimated_nav": round(estimated_nav, 4),
        "nav_change_%": round(total_return, 4),
        "current_value": round(current_value, 2),
        "pnl": round(pnl, 2),
        "pnl_percentage": round(pnl_pct, 2),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
