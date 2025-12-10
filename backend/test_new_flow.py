import requests
import os

BASE_URL = "http://127.0.0.1:8000"

def test_flow():
    print("Testing Upload Portfolio with Investment Details...")
    
    # Create a dummy excel file
    with open("dummy_holdings.xlsx", "wb") as f:
        # We need a valid excel content. 
        # Since I can't easily generate valid excel binary here without pandas/openpyxl installed in this script context (which might not be),
        # I'll rely on the existing upload logic being robust or mock the file part if passing to function directly.
        # However, to test the API properly, I need a file.
        pass

    # Actually, I can just call the logic functions directly if I import them.
    # That is safer and faster for unit testing logic.
    
    from db import save_holdings, get_holdings, client
    from nav_logic import calculate_pnl
    
    # ensure connected
    client.admin.command('ismaster')
    
    fund_name = "TestPortfolio_Automated"
    
    # 1. Simulate Save
    print(f"Saving {fund_name}...")
    save_holdings(
        fund_name=fund_name, 
        holdings_list=[{"Symbol": "RELIANCE", "Weight": 10}], 
        scheme_code="123456", 
        invested_amount=50000.0, 
        invested_date="2023-01-01"
    )
    
    # 2. Verify Storage
    doc = get_holdings(fund_name)
    print("Stored Doc:", doc)
    assert doc["invested_amount"] == 50000.0
    assert doc["invested_date"] == "2023-01-01"
    print("✅ Storage Verified")
    
    # 3. Simulate Analysis (without passing args)
    print("Simulating Analysis...")
    # calculating pnl will try to fetch NAV. Since scheme code 123456 is fake, it might fail to get NAV,
    # but we want to check if it correctly ATTEMPTS to use the stored date/amount.
    
    # We can inspect the error message.
    # If it says "Scheme Code missing" or "Could not fetch", it means it passed the input check.
    # If it says "Investment details not found", it failed.
    
    result = calculate_pnl(fund_name, None, None)
    print("Analysis Result:", result)
    
    # If logic works, it should NOT return "Investment details not found"
    if "error" in result:
        assert result["error"] != "Investment details not found. Please re-upload portfolio."
        print("✅ Logic Correctly attempted to use stored details")
    else:
        print("✅ Analysis successful (mock data worked?)")

    # Cleanup
    from db import delete_fund
    delete_fund(fund_name)
    print("Cleanup Done.")

if __name__ == "__main__":
    test_flow()
