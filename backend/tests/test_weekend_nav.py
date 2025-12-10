
import sys
import os
from datetime import datetime

# Ensure backend is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nav_logic import get_nav_at_date

# Mock response data for testing logic without real API if needed, 
# but here we can try real API or just trust logic.
# Let's trust the logic update and run a targeted test on a known scheme.

# Nippon India Multi Cap Fund Direct Growth (Scheme Code example: 120591, 118550 etc? Need a real one)
# Finding a real scheme code from the user's logs/context would be best.
# User mentioned "Nippon India Multi Cap Fund Direct Growth" in previous logs.
# Let's search for it or just use a known stable one like HDFC Top 100 (119062).

SCHEME_CODE = "120591" # Nippon India Multi Cap Fund Direct Growth (Growth)

DATE_SUNDAY = "18-12-2022" 
# Expecting to find NAV for 16-12-2022 (Friday)

print(f"--- Testing NAV Fallback for {DATE_SUNDAY} (Sunday) ---")
nav = get_nav_at_date(SCHEME_CODE, DATE_SUNDAY)

if nav:
    print(f"✅ Success! Found NAV: {nav}")
else:
    print(f"❌ Failed to find NAV.")
