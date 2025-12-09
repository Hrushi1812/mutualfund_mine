import requests
import csv
import time
from io import StringIO

# ---------------- SESSION ----------------
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json,text/html,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/"
}

session = requests.Session()
session.headers.update(HEADERS)

# ---------------- LOAD NSE MASTER CSV ----------------
def load_nse_csv():
    url = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"
    r = session.get(url, timeout=20)
    f = StringIO(r.text)
    return list(csv.DictReader(f))


# ---------------- ISIN → SYMBOL (AUTO-DETECT) ----------------
def isin_to_symbol(isin, table):
    if not table:
        return None

    headers = table[0].keys()

    isin_col = None
    symbol_col = None

    for col in headers:
        key = col.strip().lower().replace(" ", "")
        if "isin" in key:
            isin_col = col
        if key in ["symbol", "tradingsymbol", "sc_symbol"]:
            symbol_col = col

    # fallback if symbol header not obvious
    if not symbol_col:
        for col in headers:
            if "symbol" in col.lower():
                symbol_col = col

    if not isin_col or not symbol_col:
        return None

    for row in table:
        if row.get(isin_col, "").strip() == isin:
            return row.get(symbol_col)

    return None


# ---------------- NSE % CHANGE ----------------
def get_pct_change(symbol):
    base = "https://www.nseindia.com"
    api = base + "/api/quote-equity"

    # Prime cookies
    session.get(base, timeout=5)
    time.sleep(0.5)

    r = session.get(api, params={"symbol": symbol}, timeout=10)

    # NSE may return HTML when blocked
    if "application/json" not in r.headers.get("Content-Type", ""):
        return None

    data = r.json()
    return data["priceInfo"]["pChange"]


# ---------------- MAIN ----------------
if __name__ == "__main__":

    ISINS = [
        "INE040A01034",
        "INE200A01026"
    ]

    print("\nLoading NSE database...")
    nse_table = load_nse_csv()

    print("\nISIN → % CHANGE\n")

    for isin in ISINS:

        symbol = isin_to_symbol(isin, nse_table)

        if not symbol:
            print(f"{isin} -> ❌ Symbol not found in NSE list")
            continue

        pct = get_pct_change(symbol)

        if pct is None:
            print(f"{isin} -> ⚠ NSE blocked the request")
        else:
            print(f"{isin} -> {pct:.2f}% ({symbol})")
