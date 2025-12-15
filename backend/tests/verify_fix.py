
from services.nav_service import NavService
from services.holdings_service import session
from utils.common import NSE_API_URL
import requests

def verify():
    print("Verifying fix...")
    
    # 1. Ensure cookies (this should visit home page)
    print("Calling ensure_nse_cookies...")
    NavService.ensure_nse_cookies()
    print(f"Cookies after valid init: {session.cookies.get_dict()}")
    
    # 2. Try Fetch
    print("Testing fetch for SBIN...")
    p_change = NavService.get_live_price_change("SBIN")
    print(f"Result for SBIN: {p_change}")
    
    if p_change is not None:
        print("SUCCESS: Live fetch returned value.")
    else:
        print("FAILURE: Live fetch returned None.")

if __name__ == "__main__":
    verify()
