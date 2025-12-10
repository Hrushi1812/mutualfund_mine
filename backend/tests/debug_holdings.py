
import sys
import os
# Ensure parent directory is in path to import backend modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import list_funds, get_holdings
from nav_logic import get_live_price_change, load_nse_csv, isin_to_symbol_nse

print("--- Debugging Holdings ---")
funds = list_funds()
print(f"Found funds: {funds}")

if not funds:
    print("No funds found in DB.")
    exit()

# cache NSE CSV
print("Loading NSE CSV...")
nse_table = load_nse_csv()
print(f"Loaded {len(nse_table)} rows from NSE CSV.")

for fund in funds:
    print(f"\nAnalyzing Fund: {fund}")
    doc = get_holdings(fund)
    holdings = doc.get("holdings", [])
    print(f"Total Holdings: {len(holdings)}")
    
    if not holdings:
        continue
        
    resolved_count = 0
    total_weight = 0
    live_price_count = 0
    
    # Check first 5 holdings in detail
    print("\nSample Holdings:")
    for i, stock in enumerate(holdings[:5]):
        isin = stock.get("ISIN")
        symbol = stock.get("Symbol")
        weight = stock.get("Weight", 0)
        name = stock.get("Name")
        
        print(f"  {i+1}. {name} | ISIN: {isin} | Symbol: {symbol} | Weight: {weight}")
        
        # Verify resolution
        resolved_symbol = isin_to_symbol_nse(isin, nse_table)
        if resolved_symbol != symbol:
            print(f"     ⚠️  Mismatch! Logic resolves {isin} -> {resolved_symbol}")
            
        # Test Live Price
        if symbol:
            price = get_live_price_change(symbol)
            if price is not None:
                print(f"     ✅ Live Price: {price}%")
                live_price_count += 1
            else:
                print(f"     ❌ Live Price Failed for {symbol}")
        else:
            print("     ❌ No Symbol to check price")
            
    # Stats for all
    print("\nAggregate Stats:")
    for stock in holdings:
        if stock.get("Symbol"):
            resolved_count += 1
            # We won't spam API for all, just count valid symbols
        total_weight += stock.get("Weight", 0)
        
    print(f"  Holdings with Symbols: {resolved_count}/{len(holdings)}")
    print(f"  Total Weight recorded: {total_weight}%")
