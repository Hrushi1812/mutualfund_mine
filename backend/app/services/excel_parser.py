import pandas as pd
import io
from typing import List, Dict, Any
from fastapi import HTTPException
import logging

logger = logging.getLogger(__name__)

class ExcelParser:
    
    @staticmethod
    async def parse_amc_disclosure(file_content: bytes, filename: str) -> List[Dict[str, Any]]:
        try:
            if filename.endswith('.csv'):
                df = pd.read_csv(io.BytesIO(file_content))
            else:
                df = pd.read_excel(io.BytesIO(file_content))
            
            df.columns = df.columns.str.strip()
            
            column_mapping = {
                'ISIN': ['ISIN', 'ISIN Code', 'ISIN_CODE'],
                'Instrument Name': ['Instrument Name', 'Company Name', 'Security Name', 'Name'],
                'Industry': ['Industry', 'Sector', 'Industry/Sector'],
                'Quantity': ['Quantity', 'Qty', 'No. of Shares'],
                'Market Value (lakhs)': ['Market Value (lakhs)', 'Market Value', 'Value (Rs. Lakhs)', 'Market Value (Rs. Lakhs)'],
                '% to NAV': ['% to NAV', 'Percentage to NAV', '% of NAV', 'Weight (%)']
            }
            
            for standard_name, variations in column_mapping.items():
                for variation in variations:
                    if variation in df.columns:
                        df.rename(columns={variation: standard_name}, inplace=True)
                        break
            
            required_columns = ['ISIN', 'Instrument Name', 'Industry', 'Quantity', 'Market Value (lakhs)', '% to NAV']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Missing required columns: {missing_columns}. Available columns: {list(df.columns)}"
                )
            
            df = df.dropna(subset=['ISIN', 'Instrument Name'])
            df['ISIN'] = df['ISIN'].astype(str).str.strip()
            df['Instrument Name'] = df['Instrument Name'].astype(str).str.strip()
            df['Industry'] = df['Industry'].astype(str).str.strip()
            
            numeric_columns = ['Quantity', 'Market Value (lakhs)', '% to NAV']
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
            
            df = df.dropna(subset=numeric_columns)
            
            holdings = []
            for _, row in df.iterrows():
                holding = {
                    'isin': row['ISIN'],
                    'instrument_name': row['Instrument Name'],
                    'industry': row['Industry'],
                    'quantity': float(row['Quantity']),
                    'market_value_lakhs': float(row['Market Value (lakhs)']),
                    'percentage_to_nav': float(row['% to NAV'])
                }
                holdings.append(holding)
            
            logger.info(f"Parsed {len(holdings)} holdings from {filename}")
            return holdings
            
        except Exception as e:
            logger.error(f"Error parsing Excel file {filename}: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Error parsing Excel file: {str(e)}")