import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from nav_logic import calculate_pnl, get_live_price_change

# Mock DB and MFAPI for controlled testing
import nav_logic
import db

def mock_get_holdings(fund_name):
    return {
        "fund_name": "Test Fund",
        "scheme_code": "100000", # Dummy
        "holdings": [
            {"Name": "HDFC Bank", "Symbol": "HDFCBANK", "Weight": 50.0},
            {"Name": "Reliance", "Symbol": "RELIANCE", "Weight": 50.0}
        ]
    }

def mock_get_latest_nav(scheme_code):
    return {
        "date": "01-01-2024",
        "nav": 100.0,
        "meta": {}
    }

# Patching
db.get_holdings = mock_get_holdings
nav_logic.get_latest_nav = mock_get_latest_nav

if __name__ == "__main__":
    with open("verify_log.txt", "w", encoding="utf-8") as f:
        print("--- Verifying Live NAV Logic ---")
        f.write("--- Verifying Live NAV Logic ---\n")
        
        # Check if we can fetch live price first
        print("Fetching live price for HDFCBANK...")
        f.write("Fetching live price for HDFCBANK...\n")
        p1 = get_live_price_change("HDFCBANK")
        msg = f"HDFCBANK Change: {p1}%\n"
        print(msg.strip())
        f.write(msg)
        
        print("Fetching live price for RELIANCE...")
        f.write("Fetching live price for RELIANCE...\n")
        p2 = get_live_price_change("RELIANCE")
        msg = f"RELIANCE Change: {p2}%\n"
        print(msg.strip())
        f.write(msg)
        
        if p1 is None or p2 is None:
            msg = "Skipping calculation test because live prices are unavailable.\n"
            print(msg.strip())
            f.write(msg)
            exit()
            
        # Expected Portfolio Change roughly (p1 * 0.5 + p2 * 0.5)
        exp = (p1 * 0.5) + (p2 * 0.5)
        msg = f"Expected Portfolio Change: {exp:.2f}%\n"
        print(msg.strip())
        f.write(msg)
        
        print("\n--- Running calculate_pnl ---")
        f.write("\n--- Running calculate_pnl ---\n")
        result = calculate_pnl("Test Fund", 10000, "2023-01-01")
        
        msg = f"Official NAV: 100.0\nEstimated Live NAV: {result['current_nav']}\nNote: {result['note']}\n"
        print(msg.strip())
        f.write(msg)
        
        # Validation
        est_change = ((result['current_nav'] - 100.0) / 100.0) * 100
        msg = f"Calculated Change: {est_change:.2f}%\n"
        print(msg.strip())
        f.write(msg)
        
        if abs(est_change - exp) < 0.1:
            msg = "\n✅ SUCCESS: Live NAV matches expected weighted change."
        else:
            msg = "\n❌ FAILURE: Live NAV mismatch."
        
        print(msg)
        f.write(msg + "\n")
