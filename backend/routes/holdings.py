from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from services.holdings_service import holdings_service
from services.nav_service import nav_service
from services.auth_service import AuthService
from routes.auth import get_current_user

router = APIRouter(tags=["Holdings"])

@router.get("/funds/")
def view_funds(current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    return {"funds_available": holdings_service.list_funds(user_id)}

@router.delete("/funds/{fund_id}")
def remove_fund(fund_id: str, current_user: dict = Depends(get_current_user)):
    user_id = str(current_user["_id"])
    success = holdings_service.delete_fund(fund_id, user_id)
    if success:
        return {"message": f"Deleted fund {fund_id}"}
    return {"error": "Fund not found"}, 404

@router.post("/upload-holdings/")
async def upload(
    fund_name: str = Form(..., min_length=1),
    scheme_code: str = Form(None),
    file: UploadFile = File(...),
    invested_amount: str = Form(...),
    invested_date: str = Form(...), # DD-MM-YYYY
    nickname: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    
    # 1. Validate File Type
    if not file.filename.lower().endswith(('.xls', '.xlsx')):
        raise HTTPException(400, "Invalid file format. Please upload an Excel file (.xls, .xlsx).")

    # 2. Validate Amount
    if not invested_amount or not invested_amount.strip():
        raise HTTPException(422, "Invested amount is required.")
    
    try:
        amount_float = float(invested_amount)
        if amount_float <= 0:
            raise ValueError
    except:
        raise HTTPException(422, "Invested amount must be a positive number.")

    # 3. Validate Date
    if not invested_date or not invested_date.strip():
        raise HTTPException(422, "Invested date is required.")
        
    # strict DD-MM-YYYY check
    import re
    if not re.match(r"^\d{2}-\d{2}-\d{4}$", invested_date):
            raise HTTPException(422, "Invalid date format. Use DD-MM-YYYY.")
    
    # Process
    save_result = holdings_service.process_and_save_holdings(
        fund_name, file, user_id, scheme_code, amount_float, invested_date, nickname
    )
    
    if "error" in save_result:
         raise HTTPException(400, save_result["error"]) 

    analysis = None
        
    if save_result.get("id"):
        analysis = nav_service.calculate_pnl(save_result["id"], user_id, amount_float, invested_date)

    return {
        "upload_status": save_result,
        "analysis": analysis,
        "scheme_code_used": scheme_code
    }
from pydantic import BaseModel

class SchemeUpdate(BaseModel):
    scheme_code: str

@router.patch("/funds/{fund_id}/scheme")
def update_scheme(
    fund_id: str, 
    payload: SchemeUpdate,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    success = holdings_service.update_fund_scheme(fund_id, user_id, payload.scheme_code)
    
    if not success:
         raise HTTPException(404, "Fund not found or update failed.")
         
    # Re-trigger analysis since we now have the correct code
    # We might need to fetch the doc again to get investment details
    # But NavService.calculate_pnl handles fetching doc by ID.
    
    # We intentionally pass None for investment/date to use stored values
    analysis = nav_service.calculate_pnl(fund_id, user_id)
    
    return {
        "message": "Scheme updated successfully",
        "analysis": analysis
    }
