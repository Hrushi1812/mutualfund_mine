import asyncio
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class TickerMapper:
    
    def __init__(self):
        self.static_mapping = {
            'INE002A01018': 'RELIANCE.NS',
            'INE009A01021': 'INFY.NS',
            'INE467B01029': 'TCS.NS',
            'INE040A01034': 'HDFCBANK.NS',
            'INE030A01027': 'ICICIBANK.NS',
            'INE019A01038': 'ITC.NS',
            'INE062A01020': 'BHARTIARTL.NS',
            'INE001A01036': 'HINDUNILVR.NS',
        }
    
    async def get_ticker_from_isin(self, isin: str) -> Optional[str]:
        if isin in self.static_mapping:
            return self.static_mapping[isin]
        logger.warning(f"No ticker mapping found for ISIN: {isin}")
        return None
    
    async def bulk_map_isins(self, isins: list) -> Dict[str, Optional[str]]:
        tasks = [self.get_ticker_from_isin(isin) for isin in isins]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        mapping = {}
        for isin, result in zip(isins, results):
            if isinstance(result, Exception):
                mapping[isin] = None
            else:
                mapping[isin] = result
        return mapping