"""
XIRR Calculator Tests

Tests for the XIRR utility to verify correct annualized return calculation.
"""

import sys
import os
import unittest
from datetime import date

# Add backend to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.xirr import calculate_xirr, calculate_sip_xirr


class TestXIRRCalculation(unittest.TestCase):
    """Tests for XIRR calculation accuracy."""
    
    def test_simple_one_year_growth(self):
        """Invest 10000, get 11000 after 1 year = ~10% XIRR."""
        cash_flows = [
            (date(2023, 1, 1), -10000),  # Invested
            (date(2024, 1, 1), 11000),   # Final value
        ]
        xirr = calculate_xirr(cash_flows)
        self.assertIsNotNone(xirr)
        self.assertAlmostEqual(xirr, 10.0, delta=0.5)
    
    def test_monthly_sip_positive_return(self):
        """Monthly SIP of 1000 for 12 months with positive return."""
        cash_flows = [
            (date(2023, 1, 1), -1000),
            (date(2023, 2, 1), -1000),
            (date(2023, 3, 1), -1000),
            (date(2023, 4, 1), -1000),
            (date(2023, 5, 1), -1000),
            (date(2023, 6, 1), -1000),
            (date(2023, 7, 1), -1000),
            (date(2023, 8, 1), -1000),
            (date(2023, 9, 1), -1000),
            (date(2023, 10, 1), -1000),
            (date(2023, 11, 1), -1000),
            (date(2023, 12, 1), -1000),
            (date(2024, 1, 1), 13200),  # 10% return on 12000
        ]
        xirr = calculate_xirr(cash_flows)
        self.assertIsNotNone(xirr)
        # Should be around 20% annualized (since mid-point weighted)
        self.assertGreater(xirr, 10)
        self.assertLess(xirr, 30)
    
    def test_negative_return(self):
        """Investment with loss should give negative XIRR."""
        cash_flows = [
            (date(2023, 1, 1), -10000),
            (date(2024, 1, 1), 9000),  # 10% loss
        ]
        xirr = calculate_xirr(cash_flows)
        self.assertIsNotNone(xirr)
        self.assertAlmostEqual(xirr, -10.0, delta=0.5)
    
    def test_insufficient_data(self):
        """Single cash flow should return None."""
        cash_flows = [
            (date(2023, 1, 1), -10000),
        ]
        xirr = calculate_xirr(cash_flows)
        self.assertIsNone(xirr)
    
    def test_all_investments_no_return(self):
        """All negative (investments) with no positive should return None."""
        cash_flows = [
            (date(2023, 1, 1), -10000),
            (date(2023, 6, 1), -10000),
        ]
        xirr = calculate_xirr(cash_flows)
        self.assertIsNone(xirr)
    
    def test_date_string_parsing(self):
        """Should handle different date string formats."""
        cash_flows = [
            ("2023-01-01", -10000),
            ("01-01-2024", 11000),
        ]
        xirr = calculate_xirr(cash_flows)
        self.assertIsNotNone(xirr)
        self.assertAlmostEqual(xirr, 10.0, delta=0.5)


class TestSIPXIRRFunction(unittest.TestCase):
    """Tests for the SIP-specific XIRR wrapper."""
    
    def test_sip_xirr_with_paid_installments(self):
        """Calculate XIRR from SIP installments list."""
        installments = [
            {"date": "01-01-2023", "amount": 1000, "status": "PAID"},
            {"date": "01-02-2023", "amount": 1000, "status": "PAID"},
            {"date": "01-03-2023", "amount": 1000, "status": "PAID"},
            {"date": "01-04-2023", "amount": 1000, "status": "PENDING"},  # Should be ignored
            {"date": "01-05-2023", "amount": 1000, "status": "SKIPPED"},  # Should be ignored
        ]
        
        xirr = calculate_sip_xirr(
            installments=installments,
            current_value=3300,  # 10% profit on 3000
            current_date=date(2023, 6, 1)
        )
        
        self.assertIsNotNone(xirr)
        # Only 3 PAID installments (3000 invested), now worth 3300
        self.assertGreater(xirr, 0)
    
    def test_sip_xirr_no_paid_installments(self):
        """Should return None if no PAID installments."""
        installments = [
            {"date": "01-01-2023", "amount": 1000, "status": "PENDING"},
            {"date": "01-02-2023", "amount": 1000, "status": "SKIPPED"},
        ]
        
        xirr = calculate_sip_xirr(
            installments=installments,
            current_value=0,
            current_date=date(2023, 3, 1)
        )
        
        self.assertIsNone(xirr)


class TestXIRREdgeCases(unittest.TestCase):
    """Edge case tests for XIRR robustness."""
    
    def test_very_high_return(self):
        """Handle very high returns without overflow."""
        cash_flows = [
            (date(2023, 1, 1), -1000),
            (date(2024, 1, 1), 5000),  # 400% gain
        ]
        xirr = calculate_xirr(cash_flows)
        self.assertIsNotNone(xirr)
        self.assertGreater(xirr, 300)
    
    def test_very_short_period(self):
        """Handle very short investment periods."""
        cash_flows = [
            (date(2023, 1, 1), -1000),
            (date(2023, 1, 15), 1010),  # 1% in 2 weeks
        ]
        xirr = calculate_xirr(cash_flows)
        self.assertIsNotNone(xirr)
        # Annualized 1% in 2 weeks is very high
        self.assertGreater(xirr, 20)
    
    def test_20_year_sip(self):
        """Handle 20 years of monthly SIP data."""
        cash_flows = []
        start = date(2003, 1, 1)
        
        for i in range(240):  # 20 years * 12 months
            year = 2003 + (i // 12)
            month = (i % 12) + 1
            cf_date = date(year, month, 1)
            cash_flows.append((cf_date, -1000))
        
        # Final value after 20 years with ~10% CAGR
        cash_flows.append((date(2023, 1, 1), 760000))  # Roughly 3x
        
        xirr = calculate_xirr(cash_flows)
        self.assertIsNotNone(xirr)
        # Should be a reasonable positive number
        self.assertGreater(xirr, 0)
        self.assertLess(xirr, 50)


if __name__ == '__main__':
    unittest.main()
