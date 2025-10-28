#!/usr/bin/env python3
"""
Fixed validation middleware that doesn't break request handling
"""

import json
import re
from typing import Any, Dict, List, Union
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import structlog

logger = structlog.get_logger()

class InputValidator:
    """Input validation and sanitization"""
    
    def __init__(self):
        # Validation patterns
        self.email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
        self.username_pattern = re.compile(r'^[a-zA-Z0-9_-]{3,50}$')
        self.password_pattern = re.compile(r'^.{8,128}$')  # At least 8 chars, max 128
        self.uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)
        self.alphanumeric_pattern = re.compile(r'^[a-zA-Z0-9\s]+$')
        self.safe_string_pattern = re.compile(r'^[a-zA-Z0-9\s\-_.,!?()]+$')
        
        # Dangerous patterns to detect
        self.xss_patterns = [
            re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
            re.compile(r'javascript:', re.IGNORECASE),
            re.compile(r'on\w+\s*=', re.IGNORECASE),
            re.compile(r'<iframe[^>]*>', re.IGNORECASE),
            re.compile(r'<object[^>]*>', re.IGNORECASE),
            re.compile(r'<embed[^>]*>', re.IGNORECASE),
        ]
        
        self.sql_injection_patterns = [
            re.compile(r"(union|select|insert|update|delete|drop|create|alter|exec|execute)\s+", re.IGNORECASE),
            re.compile(r"'\s*(or|and)\s*'\s*=\s*'", re.IGNORECASE),
            re.compile(r"--", re.IGNORECASE),
            re.compile(r"/\*.*?\*/", re.IGNORECASE | re.DOTALL),
            re.compile(r"'\s*(;|\||&)", re.IGNORECASE),
        ]
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        return bool(self.email_pattern.match(email))
    
    def validate_username(self, username: str) -> bool:
        """Validate username format"""
        return bool(self.username_pattern.match(username))
    
    def validate_password(self, password: str) -> bool:
        """Validate password format"""
        return bool(self.password_pattern.match(password))
    
    def validate_uuid(self, uuid_str: str) -> bool:
        """Validate UUID format"""
        return bool(self.uuid_pattern.match(uuid_str))
    
    def check_xss(self, text: str) -> bool:
        """Check for XSS patterns"""
        for pattern in self.xss_patterns:
            if pattern.search(text):
                return True
        return False
    
    def check_sql_injection(self, text: str) -> bool:
        """Check for SQL injection patterns"""
        for pattern in self.sql_injection_patterns:
            if pattern.search(text):
                return True
        return False
    
    def sanitize_string(self, text: str) -> str:
        """Sanitize string by removing dangerous characters"""
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Remove control characters except newline and tab
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\t')
        
        # Escape HTML entities
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        text = text.replace('"', '&quot;')
        text = text.replace("'", '&#x27;')
        
        return text

class ValidationMiddleware:
    """Fixed validation middleware"""
    
    def __init__(self, max_request_size: int = 10 * 1024 * 1024, max_json_depth: int = 10):
        self.validator = InputValidator()
        self.max_request_size = max_request_size
        self.max_json_depth = max_json_depth
    
    async def validate_request_size(self, request: Request) -> bool:
        """Validate request size"""
        content_length = request.headers.get('content-length')
        if content_length:
            try:
                size = int(content_length)
                return size <= self.max_request_size
            except ValueError:
                return False
        return True
    
    def validate_json_depth(self, data: Any, current_depth: int = 0) -> bool:
        """Validate JSON nesting depth"""
        if current_depth > self.max_json_depth:
            return False
        
        if isinstance(data, dict):
            for value in data.values():
                if not self.validate_json_depth(value, current_depth + 1):
                    return False
        elif isinstance(data, list):
            for item in data:
                if not self.validate_json_depth(item, current_depth + 1):
                    return False
        
        return True
    
    def sanitize_json_data(self, data: Any) -> Any:
        """Sanitize JSON data recursively"""
        if isinstance(data, dict):
            return {key: self.sanitize_json_data(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_json_data(item) for item in data]
        elif isinstance(data, str):
            # Check for dangerous patterns
            if self.validator.check_xss(data):
                logger.warning(f"XSS attempt detected: {data[:100]}...")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid input detected"
                )
            
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
        """Process request with validation - FIXED VERSION"""
        
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
                    # Read body once and cache it
                    body = await request.body()
                    
                    if body:
                        try:
                            json_data = json.loads(body)
                            
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
                                
                                # Create new body with sanitized data
                                sanitized_body = json.dumps(sanitized_data).encode()
                                
                                # Store the sanitized body for the request
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
                        except json.JSONDecodeError:
                            logger.warning("Invalid JSON in request body")
                            return JSONResponse(
                                status_code=status.HTTP_400_BAD_REQUEST,
                                content={
                                    "detail": "Invalid JSON format",
                                    "error_code": "INVALID_JSON"
                                }
                            )
                    # If body is empty, that's OK for some endpoints
                    
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
validation_middleware_fixed = ValidationMiddleware()