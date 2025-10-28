"""
Advanced Authentication endpoints with refresh tokens
"""

from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel
import structlog

from app.core.security import (
    verify_password, create_token_pair, refresh_access_token,
    revoke_refresh_token, revoke_all_user_tokens, get_current_user_from_token,
    security, cleanup_expired_tokens
)

logger = structlog.get_logger()

router = APIRouter(prefix="/auth", tags=["Authentication Advanced"])


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int


class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int


@router.post("/login", response_model=TokenResponse)
async def login_with_refresh(login_data: LoginRequest):
    """
    Enhanced login with refresh token support
    """
    try:
        # Mock user validation (replace with actual database lookup)
        if login_data.email in ["admin@levitiis.com", "admin"] and login_data.password == "admin123":
            user_data = {
                "sub": "admin_user_id",
                "email": login_data.email,
                "role": "admin",
                "permissions": ["read", "write", "admin"]
            }
            
            # Create token pair
            tokens = create_token_pair(user_data)
            
            logger.info(f"User {login_data.email} logged in successfully")
            
            return TokenResponse(**tokens)
        else:
            logger.warning(f"Failed login attempt for {login_data.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )
            
    except HTTPException:
        # Propagate HTTP exceptions (e.g., 401) so they aren't converted to 500
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(refresh_data: RefreshTokenRequest):
    """
    Refresh access token using refresh token
    """
    try:
        new_tokens = refresh_access_token(refresh_data.refresh_token)
        
        if not new_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
            
        logger.info("Access token refreshed successfully")
        return RefreshResponse(**new_tokens)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token refresh error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )


@router.post("/logout")
async def logout(
    refresh_data: RefreshTokenRequest,
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Logout and revoke refresh token
    """
    try:
        success = revoke_refresh_token(refresh_data.refresh_token)
        
        if success:
            logger.info(f"User {current_user.get('email')} logged out successfully")
            return {"message": "Logged out successfully"}
        else:
            logger.warning("Failed to revoke refresh token during logout")
            return {"message": "Logout completed, but token revocation failed"}
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )


@router.post("/logout-all")
async def logout_all_devices(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Logout from all devices (revoke all refresh tokens)
    """
    try:
        user_id = current_user.get("sub")
        revoked_count = revoke_all_user_tokens(user_id)
        
        logger.info(f"User {current_user.get('email')} logged out from all devices")
        return {
            "message": f"Logged out from all devices successfully",
            "revoked_tokens": revoked_count
        }
        
    except Exception as e:
        logger.error(f"Logout all error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout from all devices failed"
        )


@router.get("/me")
async def get_current_user(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Get current user information from token
    """
    try:
        # Remove sensitive token data
        user_info = {
            "user_id": current_user.get("sub"),
            "email": current_user.get("email"),
            "role": current_user.get("role"),
            "permissions": current_user.get("permissions", [])
        }
        
        return user_info
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get user information"
        )


@router.post("/cleanup-tokens")
async def cleanup_expired_tokens_endpoint(
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Admin endpoint to cleanup expired tokens
    """
    try:
        # Check if user has admin permissions
        if current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
            
        cleanup_expired_tokens()
        
        logger.info("Token cleanup completed by admin")
        return {"message": "Expired tokens cleaned up successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Token cleanup error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token cleanup failed"
        )


@router.get("/token-info")
async def get_token_info(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get information about the current token
    """
    try:
        from app.core.security import verify_token
        import jwt
        from app.core.config import settings
        
        token = credentials.credentials
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        token_info = {
            "token_type": payload.get("type"),
            "issued_at": payload.get("iat"),
            "expires_at": payload.get("exp"),
            "token_id": payload.get("jti"),
            "user_id": payload.get("sub")
        }
        
        return token_info
        
    except Exception as e:
        logger.error(f"Token info error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )