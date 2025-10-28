
"""
Security utilities for authentication and authorization
"""

from datetime import datetime, timedelta
from typing import Optional, Union, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError
import bcrypt
from fastapi import HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog
import re
import html
import time
import secrets
import hashlib
import hmac
from functools import lru_cache

from app.core.config import settings

logger = structlog.get_logger()

# JWT Bearer token
security = HTTPBearer()

# In-memory store for refresh tokens (in production, use Redis)
_refresh_token_store = {}
_blacklisted_tokens = set()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash using bcrypt directly"""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'), 
            hashed_password.encode('utf-8')
        )
    except Exception as e:
        logger.error("Password verification failed", error=str(e))
        return False


def get_password_hash(password: str) -> str:
    """Generate password hash using bcrypt directly"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def generate_token_id() -> str:
    """Generate unique token ID for tracking"""
    return secrets.token_urlsafe(32)


def create_access_token(
    data: dict, 
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    # Add token metadata
    token_id = generate_token_id()
    to_encode.update({
        "exp": int(expire.timestamp()),
        "type": "access",
        "jti": token_id,  # JWT ID for tracking
        "iat": int(datetime.utcnow().timestamp())
    })
    
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: dict, user_id: str) -> str:
    """Create JWT refresh token with enhanced security"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )
    
    # Generate unique token ID
    token_id = generate_token_id()
    
    to_encode.update({
        "exp": int(expire.timestamp()),
        "type": "refresh",
        "jti": token_id,
        "iat": int(datetime.utcnow().timestamp())
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    # Store refresh token for validation (in production, use Redis)
    _refresh_token_store[token_id] = {
        "user_id": user_id,
        "created_at": datetime.utcnow(),
        "expires_at": expire,
        "is_active": True
    }
    
    return encoded_jwt


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify and decode JWT token with enhanced security"""
    try:
        # Add leeway to handle clock skew issues and disable iat validation
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            leeway=60,  # Allow 60 seconds tolerance for clock differences
            options={"verify_iat": False}  # Disable automatic iat validation
        )
        
        # Check token type
        if payload.get("type") != token_type:
            logger.warning(f"Invalid token type: expected {token_type}, got {payload.get('type')}")
            return None
            
        # Check if token is blacklisted
        token_id = payload.get("jti")
        if token_id and token_id in _blacklisted_tokens:
            logger.warning(f"Token {token_id} is blacklisted")
            return None
            
        # Additional validation for refresh tokens
        if token_type == "refresh" and token_id:
            token_info = _refresh_token_store.get(token_id)
            if not token_info or not token_info.get("is_active"):
                logger.warning(f"Refresh token {token_id} is not active")
                return None
                
        # Check expiration
        exp = payload.get("exp")
        if exp and datetime.utcnow().timestamp() > exp:
            logger.warning("Token has expired")
            return None
            
        return payload
        
    except InvalidTokenError as e:
        logger.warning(f"Token validation failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during token verification: {e}")
        return None


def revoke_refresh_token(token: str) -> bool:
    """Revoke a refresh token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        token_id = payload.get("jti")
        if token_id and token_id in _refresh_token_store:
            _refresh_token_store[token_id]["is_active"] = False
            _blacklisted_tokens.add(token_id)
            logger.info(f"Refresh token {token_id} revoked")
            return True
            
    except Exception as e:
        logger.error(f"Failed to revoke refresh token: {e}")
        
    return False


def revoke_all_user_tokens(user_id: str) -> int:
    """Revoke all refresh tokens for a user"""
    revoked_count = 0
    
    for token_id, token_info in _refresh_token_store.items():
        if token_info.get("user_id") == user_id and token_info.get("is_active"):
            token_info["is_active"] = False
            _blacklisted_tokens.add(token_id)
            revoked_count += 1
            
    logger.info(f"Revoked {revoked_count} tokens for user {user_id}")
    return revoked_count


def cleanup_expired_tokens():
    """Clean up expired tokens from memory"""
    current_time = datetime.utcnow()
    expired_tokens = []
    
    for token_id, token_info in _refresh_token_store.items():
        if token_info.get("expires_at", current_time) < current_time:
            expired_tokens.append(token_id)
            
    for token_id in expired_tokens:
        del _refresh_token_store[token_id]
        _blacklisted_tokens.discard(token_id)
        
    if expired_tokens:
        logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")


@lru_cache(maxsize=1000)
def get_token_hash(token: str) -> str:
    """Get hash of token for caching purposes"""
    return hashlib.sha256(token.encode()).hexdigest()


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """Extract current user from JWT token"""
    token = credentials.credentials
    
    payload = verify_token(token, "access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return payload


def create_token_pair(user_data: dict) -> Dict[str, str]:
    """Create both access and refresh tokens"""
    user_id = str(user_data.get("sub", user_data.get("user_id", "")))
    
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data, user_id)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


def refresh_access_token(refresh_token: str) -> Optional[Dict[str, str]]:
    """Generate new access token from refresh token"""
    payload = verify_token(refresh_token, "refresh")
    if not payload:
        return None
        
    # Create new access token with same user data
    user_data = {k: v for k, v in payload.items() 
                if k not in ["exp", "iat", "jti", "type"]}
    
    new_access_token = create_access_token(user_data)
    
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }


def get_current_user_id(credentials: HTTPAuthorizationCredentials) -> str:
    """Extract user ID from JWT token"""
    token = credentials.credentials
    payload = verify_token(token, "access")
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def check_permissions(user_role: str, required_permissions: list) -> bool:
    """Check if user has required permissions"""
    role_permissions = {
        "admin": ["read", "write", "delete", "admin"],
        "manager": ["read", "write"],
        "user": ["read"],
        "auditor": ["read", "audit"],
        "technician": ["read", "maintenance"]
    }
    
    user_permissions = role_permissions.get(user_role, [])
    return any(perm in user_permissions for perm in required_permissions)


# RBAC helpers aligned with roles: admin, gestor, auditor, agent, system
from typing import List
from fastapi import Depends

def get_current_user_payload(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Return the full JWT payload for the current user"""
    return get_current_user_from_token(credentials)


