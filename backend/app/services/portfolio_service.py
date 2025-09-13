from typing import List, Dict, Optional
from datetime import datetime, date
from ..models.portfolio import Portfolio, Holding, NAVHistory, PortfolioSummary
from ..database import get_database
from .market_data import MarketDataService
from .ticker_mapping import TickerMapper
import logging
from bson import ObjectId

logger = logging.getLogger(__name__)

class PortfolioService:
    
    def __init__(self):
        self.market_service = MarketDataService()
        self.ticker_mapper = TickerMapper()
    
    async def create_portfolio(self, user_id: str, portfolio_data: dict, holdings: List[Dict]) -> str:
        """Create a new portfolio with holdings"""
        try:
            db = await get_database()
            
            # Map ISINs to tickers
            isins = [h['isin'] for h in holdings]
            ticker_mapping = await self.ticker_mapper.bulk_map_isins(isins)
            
            # Add ticker information to holdings
            processed_holdings = []
            for holding in holdings:
                holding_dict = holding.copy()
                holding_dict['ticker'] = ticker_mapping.get(holding['isin'])
                processed_holdings.append(holding_dict)
            
            # Get NAV at investment date
            nav_at_investment = None
            if portfolio_data.get('scheme_code'):
                nav_at_investment = await self.market_service.get_nav_from_amfi(
                    portfolio_data['scheme_code'], 
                    portfolio_data['investment_date']
                )
            
            # Calculate units if NAV is available
            units = None
            if nav_at_investment:
                units = portfolio_data['invested_amount'] / nav_at_investment
            
            # Create portfolio document
            portfolio_doc = {
                'user_id': user_id,
                'invested_amount': portfolio_data['invested_amount'],
                'investment_date': portfolio_data['investment_date'],
                'nav_at_investment': nav_at_investment,
                'units': units,
                'scheme_code': portfolio_data.get('scheme_code'),
                'scheme_name': portfolio_data.get('scheme_name'),
                'holdings': processed_holdings,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            
            result = await db.portfolios.insert_one(portfolio_doc)
            portfolio_id = str(result.inserted_id)
            
            # Calculate initial values
            await self.update_portfolio_values(portfolio_id)
            
            logger.info(f"Created portfolio {portfolio_id} for user {user_id}")
            return portfolio_id
            
        except Exception as e:
            logger.error(f"Error creating portfolio: {str(e)}")
            raise
    
    async def get_portfolio(self, portfolio_id: str, user_id: str) -> Optional[PortfolioSummary]:
        """Get portfolio with calculated values and history"""
        try:
            db = await get_database()
            
            # Get portfolio
            portfolio_doc = await db.portfolios.find_one({
                '_id': ObjectId(portfolio_id),
                'user_id': user_id
            })
            
            if not portfolio_doc:
                return None
            
            # Get NAV history
            nav_history = await db.nav_history.find({
                'portfolio_id': portfolio_id
            }).sort('date', -1).limit(30).to_list(30)
            
            # Calculate sector allocation
            top_sectors = self._calculate_sector_allocation(portfolio_doc.get('holdings', []))
            
            # Convert to Pydantic models
            portfolio_doc['id'] = str(portfolio_doc['_id'])
            portfolio = Portfolio(**portfolio_doc)
            
            nav_history_models = [NAVHistory(**doc) for doc in nav_history]
            
            return PortfolioSummary(
                portfolio=portfolio,
                nav_history=nav_history_models,
                total_holdings=len(portfolio.holdings),
                top_sectors=top_sectors
            )
            
        except Exception as e:
            logger.error(f"Error getting portfolio {portfolio_id}: {str(e)}")
            return None
    
    async def update_portfolio_values(self, portfolio_id: str):
        """Update portfolio current values and P&L"""
        try:
            db = await get_database()
            
            # Get portfolio
            portfolio_doc = await db.portfolios.find_one({'_id': ObjectId(portfolio_id)})
            if not portfolio_doc:
                return
            
            holdings = portfolio_doc.get('holdings', [])
            nav_at_investment = portfolio_doc.get('nav_at_investment')
            units = portfolio_doc.get('units')
            invested_amount = portfolio_doc.get('invested_amount')
            
            # Update holdings with current prices
            updated_holdings = []
            tickers = [h.get('ticker') for h in holdings if h.get('ticker')]
            
            if tickers:
                price_data = await self.market_service.get_live_stock_prices(tickers)
                
                for holding in holdings:
                    holding_copy = holding.copy()
                    ticker = holding.get('ticker')
                    
                    if ticker and ticker in price_data and price_data[ticker]:
                        holding_copy['current_price'] = price_data[ticker]['price']
                        holding_copy['price_change_percent'] = price_data[ticker]['change_percent']
                    
                    updated_holdings.append(holding_copy)
            else:
                updated_holdings = holdings
            
            # Calculate current NAV
            current_nav = nav_at_investment
            if nav_at_investment and updated_holdings:
                current_nav = await self.market_service.calculate_portfolio_nav(
                    updated_holdings, nav_at_investment
                )
            
            # Calculate current value and P&L
            current_value = None
            profit_loss = None
            profit_loss_percent = None
            
            if units and current_nav:
                current_value = units * current_nav
                profit_loss = current_value - invested_amount
                profit_loss_percent = (profit_loss / invested_amount) * 100
            
            # Update portfolio
            update_data = {
                'holdings': updated_holdings,
                'current_nav': current_nav,
                'current_value': current_value,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent,
                'updated_at': datetime.utcnow()
            }
            
            await db.portfolios.update_one(
                {'_id': ObjectId(portfolio_id)},
                {'$set': update_data}
            )
            
            # Save NAV history
            if current_nav and current_value is not None:
                nav_history_doc = {
                    'portfolio_id': portfolio_id,
                    'date': date.today(),
                    'nav': current_nav,
                    'current_value': current_value,
                    'pnl': profit_loss or 0,
                    'pnl_percent': profit_loss_percent or 0
                }
                
                # Upsert (update if exists for today, insert if not)
                await db.nav_history.update_one(
                    {'portfolio_id': portfolio_id, 'date': date.today()},
                    {'$set': nav_history_doc},
                    upsert=True
                )
            
            logger.info(f"Updated portfolio values for {portfolio_id}")
            
        except Exception as e:
            logger.error(f"Error updating portfolio values for {portfolio_id}: {str(e)}")
    
    async def get_user_portfolios(self, user_id: str) -> List[Portfolio]:
        """Get all portfolios for a user"""
        try:
            db = await get_database()
            
            portfolios = await db.portfolios.find({'user_id': user_id}).to_list(100)
            
            result = []
            for portfolio_doc in portfolios:
                portfolio_doc['id'] = str(portfolio_doc['_id'])
                result.append(Portfolio(**portfolio_doc))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting portfolios for user {user_id}: {str(e)}")
            return []
    
    def _calculate_sector_allocation(self, holdings: List[Dict]) -> Dict[str, float]:
        """Calculate sector-wise allocation"""
        sector_allocation = {}
        
        for holding in holdings:
            sector = holding.get('industry', 'Unknown')
            percentage = holding.get('percentage_to_nav', 0)
            
            if sector in sector_allocation:
                sector_allocation[sector] += percentage
            else:
                sector_allocation[sector] = percentage
        
        # Sort by allocation and return top 10
        sorted_sectors = sorted(sector_allocation.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_sectors[:10])