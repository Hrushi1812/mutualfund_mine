"""
Fyers API Routes - OAuth callback and token management
"""
from fastapi import APIRouter, Query, HTTPException
from fastapi.responses import HTMLResponse
from services.fyers_service import fyers_service
from core.logging import get_logger

logger = get_logger("FyersRoutes")

router = APIRouter(prefix="/api/fyers", tags=["fyers"])


@router.get("/auth-url")
def get_auth_url():
    """
    Get the Fyers OAuth authorization URL.
    User should visit this URL in browser to authorize.
    """
    if not fyers_service.secret_key:
        raise HTTPException(status_code=500, detail="FYERS_SECRET_KEY not configured")
    
    url = fyers_service.get_auth_url()
    return {
        "auth_url": url,
        "instructions": "Visit this URL in your browser, login with Fyers credentials, and you'll be redirected back with an auth_code"
    }


@router.get("/callback")
def fyers_callback(
    auth_code: str = Query(None, alias="auth_code"),
    code: str = Query(None),  # Fyers sometimes uses 'code' instead
    s: str = Query(None),     # Status
):
    """
    OAuth callback endpoint. Fyers redirects here after user authorization.
    Exchanges auth_code for access_token.
    """
    # Fyers may send code as 'auth_code' or 'code'
    final_code = auth_code or code
    
    if not final_code:
        return HTMLResponse(content="""
            <html>
            <head><title>Fyers Auth Failed</title></head>
            <body>
                <h2>❌ Authorization Failed</h2>
                <p>No auth_code received. Please try again.</p>
                <a href="/api/fyers/auth-url">Get Auth URL</a>
            </body>
            </html>
        """, status_code=400)
    
    success = fyers_service.generate_token(final_code)
    
    if success:
        return HTMLResponse(content="""
            <html>
            <head><title>Fyers Auth Success</title></head>
            <body>
                <h2>✅ Authorization Successful!</h2>
                <p>Fyers API is now connected. You can close this window.</p>
                <p>Token is valid for ~24 hours.</p>
            </body>
            </html>
        """)
    else:
        return HTMLResponse(content="""
            <html>
            <head><title>Fyers Auth Failed</title></head>
            <body>
                <h2>❌ Token Generation Failed</h2>
                <p>Could not exchange auth_code for token. Please try again.</p>
                <a href="/api/fyers/auth-url">Get Auth URL</a>
            </body>
            </html>
        """, status_code=400)


@router.get("/status")
def get_fyers_status():
    """Check if Fyers API is authenticated and working."""
    is_auth = fyers_service.is_authenticated()
    
    return {
        "authenticated": is_auth,
        "app_id": fyers_service.app_id,
        "token_expiry": fyers_service._token_expiry.isoformat() if fyers_service._token_expiry else None,
        "message": "Ready" if is_auth else "Not authenticated. Visit /api/fyers/auth-url to connect."
    }


@router.post("/set-token")
def set_token_manually(access_token: str):
    """
    Manually set an access token (for advanced users who generate token externally).
    """
    fyers_service.set_token_directly(access_token)
    return {"success": True, "message": "Token set successfully"}


@router.get("/test-quote")
def test_quote(symbol: str = "RELIANCE"):
    """Test fetching a live quote."""
    if not fyers_service.is_authenticated():
        raise HTTPException(status_code=401, detail="Fyers not authenticated")
    
    quotes = fyers_service.get_quotes([symbol])
    if symbol.upper() in quotes:
        return {"symbol": symbol, "data": quotes[symbol.upper()]}
    return {"symbol": symbol, "data": None, "error": "Quote not found"}
