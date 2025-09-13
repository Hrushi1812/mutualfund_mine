import pytest
from app.services.ticker_mapping import TickerMapper

class TestTickerMapping:
    
    @pytest.mark.asyncio
    async def test_get_ticker_from_known_isin(self):
        """Test mapping known ISIN to ticker"""
        mapper = TickerMapper()
        
        ticker = await mapper.get_ticker_from_isin("INE002A01018")
        assert ticker == "RELIANCE.NS"
        
        ticker = await mapper.get_ticker_from_isin("INE009A01021")
        assert ticker == "INFY.NS"
    
    @pytest.mark.asyncio
    async def test_get_ticker_from_unknown_isin(self):
        """Test mapping unknown ISIN"""
        mapper = TickerMapper()
        
        ticker = await mapper.get_ticker_from_isin("UNKNOWN123456")
        assert ticker is None
    
    @pytest.mark.asyncio
    async def test_bulk_map_isins(self):
        """Test bulk mapping of ISINs"""
        mapper = TickerMapper()
        
        isins = ["INE002A01018", "INE009A01021", "UNKNOWN123456"]
        mapping = await mapper.bulk_map_isins(isins)
        
        assert mapping["INE002A01018"] == "RELIANCE.NS"
        assert mapping["INE009A01021"] == "INFY.NS"
        assert mapping["UNKNOWN123456"] is None
    
    def test_add_static_mapping(self):
        """Test adding new static mapping"""
        mapper = TickerMapper()
        
        # Add new mapping
        mapper.add_static_mapping("TEST123456", "TEST.NS")
        
        # Verify it was added
        assert mapper.static_mapping["TEST123456"] == "TEST.NS"