def require_roles(allowed_roles: List[str]):
    """Dependency to enforce role-based access control (RBAC)"""
    async def _role_checker(payload: dict = Depends(get_current_user_payload)):
        # role may be a single string or a list of strings in the token claims
        roles = payload.get("roles") or payload.get("role") or "user"
        if isinstance(roles, str):
            roles = [roles]
        # normalize to lowercase for comparison
        normalized = {str(r).lower() for r in roles}
        allowed = {r.lower() for r in allowed_roles}
        if normalized.isdisjoint(allowed):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: insufficient role"
            )
        return payload
    return _role_checker

# Hybrid authentication: allow either JWT with roles or a valid Agent API key
def require_roles_or_api_key(allowed_roles: List[str]):
    """Dependency that authorizes via JWT roles or Agent API Key header.
    - If Authorization: Bearer <token> is present and valid with one of allowed_roles, grant access.
    - Else, if settings.API_KEY_HEADER_NAME is present in headers and matches one of settings.get_agent_api_keys(), grant access with role 'agent'.
    - Otherwise, raise 401/403 accordingly.
    Returns a principal payload dict containing at least keys: sub, roles, auth_type.
    """
    async def _auth_checker(request: Request):
        # Try JWT first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.lower().startswith("bearer "):
            token = auth_header.split(" ", 1)[1]
            payload = verify_token(token, "access")
            if payload:
                roles = payload.get("roles") or payload.get("role") or "user"
                if isinstance(roles, str):
                    roles = [roles]
                normalized = {str(r).lower() for r in roles}
                allowed = {r.lower() for r in allowed_roles}
                if normalized.isdisjoint(allowed):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Forbidden: insufficient role"
                    )
                payload["auth_type"] = "jwt"
                return payload
            else:
                # Invalid or expired token provided
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired token",
                    headers={"WWW-Authenticate": "Bearer"},
                )

        # Fallback: API Key header for agents
        api_key_header_name = settings.API_KEY_HEADER_NAME
        api_key_value = request.headers.get(api_key_header_name)
        if api_key_value:
            allowed_keys = settings.get_agent_api_keys()
            if api_key_value in allowed_keys:
                # Build a minimal principal for agent callers
                principal = {
                    "sub": "agent-api-key",
                    "roles": ["agent"],
                    "auth_type": "api_key",
                    "api_key_last4": api_key_value[-4:] if len(api_key_value) >= 4 else api_key_value,
                }
                return principal

        # No valid auth provided
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized: valid JWT or API key required",
        )

    return _auth_checker


def sanitize_input(value: str) -> str:
    """Sanitizar entrada contra XSS e ataques de injeção"""
    if not isinstance(value, str):
        return value
    
    # Escape HTML entities
    cleaned = html.escape(value)
    
    # Remove caracteres perigosos
    dangerous_chars = ['javascript:', 'data:', 'vbscript:']
    for char in dangerous_chars:
        cleaned = cleaned.replace(char, '')
    
    return cleaned


def validate_password_strength(password: str) -> bool:
    """Validar força da senha"""
    if len(password) < 8:
        return False
    
    # Deve ter pelo menos uma letra maiúscula, minúscula, número e símbolo
    patterns = [
        r'[A-Z]',  # Maiúscula
        r'[a-z]',  # Minúscula
        r'[0-9]',  # Número
        r'[!@#$%^&*(),.?":{}|<>]'  # Símbolo
    ]
    
    return all(re.search(pattern, password) for pattern in patterns)


def detect_malicious_content(content: str) -> bool:
    """Detectar conteúdo malicioso"""
    if not isinstance(content, str):
        return False
        
    malicious_patterns = [
        r"'.*OR.*'.*=.*'",  # SQL Injection
        r"UNION.*SELECT",   # SQL Injection
        r"DROP.*TABLE",     # SQL Injection
        r"<script.*?>",     # XSS
        r"javascript:",     # XSS
        r"eval\(",          # Code injection
        r"exec\(",          # Code injection
    ]
    
    content_upper = content.upper()
    for pattern in malicious_patterns:
        if re.search(pattern, content_upper, re.IGNORECASE):
            return True
    
    return False


def validate_email(email: str) -> bool:
    """Validar formato de email"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# Audit trail helpers
def compute_audit_record_hash(data: Dict[str, Any]) -> str:
    """Compute a deterministic SHA-256 hash for an audit record payload.
    Uses JSON serialization with sorted keys for stability.
    """
    try:
        import json
        serialized = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    except Exception as e:
        logger.error("Failed to compute audit record hash", error=str(e))
        raise


def compute_audit_signature(record_hash: str, prev_hash: Optional[str] = None) -> str:
    """Compute HMAC-SHA256 signature over record_hash and optional prev_hash.
    The key material comes from settings.SECRET_KEY.
    """
    try:
        message = (prev_hash or "") + record_hash
        signature = hmac.new(
            key=settings.SECRET_KEY.encode("utf-8"),
            msg=message.encode("utf-8"),
            digestmod=hashlib.sha256
        ).hexdigest()
        return signature
    except Exception as e:
        logger.error("Failed to compute audit signature", error=str(e))
        raise
