
import sys
import os
from unittest.mock import MagicMock, patch
from datetime import datetime, date, time as dt_time

# Adjust path to find backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.nav_service import NavService
from utils import date_utils

def run_verification():
    print("Running Stale NAV Verification...")

    # Mock Data
    scheme_code = "123456"
    mock_holdings = {"fund_name": "Test Fund", "scheme_code": scheme_code, "holdings": [], "invested_amount": 1000, "invested_date": "2023-01-01"}
    
    # Mock Dates: Let's assume today is Friday 2023-10-27
    # Market Open is 09:15
    mock_today = datetime(2023, 10, 27, 10, 0, 0) # 10:00 AM
    d0_str = "27-10-2023"
    d_minus_1_str = "26-10-2023"
    
    # Mock NAV Data: d0 and d-1 are IDENTICAL (Stale case)
    mock_nav_data = [
        {"date": d0_str, "nav": "100.0"},       # "Today"
        {"date": d_minus_1_str, "nav": "100.0"}, # Yesterday (Same as today)
        {"date": "25-10-2023", "nav": "99.0"}
    ]

    # Patch 1: holdings_service.get_holdings
    with patch('services.nav_service.holdings_service.get_holdings', return_value=mock_holdings):
        # Patch 2: date_utils functions
        with patch('services.nav_service.get_current_ist_time', return_value=mock_today):
            with patch('services.nav_service.is_trading_day', return_value=True):
                 # Patch 3: NavService.get_latest_nav
                with patch.object(NavService, 'get_latest_nav', return_value=mock_nav_data):
                     # Patch 4: NavService.calculate_portfolio_change (live est)
                     # We want to see if it tries to estimate. 
                     # If official_d0 is kept as 100.0, it enters "Official NAV" branch.
                     # If official_d0 is set to None, it enters "Estimate D0" branch.
                     
                     with patch.object(NavService, 'calculate_portfolio_change', return_value=1.0) as mock_calc_change:
                        
                        # EXECUTE
                        result = NavService.calculate_pnl("dummy_id", "dummy_user")
                        
                        print("\n--- Result ---")
                        print(f"Current NAV: {result.get('current_nav')}")
                        print(f"Note: {result.get('note')}")
                        
                        # VERIFICATION LOGIC
                        if "Estimated" in result.get("note", ""):
                            print("SUCCESS: Logic correctly switched to ESTIMATED mode despite 'today' NAV being present.")
                        elif "Official NAV" in result.get("note", ""):
                             print("FAILURE: Logic used the Stale Official NAV.")
                        else:
                            print("UNKNOWN: Checking logs.")

if __name__ == "__main__":
    run_verification()
