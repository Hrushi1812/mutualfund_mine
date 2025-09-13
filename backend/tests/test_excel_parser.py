import pytest
import pandas as pd
import io
from app.services.excel_parser import ExcelParser
from fastapi import HTTPException

class TestExcelParser:
    
    @pytest.mark.asyncio
    async def test_parse_valid_excel_file(self, sample_excel_file):
        """Test parsing a valid Excel file"""
        parser = ExcelParser()
        
        holdings = await parser.parse_amc_disclosure(sample_excel_file, "test.xlsx")
        
        assert len(holdings) == 3
        assert holdings[0]['isin'] == 'INE002A01018'
        assert holdings[0]['instrument_name'] == 'Reliance Industries Ltd'
        assert holdings[0]['industry'] == 'Oil & Gas'
        assert holdings[0]['quantity'] == 1000.0
        assert holdings[0]['market_value_lakhs'] == 25.5
        assert holdings[0]['percentage_to_nav'] == 15.2
    
    @pytest.mark.asyncio
    async def test_parse_csv_file(self):
        """Test parsing a CSV file"""
        csv_data = """ISIN,Instrument Name,Industry,Quantity,Market Value (lakhs),% to NAV
INE002A01018,Reliance Industries Ltd,Oil & Gas,1000.0,25.5,15.2
INE009A01021,Infosys Ltd,Information Technology,500.0,18.3,10.9"""
        
        csv_bytes = csv_data.encode('utf-8')
        parser = ExcelParser()
        
        holdings = await parser.parse_amc_disclosure(csv_bytes, "test.csv")
        
        assert len(holdings) == 2
        assert holdings[0]['isin'] == 'INE002A01018'
    
    @pytest.mark.asyncio
    async def test_parse_file_with_missing_columns(self):
        """Test parsing file with missing required columns"""
        data = {
            'ISIN': ['INE002A01018'],
            'Company Name': ['Reliance Industries Ltd'],
            # Missing Industry, Quantity, etc.
        }
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        
        parser = ExcelParser()
        
        with pytest.raises(HTTPException) as exc_info:
            await parser.parse_amc_disclosure(buffer.getvalue(), "invalid.xlsx")
        
        assert exc_info.value.status_code == 400
        assert "Missing required columns" in str(exc_info.value.detail)
    
    @pytest.mark.asyncio
    async def test_parse_file_with_column_variations(self):
        """Test parsing file with different column name variations"""
        data = {
            'ISIN Code': ['INE002A01018'],  # Variation of ISIN
            'Company Name': ['Reliance Industries Ltd'],  # Variation of Instrument Name
            'Sector': ['Oil & Gas'],  # Variation of Industry
            'Qty': [1000.0],  # Variation of Quantity
            'Value (Rs. Lakhs)': [25.5],  # Variation of Market Value
            'Weight (%)': [15.2]  # Variation of % to NAV
        }
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        
        parser = ExcelParser()
        holdings = await parser.parse_amc_disclosure(buffer.getvalue(), "variations.xlsx")
        
        assert len(holdings) == 1
        assert holdings[0]['isin'] == 'INE002A01018'
        assert holdings[0]['instrument_name'] == 'Reliance Industries Ltd'
    
    @pytest.mark.asyncio
    async def test_parse_file_with_invalid_data_types(self):
        """Test parsing file with invalid numeric data"""
        data = {
            'ISIN': ['INE002A01018', 'INE009A01021'],
            'Instrument Name': ['Reliance Industries Ltd', 'Infosys Ltd'],
            'Industry': ['Oil & Gas', 'IT'],
            'Quantity': ['invalid', 500.0],  # Invalid quantity
            'Market Value (lakhs)': [25.5, 'invalid'],  # Invalid market value
            '% to NAV': [15.2, 10.9]
        }
        df = pd.DataFrame(data)
        buffer = io.BytesIO()
        df.to_excel(buffer, index=False)
        buffer.seek(0)
        
        parser = ExcelParser()
        holdings = await parser.parse_amc_disclosure(buffer.getvalue(), "invalid_data.xlsx")
        
        # Should filter out rows with invalid data
        assert len(holdings) == 0  # Both rows have some invalid data
    
    def test_validate_holdings_data(self, sample_holdings_data):
        """Test holdings data validation"""
        parser = ExcelParser()
        
        # Valid data
        assert parser.validate_holdings_data(sample_holdings_data) == True
        
        # Empty data
        assert parser.validate_holdings_data([]) == False
        
        # Data with incorrect total percentage
        invalid_data = [
            {"percentage_to_nav": 50.0},
            {"percentage_to_nav": 20.0}  # Total = 70%, should be ~100%
        ]
        # Should still return True but log warning
        assert parser.validate_holdings_data(invalid_data) == True