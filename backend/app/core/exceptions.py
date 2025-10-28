"""
Custom application exceptions
"""

from typing import Optional


class AppException(Exception):
    """Base application exception"""
    
    def __init__(
        self,
        detail: str,
        status_code: int = 500,
        error_code: Optional[str] = None
    ):
        self.detail = detail
        self.status_code = status_code
        self.error_code = error_code or "APP_ERROR"
        super().__init__(detail)


class ValidationException(AppException):
    """Validation error exception"""
    
    def __init__(self, detail: str):
        super().__init__(
            detail=detail,
            status_code=422,
            error_code="VALIDATION_ERROR"
        )


class AuthenticationException(AppException):
    """Authentication error exception"""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            detail=detail,
            status_code=401,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationException(AppException):
    """Authorization error exception"""
    
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            detail=detail,
            status_code=403,
            error_code="AUTHORIZATION_ERROR"
        )


class NotFoundException(AppException):
    """Resource not found exception"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            detail=detail,
            status_code=404,
            error_code="NOT_FOUND"
        )


class ConflictException(AppException):
    """Resource conflict exception"""
    
    def __init__(self, detail: str = "Resource conflict"):
        super().__init__(
            detail=detail,
            status_code=409,
            error_code="CONFLICT"
        )


class NetworkException(AppException):
    """Network operation exception"""
    
    def __init__(self, detail: str = "Network operation failed"):
        super().__init__(
            detail=detail,
            status_code=503,
            error_code="NETWORK_ERROR"
        )