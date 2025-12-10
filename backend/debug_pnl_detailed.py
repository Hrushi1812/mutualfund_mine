
import sys
import os
import time

# Ensure backend is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db import get_holdings, list_funds
from nav_logic import get_live_price_change

def debug_live_nav_logic():
    print("\n🔍 STARTING LIVE NAV DEBUGGER 🔍")
    print("====================================")

    # 1. Pick a fund
    funds = list_funds()
    if not funds:
        print("❌ No funds found in the database.")
        return

    fund_name = funds[0] # Default to first fund
    print(f"📂 Analyzing Fund: '{fund_name}'")

    doc = get_holdings(fund_name)
    print(doc)
    if not doc or "holdings" not in doc:
        print("❌ No holdings found for this fund.")
        return

    holdings = doc["holdings"]
    print(f"📊 Total Holdings Found: {len(holdings)}")

    # 2. Simulate the loop from nav_logic.py
    total_pchange_contribution = 0.0
    total_weight_checked = 0.0
    stocks_checked = 0
    weights_raw = []

    print("\n🚀 Processing Stocks (limit first 20 for brevity)...")
    print(f"{'#':<4} {'Symbol':<15} {'Weight (Raw)':<15} {'Live Change %':<15} {'Contribution':<15}")
    print("-" * 70)

    for i, stock in enumerate(holdings):
        symbol = stock.get("Symbol")
        weight = stock.get("Weight", 0)
        weights_raw.append(weight)

        # Skip logging every single one if list is huge, but user asked for detail
        # We'll show all if < 50 items, else first 20
        # if i >= 20 and len(holdings) > 50:
        #     continue

        live_pct = "N/A"
        contrib = 0.0
        status = "⚪" # neutral

        if symbol and weight > 0:
            # Fetch Price
            pct = get_live_price_change(symbol)
            
            if pct is not None:
                live_pct = f"{pct:.2f}%"
                
                # Logic from code:
                # Contribution = Weight * pct
                contrib = weight * pct
                
                total_pchange_contribution += contrib
                total_weight_checked += weight
                stocks_checked += 1
                status = "✅"
            else:
                live_pct = "Failed"
                status = "❌"
        else:
             status = "⚠️ (No Symbol/Weight)"

        print(f"{i+1:<4} {str(symbol):<15} {weight:<15} {live_pct:<15} {contrib:<15.4f} {status}")
        
        # Polite delay not needed for debug run usually, but good practice
        # time.sleep(0.1)

    print("-" * 70)
    
    # 3. Analyze the result
    print("\n RESULTS ANALYSIS")
    print(f"Stocks Checked successfully: {stocks_checked} / {len(holdings)}")
    print(f"Total Weight Checked: {total_weight_checked}")
    
    # Check for Fraction vs Percentage issue
    print("\n🕵️ WEIGHT FORMAT DIAGNOSIS:")
    if weights_raw:
        avg_weight = sum(weights_raw) / len(weights_raw)
        max_weight = max(weights_raw)
        sum_weight = sum(weights_raw)
        
        print(f"   Sum of ALL weights in DB: {sum_weight}")
        print(f"   Max single weight: {max_weight}")
        
        if sum_weight > 0.5:
             print("   ✅ Weights appear to be in PERCENTAGE format (Sum > 0.5).")
        else:
             print("   ❓ Total weight is low (< 0.5). Ensure you are using PERCENTAGES (0-100).")

    # 4. Replicate the specific condition that failed
    print("\n📜 LOGIC CHECK:")
    print(f"   Code Condition: if total_weight_checked ({total_weight_checked}) > 0.5:")
    
    if total_weight_checked > 0.5:
        portfolio_change = total_pchange_contribution / total_weight_checked
        print(f"   ✅ PASS: Calculation would proceed.")
        print(f"   Estimated Portfolio Change: {portfolio_change:.4f}%")
    else:
        print(f"   ❌ FAIL: Threshold (0.5) not met.")
        print(f"      Skipping Live NAV: Only checked {total_weight_checked}% weight")

if __name__ == "__main__":
    debug_live_nav_logic()
