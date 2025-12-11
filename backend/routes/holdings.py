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
    invested_amount: str = Form(None),
    invested_date: str = Form(None), # YYYY-MM-DD
    nickname: str = Form(None),
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    
    # 1. Validate File Type
    if not file.filename.lower().endswith(('.xls', '.xlsx')):
        raise HTTPException(400, "Invalid file format. Please upload an Excel file (.xls, .xlsx).")

    # 2. Validate Amount
    amount_float = None
    if invested_amount and invested_amount.strip():
        try:
            amount_float = float(invested_amount)
            if amount_float <= 0:
                raise ValueError
        except:
            raise HTTPException(422, "Invested amount must be a positive number.")

    # 3. Validate Date
    if invested_date and invested_date.strip():
        # strict YYYY-MM-DD check
        import re
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", invested_date):
             raise HTTPException(422, "Invalid date format. Use YYYY-MM-DD.")
    
    # Process
    save_result = holdings_service.process_and_save_holdings(
        fund_name, file, user_id, scheme_code, amount_float, invested_date, nickname
    )
    
    if "error" in save_result and save_result["error"] != "No valid holdings resolved.":
         pass 

    analysis = None
        
    if amount_float and invested_date and save_result.get("id"):
        analysis = nav_service.calculate_pnl(save_result["id"], user_id, amount_float, invested_date)

    return {
        "upload_status": save_result,
        "analysis": analysis,
        "scheme_code_used": scheme_code
    }
