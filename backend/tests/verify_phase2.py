import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils.date_utils import is_market_open, get_previous_business_day, parse_date_from_str
from services.nav_service import NavService
from datetime import datetime, time

def test_market_open_logic():
    print("\n--- Testing Market Open Logic ---")
    
    # Mock times
    monday_morning = datetime(2024, 12, 16, 10, 0) # Mon 10 AM
    monday_night = datetime(2024, 12, 16, 20, 0)   # Mon 8 PM
    sunday = datetime(2024, 12, 15, 10, 0)         # Sun 10 AM
    holiday = datetime(2024, 12, 25, 10, 0)        # Christmas

    print(f"Mon 10 AM (Should be True): {is_market_open(monday_morning)}")
    print(f"Mon 8 PM (Should be False): {is_market_open(monday_night)}")
    print(f"Sun 10 AM (Should be False): {is_market_open(sunday)}")
    print(f"Christmas (Should be False): {is_market_open(holiday)}")

def test_nav_fetch():
    print("\n--- Testing NAV Fetch ---")
    scheme_code = "119063" # SBI Small Cap
    
    # 1. Latest
    latest = NavService.get_latest_nav(scheme_code)
    print(f"Latest NAV: {latest['date']} -> {latest['nav']}")
    
    # 2. Historical (Known Date)
    target_date = "10-12-2024" 
    res = NavService.get_nav_at_date(scheme_code, target_date)
    print(f"NAV on {target_date}: {res}")
    
    # 3. Historical (Weekend - 08-12-2024 was Sunday)
    target_sunday = "08-12-2024"
    res_sun = NavService.get_nav_at_date(scheme_code, target_sunday)
    print(f"NAV check for {target_sunday} (Expect <= 06-12): {res_sun}")

if __name__ == "__main__":
    test_market_open_logic()
    test_nav_fetch()
