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
    invested_amount: str = Form(None), # Optional for SIP (derived) or Lumpsum
    invested_date: str = Form(...), # DD-MM-YYYY (Start Date for SIP)
    nickname: str = Form(None),
    # SIP Fields
    investment_type: str = Form("lumpsum"), # lumpsum, sip
    sip_amount: str = Form(None),
    sip_day: str = Form(None),
    total_units: str = Form(None),
    total_invested_amount: str = Form(None),  # CAS Invested Amount
    # Step-Up SIP Fields
    stepup_enabled: str = Form("false"),  # "true" or "false"
    stepup_type: str = Form("percentage"),  # "percentage" or "amount"
    stepup_value: str = Form(None),  # e.g., "10" for 10% or "500" for ₹500
    stepup_frequency: str = Form("Annual"),  # "Annual", "Half-Yearly", "Quarterly"
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    
    # 1. Validate File Type
    if not file.filename.lower().endswith(('.xls', '.xlsx')):
        raise HTTPException(400, "Invalid file format. Please upload an Excel file (.xls, .xlsx).")

    # 2. Validate Amount
    amount_float = 0.0
    if investment_type == "lumpsum":
        if not invested_amount or not invested_amount.strip():
            raise HTTPException(422, "Invested amount is required for Lumpsum.")
        try:
            amount_float = float(invested_amount)
            if amount_float <= 0: raise ValueError
        except:
             raise HTTPException(422, "Invested amount must be a positive number.")
             
    # 3. Validate SIP Fields
    sip_amount_float = 0.0
    sip_day_int = None
    manual_total_units_float = 0.0
    
    if investment_type == "sip":
        if not sip_amount or not sip_amount.strip():
             raise HTTPException(422, "SIP Amount is required.")
        try:
            sip_amount_float = float(sip_amount)
            if sip_amount_float <= 0: raise ValueError
        except:
             raise HTTPException(422, "SIP Amount must be positive.")
             
        if not sip_day or not sip_day.strip():
             raise HTTPException(422, "SIP Day is required.")
        try:
            sip_day_int = int(sip_day)
            if not (1 <= sip_day_int <= 31): raise ValueError
        except:
             raise HTTPException(422, "SIP Day must be between 1 and 31.")
        
        # Total Units (Optional but recommended)
        if total_units and total_units.strip():
             try:
                 manual_total_units_float = float(total_units)
             except:
                 pass # Ignore invalid units, default 0

        # Total Invested Amount from CAS (Mandatory for correct P&L)
        manual_invested_amount_float = 0.0
        if total_invested_amount and total_invested_amount.strip():
            try:
                manual_invested_amount_float = float(total_invested_amount)
            except:
                pass  # Ignore invalid, default 0

    # 4. Validate Date
    if not invested_date or not invested_date.strip():
        raise HTTPException(422, "Invested date is required.")
        
    # strict DD-MM-YYYY check
    import re
    if not re.match(r"^\d{2}-\d{2}-\d{4}$", invested_date):
            raise HTTPException(422, "Invalid date format. Use DD-MM-YYYY.")
    
    # 5. Parse Step-Up Fields (only for SIP)
    stepup_enabled_bool = False
    stepup_value_float = None
    stepup_type_str = "percentage"
    stepup_frequency_str = "Annual"
    
    if investment_type == "sip":
        stepup_enabled_bool = stepup_enabled.lower() == "true"
        
        if stepup_enabled_bool:
            stepup_type_str = stepup_type if stepup_type in ["percentage", "amount"] else "percentage"
            stepup_frequency_str = stepup_frequency if stepup_frequency in ["Annual", "Half-Yearly", "Quarterly"] else "Annual"
            
            if stepup_value and stepup_value.strip():
                try:
                    stepup_value_float = float(stepup_value)
                    if stepup_value_float <= 0:
                        raise HTTPException(422, "Step-up value must be positive.")
                except ValueError:
                    raise HTTPException(422, "Step-up value must be a valid number.")
            else:
                raise HTTPException(422, "Step-up value is required when step-up is enabled.")
    
    # Process
    manual_invested_for_service = manual_invested_amount_float if investment_type == "sip" else 0.0
    save_result = holdings_service.process_and_save_holdings(
        fund_name, file, user_id, scheme_code, amount_float, invested_date, nickname,
        investment_type, sip_amount_float, sip_day_int, manual_total_units_float, manual_invested_for_service,
        stepup_enabled=stepup_enabled_bool,
        stepup_type=stepup_type_str,
        stepup_value=stepup_value_float,
        stepup_frequency=stepup_frequency_str
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

from models.db_schemas import SIPAction

@router.post("/funds/{fund_id}/sip-action")
def sip_action(
    fund_id: str,
    payload: SIPAction,
    current_user: dict = Depends(get_current_user)
):
    user_id = str(current_user["_id"])
    result = holdings_service.handle_sip_action(fund_id, user_id, payload.date, payload.action)
    
    if "error" in result:
        raise HTTPException(400, result["error"])
        
    return result
