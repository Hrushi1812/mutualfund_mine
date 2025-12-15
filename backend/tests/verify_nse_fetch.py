
import requests
from services.holdings_service import session
from utils.common import NSE_API_URL, NSE_BASE_URL
from core.logging import get_logger

# Setup simpler logger for script
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Verifier")

def test_fetch(symbol="SBIN"):
    logger.info(f"Testing fetch for {symbol}...")
    try:
        # 1. Inspect current session headers
        logger.info(f"Session Headers: {session.headers}")
        
        # 2. Try fetching API directly
        logger.info(f"Attempting GET {NSE_API_URL} params={{'symbol': '{symbol}'}}")
        r = session.get(NSE_API_URL, params={"symbol": symbol}, timeout=10)
        
        logger.info(f"Status Code: {r.status_code}")
        logger.info(f"Content-Type: {r.headers.get('Content-Type')}")
        
        if "application/json" in r.headers.get("Content-Type", ""):
            data = r.json()
            logger.info("Success! JSON received.")
            p_change = data.get("priceInfo", {}).get("pChange")
            logger.info(f"pChange: {p_change}")
        else:
            logger.error("Failed: Non-JSON response")
            logger.error(f"Response text snippet: {r.text[:200]}")
            
    except Exception as e:
        logger.error(f"Exception: {e}")

if __name__ == "__main__":
    test_fetch()
