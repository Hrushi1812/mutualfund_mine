# Common Constants and Headers

NSE_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept": "application/json,text/html,*/*",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.nseindia.com/"
}

NSE_BASE_URL = "https://www.nseindia.com"
NSE_API_URL = NSE_BASE_URL + "/api/quote-equity"
NSE_CSV_URL = "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv"

# FYERS public symbol master files (contain ISIN mappings).
# These are used as a fallback when a holding isn't present in NSE's EQUITY_L list.
FYERS_NSE_CM_URL = "https://public.fyers.in/sym_details/NSE_CM.csv"
FYERS_BSE_CM_URL = "https://public.fyers.in/sym_details/BSE_CM.csv"

MFAPI_BASE_URL = "https://api.mfapi.in/mf"
