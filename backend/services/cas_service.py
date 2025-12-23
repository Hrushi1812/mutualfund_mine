"""
CAS Parser Service
==================
Parses Consolidated Account Statement (CAS) PDF files using casparser library.
Extracts transaction data for accurate XIRR calculation in detailed SIP mode.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, date
import tempfile
import os
import json

logger = logging.getLogger(__name__)

# Try importing casparser
try:
    import casparser
    CASPARSER_AVAILABLE = True
except ImportError:
    CASPARSER_AVAILABLE = False
    logger.warning("casparser not installed. CAS parsing will not be available.")


def _to_dict(obj):
    """Convert any object to a JSON-serializable dict."""
    if obj is None:
        return None
    if isinstance(obj, dict):
        return {k: _to_dict(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_dict(item) for item in obj]
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, (int, float, str, bool)):
        return obj
    # Handle Decimal type (casparser uses this for amounts)
    try:
        from decimal import Decimal
        if isinstance(obj, Decimal):
            return float(obj)
    except ImportError:
        pass
    # For objects with __dict__
    if hasattr(obj, '__dict__'):
        return {k: _to_dict(v) for k, v in obj.__dict__.items() if not k.startswith('_')}
    # Fallback - try to convert to float if it looks numeric
    try:
        return float(obj)
    except (ValueError, TypeError):
        pass
    return str(obj)


class CASService:
    """Service for parsing CAS PDF files and extracting transaction data."""
    
    def __init__(self):
        if not CASPARSER_AVAILABLE:
            logger.warning("CASService initialized but casparser is not available.")
    
    def parse_cas_pdf(self, file_bytes: bytes, password: str) -> Dict[str, Any]:
        """
        Parse a CAS PDF file and return structured data.
        
        Args:
            file_bytes: Raw bytes of the PDF file
            password: PDF password (usually PAN + DOB or custom)
            
        Returns:
            dict: Parsed CAS data with investor info and folios
            
        Raises:
            ValueError: If casparser is not available or parsing fails
        """
        if not CASPARSER_AVAILABLE:
            raise ValueError("casparser library is not installed. Please run: pip install casparser[mupdf]")
        
        # Write bytes to temp file (casparser requires file path)
        temp_file = None
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
            temp_file.write(file_bytes)
            temp_file.close()
            
            # Parse CAS - casparser returns CASData object
            cas_data = casparser.read_cas_pdf(temp_file.name, password)
            
            if not cas_data:
                raise ValueError("Failed to parse CAS PDF. Please check the file and password.")
            
            # Convert CASData object to dict
            data = _to_dict(cas_data)
            
            return data
            
        except Exception as e:
            error_msg = str(e)
            if "password" in error_msg.lower() or "decrypt" in error_msg.lower():
                raise ValueError("Invalid password. Try PAN + DOB (DDMMYYYY) or the one you set.")
            elif "pdf" in error_msg.lower():
                raise ValueError("Invalid or corrupted PDF file.")
            else:
                logger.error(f"CAS parsing error: {e}")
                raise ValueError(f"Failed to parse CAS: {error_msg}")
        finally:
            # Cleanup temp file
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def extract_schemes(self, cas_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract all schemes from parsed CAS data.
        
        Args:
            cas_data: Parsed CAS data from parse_cas_pdf
            
        Returns:
            list: List of schemes with name, isin, amfi, valuation data, and transaction count
        """
        schemes = []
        
        # Handle both dict formats - folios might be under different keys
        folios = cas_data.get("folios", [])
        if not folios:
            folios = cas_data.get("cas_data", {}).get("folios", [])
        
        for folio in folios:
            amc = folio.get("amc", "Unknown AMC")
            
            folio_schemes = folio.get("schemes", [])
            for scheme in folio_schemes:
                scheme_name = scheme.get("scheme", "") or scheme.get("scheme_name", "Unknown Scheme")
                isin = scheme.get("isin", "")
                amfi = scheme.get("amfi", "") or scheme.get("amfi_code", "")
                transactions = scheme.get("transactions", [])
                
                # Get valuation data (includes Total Cost Value from CAS)
                valuation = scheme.get("valuation", {}) or {}
                cost_value = valuation.get("cost")  # Total Cost Value (includes stamp duty)
                nav = valuation.get("nav")
                market_value = valuation.get("value")
                
                # Get close balance (total units)
                close_units = scheme.get("close")  # Closing unit balance
                
                # Filter only purchase transactions (positive units)
                purchase_txns = []
                for t in transactions:
                    try:
                        units_val = float(t.get("units", 0) or 0)
                        amount_val = float(t.get("amount", 0) or 0)
                        if units_val > 0 and amount_val > 0:
                            purchase_txns.append(t)
                    except (ValueError, TypeError):
                        continue
                
                schemes.append({
                    "name": scheme_name,
                    "amc": amc,
                    "isin": isin,
                    "amfi": amfi,
                    "folio": folio.get("folio", ""),
                    "transaction_count": len(purchase_txns),
                    "total_transactions": len(transactions),
                    # Valuation data from CAS
                    "cost_value": float(cost_value) if cost_value else None,  # Total Cost Value (₹2,200.00)
                    "nav": float(nav) if nav else None,
                    "market_value": float(market_value) if market_value else None,
                    "close_units": float(close_units) if close_units else None
                })
        
        return schemes
    
    def extract_transactions_for_scheme(
        self, 
        cas_data: Dict[str, Any], 
        scheme_filter: str = None,
        isin_filter: str = None,
        sip_day: int = None  # SIP day for current month detection
    ) -> Dict[str, Any]:
        """
        Extract purchase transactions for a specific scheme.
        
        Uses raw amounts from CAS (no stamp duty calculation needed).
        The CAS's 'Total Cost Value' already includes stamp duty, so we just
        need to match the sum of individual transactions to that value.
        
        Args:
            cas_data: Parsed CAS data
            scheme_filter: Partial scheme name to filter (case-insensitive)
            isin_filter: ISIN to filter by
            sip_day: SIP day of month (for detecting missing current month installment)
            
        Returns:
            dict with:
                - transactions: List of transactions with date, amount, units, nav
                - cost_value: Total Cost Value from CAS (includes stamp duty)
                - close_units: Total units from CAS
                - missing_current_month: True if current month SIP is missing
                - pending_installment: Pending installment for current month (if any)
        """
        transactions = []
        scheme_valuation = {}
        
        # Handle both dict formats
        folios = cas_data.get("folios", [])
        if not folios:
            folios = cas_data.get("cas_data", {}).get("folios", [])
        
        for folio in folios:
            folio_schemes = folio.get("schemes", [])
            for scheme in folio_schemes:
                scheme_name = scheme.get("scheme", "") or scheme.get("scheme_name", "")
                isin = scheme.get("isin", "")
                
                # Apply filters
                if isin_filter:
                    if isin != isin_filter:
                        continue
                elif scheme_filter:
                    if scheme_filter.lower() not in scheme_name.lower():
                        continue
                
                # Get valuation data from scheme
                valuation = scheme.get("valuation", {}) or {}
                scheme_valuation = {
                    "cost_value": float(valuation.get("cost") or 0) if valuation.get("cost") else None,
                    "nav": float(valuation.get("nav") or 0) if valuation.get("nav") else None,
                    "market_value": float(valuation.get("value") or 0) if valuation.get("value") else None,
                    "close_units": float(scheme.get("close") or 0) if scheme.get("close") else None
                }
                
                # Extract transactions
                for txn in scheme.get("transactions", []):
                    try:
                        units = float(txn.get("units", 0) or 0)
                        amount = float(txn.get("amount", 0) or 0)
                        nav = float(txn.get("nav", 0) or 0)
                    except (ValueError, TypeError):
                        continue
                    
                    # Only include purchase transactions (positive units and amount)
                    if units > 0 and amount > 0:
                        # Parse date
                        txn_date = txn.get("date")
                        if txn_date:
                            # Convert to DD-MM-YYYY format
                            if isinstance(txn_date, datetime):
                                date_str = txn_date.strftime("%d-%m-%Y")
                            elif isinstance(txn_date, date):
                                date_str = txn_date.strftime("%d-%m-%Y")
                            elif isinstance(txn_date, str):
                                # Try different formats
                                try:
                                    if 'T' in txn_date:
                                        dt = datetime.fromisoformat(txn_date.split('T')[0])
                                    elif '-' in txn_date and len(txn_date.split('-')[0]) == 4:
                                        dt = datetime.strptime(txn_date[:10], "%Y-%m-%d")
                                    else:
                                        date_str = txn_date
                                        dt = None
                                    if dt:
                                        date_str = dt.strftime("%d-%m-%Y")
                                except:
                                    date_str = str(txn_date)
                            else:
                                continue
                        else:
                            continue
                        
                        # Use raw amount from CAS (don't add stamp duty - CAS already tracked it)
                        # The valuation.cost already includes all stamp duties
                        transactions.append({
                            "date": date_str,
                            "amount": round(float(amount), 2),  # Raw amount from CAS
                            "units": round(float(units), 4),
                            "nav": round(float(nav), 4) if nav else None,
                            "description": txn.get("description", "") or txn.get("type", ""),
                            "status": "PAID"  # CAS transactions are already paid
                        })
        
        # Sort by date (oldest first)
        try:
            transactions.sort(key=lambda x: datetime.strptime(x["date"], "%d-%m-%Y"))
        except:
            pass  # Keep original order if sorting fails
        
        # === SMART CURRENT MONTH HANDLING ===
        # If CAS doesn't have this month's installment but SIP date has passed, add a PENDING one
        missing_current_month = False
        pending_installment = None
        
        if sip_day and transactions:
            today = date.today()
            current_month_sip_date = None
            
            try:
                # Calculate this month's SIP date
                current_month_sip_date = today.replace(day=sip_day)
            except ValueError:
                # Invalid day for this month (e.g., Feb 31), use last day
                import calendar
                last_day = calendar.monthrange(today.year, today.month)[1]
                current_month_sip_date = today.replace(day=min(sip_day, last_day))
            
            # Check if SIP date has passed this month
            if current_month_sip_date and today >= current_month_sip_date:
                # Check if this month's SIP is already in CAS
                current_month_sip_str = current_month_sip_date.strftime("%d-%m-%Y")
                current_month_found = False
                
                for txn in transactions:
                    try:
                        txn_dt = datetime.strptime(txn["date"], "%d-%m-%Y").date()
                        if txn_dt.year == today.year and txn_dt.month == today.month:
                            current_month_found = True
                            break
                    except:
                        continue
                
                if not current_month_found:
                    # Current month's SIP is missing from CAS
                    missing_current_month = True
                    
                    # Get the last known SIP amount
                    last_sip_amount = transactions[-1]["amount"] if transactions else 0
                    
                    pending_installment = {
                        "date": current_month_sip_str,
                        "amount": last_sip_amount,  # Use last known amount
                        "units": None,
                        "nav": None,
                        "status": "PENDING",  # Needs user confirmation
                        "description": "Pending - confirm if paid"
                    }
        
        return {
            "transactions": transactions,
            "cost_value": scheme_valuation.get("cost_value"),  # Total Cost Value from CAS
            "close_units": scheme_valuation.get("close_units"),  # Total units from CAS
            "nav": scheme_valuation.get("nav"),
            "market_value": scheme_valuation.get("market_value"),
            "missing_current_month": missing_current_month,
            "pending_installment": pending_installment
        }
    
    def get_investor_info(self, cas_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract investor information from CAS data."""
        investor = cas_data.get("investor_info", {}) or {}
        period = cas_data.get("statement_period", {}) or {}
        
        return {
            "name": investor.get("name", "") or "",
            "email": investor.get("email", "") or "",
            "pan": investor.get("pan", "") or "",
            "period_from": str(period.get("from", "") or ""),
            "period_to": str(period.get("to", "") or "")
        }


# Singleton instance
cas_service = CASService()
