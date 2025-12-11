import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from models.schemas import UserCreate, FundBase, PortfolioAnalysisRequest
from pydantic import ValidationError

def test_validation():
    print("\n--- Testing Pydantic Validation ---")
    
    # 1. Invalid User (Short password)
    try:
        UserCreate(username="validuser", email="test@example.com", password="123")
        print("❌ Failed: Accepted short password")
    except ValidationError:
        print("✅ Correctly rejected short password")

    # 2. Invalid Amount (Negative)
    try:
        PortfolioAnalysisRequest(fund_id="123", investment_amount=-500)
        print("❌ Failed: Accepted negative amount")
    except ValidationError:
        print("✅ Correctly rejected negative amount")

    # 3. Invalid Date Format
    try:
        PortfolioAnalysisRequest(fund_id="123", investment_date="12-12-2024") # Expects YYYY-MM-DD
        print("❌ Failed: Accepted DD-MM-YYYY")
    except ValidationError:
        print("✅ Correctly rejected wrong date format")

    print("--- Validation Tests Complete ---\n")

if __name__ == "__main__":
    test_validation()
