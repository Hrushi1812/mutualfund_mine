"""
Manual Robustness Test for Live Stock Fetching
Run this script to test the NSE fetching mechanism.

Usage:
    python tests/test_live_fetch_robustness.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import time
from services.holdings_service import session
from services.nav_service import NavService
from utils.common import NSE_BASE_URL

def test_cookie_status():
    """Test 1: Check current cookie state"""
    print("\n" + "="*60)
    print("TEST 1: Cookie Status")
    print("="*60)
    
    print(f"Current cookies: {len(session.cookies)}")
    for cookie in session.cookies:
        print(f"  - {cookie.name}: {cookie.value[:20]}..." if len(cookie.value) > 20 else f"  - {cookie.name}: {cookie.value}")
    
    if len(session.cookies) == 0:
        print("⚠️  No cookies - will be initialized on first request")
    else:
        print("✅ Cookies already present")

def test_single_stock_fetch():
    """Test 2: Fetch a single stock to verify basic functionality"""
    print("\n" + "="*60)
    print("TEST 2: Single Stock Fetch (RELIANCE)")
    print("="*60)
    
    NavService.ensure_nse_cookies()
    print(f"Cookies after ensure: {len(session.cookies)}")
    
    start = time.time()
    result = NavService.get_live_price_change("RELIANCE")
    duration = time.time() - start
    
    if result is not None:
        print(f"✅ RELIANCE pChange: {result:+.2f}% (fetched in {duration:.2f}s)")
    else:
        print(f"❌ Failed to fetch RELIANCE (took {duration:.2f}s)")

def test_multiple_stocks_sequential():
    """Test 3: Fetch multiple stocks sequentially to test rate limiting"""
    print("\n" + "="*60)
    print("TEST 3: Sequential Fetch (10 stocks)")
    print("="*60)
    
    test_symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", 
                    "HINDUNILVR", "SBIN", "BHARTIARTL", "KOTAKBANK", "LT"]
    
    success = 0
    failed = []
    
    for sym in test_symbols:
        result = NavService.get_live_price_change(sym)
        if result is not None:
            print(f"  ✅ {sym}: {result:+.2f}%")
            success += 1
        else:
            print(f"  ❌ {sym}: FAILED")
            failed.append(sym)
        time.sleep(0.2)  # Small delay
    
    print(f"\nResult: {success}/{len(test_symbols)} successful")
    if failed:
        print(f"Failed symbols: {failed}")

def test_cookie_clear_and_refetch():
    """Test 4: Clear cookies and verify re-initialization"""
    print("\n" + "="*60)
    print("TEST 4: Cookie Clear & Re-fetch")
    print("="*60)
    
    print("Clearing all cookies...")
    session.cookies.clear()
    print(f"Cookies after clear: {len(session.cookies)}")
    
    print("Fetching INFY (should auto-initialize cookies)...")
    NavService.ensure_nse_cookies()
    result = NavService.get_live_price_change("INFY")
    
    print(f"Cookies after fetch: {len(session.cookies)}")
    if result is not None:
        print(f"✅ INFY pChange: {result:+.2f}%")
    else:
        print("❌ Failed - cookies may not be initializing properly")

def test_invalid_symbol():
    """Test 5: Test behavior with invalid symbol"""
    print("\n" + "="*60)
    print("TEST 5: Invalid Symbol Handling")
    print("="*60)
    
    result = NavService.get_live_price_change("INVALIDSYMBOL123")
    if result is None:
        print("✅ Correctly returned None for invalid symbol")
    else:
        print(f"⚠️  Unexpected result: {result}")

def test_portfolio_change_mock():
    """Test 6: Test calculate_portfolio_change with mock holdings"""
    print("\n" + "="*60)
    print("TEST 6: Portfolio Change Calculation (Mini Test)")
    print("="*60)
    
    # Mock holdings with 5 major stocks
    mock_holdings = [
        {"Symbol": "RELIANCE", "Weight": 25},
        {"Symbol": "TCS", "Weight": 20},
        {"Symbol": "INFY", "Weight": 15},
        {"Symbol": "HDFCBANK", "Weight": 20},
        {"Symbol": "ICICIBANK", "Weight": 20},
    ]
    
    print(f"Testing with {len(mock_holdings)} stocks (total weight: 100%)")
    start = time.time()
    result = NavService.calculate_portfolio_change(mock_holdings)
    duration = time.time() - start
    
    if result is not None:
        print(f"✅ Portfolio change: {result:+.2f}% (calculated in {duration:.2f}s)")
    else:
        print(f"❌ Failed to calculate (took {duration:.2f}s)")
        print("   This could mean coverage < 75% threshold")

def test_rate_limit_stress():
    """Test 7: Stress test to check rate limiting behavior"""
    print("\n" + "="*60)
    print("TEST 7: Rate Limit Stress Test (20 rapid requests)")
    print("="*60)
    
    symbols = ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"] * 4  # 20 requests
    
    start = time.time()
    success = 0
    
    for i, sym in enumerate(symbols):
        result = NavService.get_live_price_change(sym, max_retries=1)  # Reduced retries for speed
        if result is not None:
            success += 1
        # NO delay - intentionally stress testing
    
    duration = time.time() - start
    print(f"Result: {success}/{len(symbols)} in {duration:.2f}s")
    
    if success < 15:
        print("⚠️  High failure rate - NSE may be rate limiting")
    else:
        print("✅ Good success rate under stress")

def run_all_tests():
    """Run all robustness tests"""
    print("\n" + "🔧 "*20)
    print("   NSE LIVE FETCH ROBUSTNESS TEST SUITE")
    print("🔧 "*20)
    
    test_cookie_status()
    test_single_stock_fetch()
    test_multiple_stocks_sequential()
    test_cookie_clear_and_refetch()
    test_invalid_symbol()
    test_portfolio_change_mock()
    test_rate_limit_stress()
    
    print("\n" + "="*60)
    print("ALL TESTS COMPLETED")
    print("="*60)
    print("\nCheck the results above to identify any weak points.")
    print("If TEST 6 fails, your real portfolio fetch will also fail.")

if __name__ == "__main__":
    run_all_tests()
