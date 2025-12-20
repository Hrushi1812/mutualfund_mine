import sys
import os
import unittest
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Mock fyers_service BEFORE importing nav_service (to avoid import errors)
sys.modules['services.fyers_service'] = MagicMock()

from services.holdings_service import HoldingsService
from services.nav_service import NavService
from models.db_schemas import SIPInstallment

class TestSIPLogic(unittest.TestCase):
    
    def test_generate_installment_dates(self):
        # Case 1: Start Date = 2023-01-01, SIP Day = 5.
        # Expect: 2023-01-01 (Start), then 2023-02-05, 2023-03-05...
        
        # Mock "Today" to be 2023-04-10
        with patch('services.holdings_service.get_current_ist_time') as mock_now:
            mock_now.return_value.date.return_value = date(2023, 4, 10)
            
            installments = HoldingsService.generate_installment_dates("01-01-2023", 5)
            
            # Dates should be: Jan 1 (Start), Feb 5, Mar 5, Apr 5
            self.assertEqual(len(installments), 4)
            self.assertEqual(installments[0]["date"], "01-01-2023")
            self.assertEqual(installments[0]["status"], "PAID")
            
            self.assertEqual(installments[1]["date"], "05-02-2023")
            self.assertEqual(installments[2]["date"], "05-03-2023")
            self.assertEqual(installments[3]["date"], "05-04-2023")
            self.assertEqual(installments[3]["status"], "PAID") # Past date relative to today
            
    def test_generate_installment_dates_pending_today(self):
        # Case 2: SIP Due Today
        with patch('services.holdings_service.get_current_ist_time') as mock_now:
            today = date(2023, 5, 5)
            mock_now.return_value.date.return_value = today
            
            # Start 1 month ago
            installments = HoldingsService.generate_installment_dates("05-04-2023", 5)
            
            # Apr 5, May 5
            self.assertEqual(len(installments), 2)
            self.assertEqual(installments[1]["date"], "05-05-2023")
            self.assertEqual(installments[1]["status"], "PENDING")

    def test_pnl_sip_logic(self):
        # Mock Doc - MUST include scheme_code or calculate_pnl returns error
        mock_doc = {
            "fund_name": "Test SIP Fund",
            "scheme_code": "123456",
            "investment_type": "sip",
            "manual_total_units": 100.0,
            "future_sip_units": 10.0,  # Total 110 units
            "invested_amount": 5000.0,  # Total Invested
            "holdings": [],
            "sip_installments": [
                {"date": "01-01-2023", "amount": 1000, "status": "PAID"},
                {"date": "01-02-2023", "amount": 1000, "status": "PENDING"}  # Pending one
            ]
        }
        
        # Mock all dependencies at once
        with patch('services.nav_service.holdings_service.get_holdings', return_value=mock_doc), \
             patch('services.nav_service.NavService.get_latest_nav', return_value=[{"date": "19-12-2025", "nav": 20.0}]), \
             patch('services.nav_service.get_current_ist_time') as mock_time, \
             patch('services.nav_service.is_trading_day', return_value=False):
             
             # Set time to match NAV date so it picks it up as D0
             mock_time.return_value.date.return_value = date(2025, 12, 19)
             mock_time.return_value.time.return_value = date(2025, 12, 19)  # dummy
             
             res = NavService.calculate_pnl("dummy_id", "dummy_user")
             
             # Debug: Print result if error
             if "error" in res:
                 print(f"ERROR: {res}")
             
             # Total Units = 110
             # Current NAV = 20.0
             # Current Value = 2200.0
             # Invested = 5000.0
             # PnL = 2200 - 5000 = -2800
             
             self.assertEqual(res["units"], 110.0)
             self.assertEqual(res["current_value"], 2200.0)
             self.assertEqual(res["pnl"], -2800.0)
             self.assertEqual(len(res["sip_pending_installments"]), 1)
             self.assertEqual(res["sip_pending_installments"][0]["date"], "01-02-2023")

if __name__ == '__main__':
    unittest.main()