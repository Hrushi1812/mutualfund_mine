
import sys
import os
from datetime import datetime

# Ensure backend is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nav_logic import get_nav_at_date

# known scheme
SCHEME_CODE = "119062" # HDFC Top 100 fund

# 18-12-2022 was a SUNDAY
TARGET_DATE = "18-12-2022" 

print(f"--- Verifying NAV Fallback for {TARGET_DATE} (Sunday) ---")
print("Target: Find NAV for 18th or the immediately preceding Friday (16th).")

nav_result = get_nav_at_date(SCHEME_CODE, TARGET_DATE)

if nav_result:
    nav, date = nav_result
    print(f"✅ Success! Found NAV: {nav} on Date: {date}")
else:
    print(f"❌ Result: None (Lookup failed)")

# Also print what expected behavior implies
# If it works, 'nav' should be the float value of 16th Dec 2022.
