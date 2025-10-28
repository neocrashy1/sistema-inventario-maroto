"""
Input validation and sanitization middleware
"""
import re
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import html
import urllib.parse

logger = logging.getLogger(__name__)

class InputValidator:
    """
    Input validation and sanitization utilities
    """
    
    # Common patterns for validation
    PATTERNS = {
        'email': re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'),
        'username': re.compile(r'^[a-zA-Z0-9_-]{3,50}$'),
        'password': re.compile(r'^.{8,128}$'),  # At least 8 chars, max 128
        'uuid': re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'),
        'alphanumeric': re.compile(r'^[a-zA-Z0-9\s]+$'),
        'safe_string': re.compile(r'^[a-zA-Z0-9\s\-_.,!?()]+$')
    }
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
        re.compile(r'javascript:', re.IGNORECASE),
        re.compile(r'on\w+\s*=', re.IGNORECASE),
        re.compile(r'<iframe[^>]*>.*?</iframe>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<object[^>]*>.*?</object>', re.IGNORECASE | re.DOTALL),
        re.compile(r'<embed[^>]*>', re.IGNORECASE),
        re.compile(r'eval\s*\(', re.IGNORECASE),
        re.compile(r'expression\s*\(', re.IGNORECASE),
        re.compile(r'vbscript:', re.IGNORECASE),
        re.compile(r'data:text/html', re.IGNORECASE)
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        re.compile(r'\b(union|select|insert|update|delete|drop|create|alter|exec|execute)\b', re.IGNORECASE),
        re.compile(r'[\'";]', re.IGNORECASE),
        re.compile(r'--', re.IGNORECASE),
        re.compile(r'/\*.*?\*/', re.IGNORECASE | re.DOTALL)
    ]
    
    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input
        """
        if not isinstance(value, str):
            return str(value)
        
        # Truncate if too long
        if len(value) > max_length:
            value = value[:max_length]
        
        # HTML encode
        value = html.escape(value)
        
        # URL decode to prevent double encoding attacks
        try:
            value = urllib.parse.unquote(value)
        except:
            pass
        
        return value.strip()
    
    @classmethod
    def check_dangerous_patterns(cls, value: str) -> bool:
        """
        Check if string contains dangerous patterns
        """
        for pattern in cls.DANGEROUS_PATTERNS:
            if pattern.search(value):
                return True
        return False
    
    @classmethod
    def check_sql_injection(cls, value: str) -> bool:
        """
        Check for SQL injection patterns
        """
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if pattern.search(value):
                return True
        return False
    
    @classmethod
    def validate_email(cls, email: str) -> bool:
        """
        Validate email format
        """
        return bool(cls.PATTERNS['email'].match(email))
    
    @classmethod
    def validate_username(cls, username: str) -> bool:
        """
        Validate username format
        """
        return bool(cls.PATTERNS['username'].match(username))
    
    @classmethod
    def validate_password_strength(cls, password: str) -> Dict[str, Any]:
        """
        Validate password strength
        """
        result = {
            'valid': True,
            'errors': []
        }
        
        if len(password) < 8:
            result['valid'] = False
            result['errors'].append('Password must be at least 8 characters long')
        
        if len(password) > 128:
            result['valid'] = False
            result['errors'].append('Password must be less than 128 characters')
        
        if not re.search(r'[a-z]', password):
            result['valid'] = False
            result['errors'].append('Password must contain at least one lowercase letter')
        
        if not re.search(r'[A-Z]', password):
            result['valid'] = False
            result['errors'].append('Password must contain at least one uppercase letter')
        
        if not re.search(r'\d', password):
            result['valid'] = False
            result['errors'].append('Password must contain at least one digit')
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            result['valid'] = False
            result['errors'].append('Password must contain at least one special character')
        
        return result

class ValidationMiddleware:
    """
    Request validation middleware
    """
    
    def __init__(self):
        self.validator = InputValidator()
        self.max_request_size = 10 * 1024 * 1024  # 10MB
        self.max_json_depth = 10
    
    async def validate_request_size(self, request: Request) -> bool:
        """
        Validate request size
        """
        content_length = request.headers.get('content-length')
        if content_length and int(content_length) > self.max_request_size:
            return False
        return True
    
    def validate_json_depth(self, obj: Any, depth: int = 0) -> bool:
        """
        Validate JSON nesting depth
        """
        if depth > self.max_json_depth:
            return False
        
        if isinstance(obj, dict):
            return all(self.validate_json_depth(v, depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            return all(self.validate_json_depth(item, depth + 1) for item in obj)
        
        return True
    
    def sanitize_json_data(self, data: Any) -> Any:
        """
        Recursively sanitize JSON data
        """
        if isinstance(data, dict):
            return {
                key: self.sanitize_json_data(value)
                for key, value in data.items()
                if isinstance(key, str) and len(key) <= 100  # Limit key length
            }
        elif isinstance(data, list):
            return [self.sanitize_json_data(item) for item in data[:1000]]  # Limit array size
        elif isinstance(data, str):
            # Check for dangerous patterns
            if self.validator.check_dangerous_patterns(data):
                logger.warning(f"Dangerous pattern detected in input: {data[:100]}...")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
            
            # Check for SQL injection
            if self.validator.check_sql_injection(data):
                logger.warning(f"SQL injection attempt detected: {data[:100]}...")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
            
            return self.validator.sanitize_string(data)
        else:
            return data
    
    async def __call__(self, request: Request, call_next):
        """
        Process request with validation
        """
        # Validate request size
        if not await self.validate_request_size(request):
            logger.warning(f"Request too large from {request.client.host if request.client else 'unknown'}")
            return JSONResponse(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                content={
                    "detail": "Request entity too large",
                    "error_code": "REQUEST_TOO_LARGE"
                }
            )
        
        # Validate and sanitize JSON body for POST/PUT requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('content-type', '')
            
            if 'application/json' in content_type:
                try:
                    # Prefer FastAPI/Starlette built-in JSON parser
                    try:
                        json_data = await request.json()
                    except Exception:
                        body = await request.body()
                        if body:
                            json_data = json.loads(body)
                        else:
                            json_data = None
                    
                    if json_data is not None:
                        # Validate JSON depth
                        if not self.validate_json_depth(json_data):
                            logger.warning("JSON nesting too deep")
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                    "detail": "JSON nesting too deep",
                                    "error_code": "INVALID_JSON_STRUCTURE"
                                }
                            )
                        
                        # Sanitize JSON data
                        try:
                            sanitized_data = self.sanitize_json_data(json_data)
                            
                            # Replace request body with sanitized data
                            sanitized_body = json.dumps(sanitized_data).encode()
                            
                            # Store the sanitized body for the request (FIXED: don't modify _receive)
                            request._body = sanitized_body
                        except HTTPException:
                            raise
                        except Exception as e:
                            logger.error(f"Error sanitizing JSON data: {e}")
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                    "detail": "Invalid request data",
                                    "error_code": "INVALID_REQUEST_DATA"
                                }
                            )
                    # If body is empty, that's OK for some endpoints
                
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON in request body")
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "detail": "Invalid JSON format",
                            "error_code": "INVALID_JSON"
                        }
                    )
                except Exception as e:
                    logger.error(f"Error processing request body: {e}")
                    return JSONResponse(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        content={
                            "detail": "Error processing request",
                            "error_code": "REQUEST_PROCESSING_ERROR"
                        }
                    )
        
        # Continue with request
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

# Global validation middleware instance
validation_middleware = ValidationMiddleware()