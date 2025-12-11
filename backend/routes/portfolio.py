from fastapi import APIRouter, Depends, Form
from services.nav_service import nav_service
from routes.auth import get_current_user

router = APIRouter(tags=["Portfolio"])

@router.post("/analyze-portfolio")
async def analyze_portfolio(
    fund_id: str = Form(...),
    investment_amount: float = Form(None),
    investment_date: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    return nav_service.calculate_pnl(fund_id, user_id, investment_amount, investment_date)
