"""
FastAPI Security Middleware

Middleware for validating requests, detecting prompt injections, and logging security events.
"""

import logging
import time
import uuid
from typing import Callable, Dict, Any, Optional, Tuple, TYPE_CHECKING
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

if TYPE_CHECKING:
    from prompt_security import SecurityModule, ValidationError, InjectionDetectedError

try:
    from prometheus_client import Counter, Histogram
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False

try:
    from prompt_security import SecurityModule, ValidationError, InjectionDetectedError
    SECURITY_MODULE_AVAILABLE = True
except ImportError:
    SECURITY_MODULE_AVAILABLE = False
    SecurityModule = None  # Type stub for type hints
    ValidationError = Exception  # Fallback
    InjectionDetectedError = Exception  # Fallback


# Setup logger
logger = logging.getLogger("prompt_manager.security")


# Prometheus metrics for security events
if PROMETHEUS_AVAILABLE:
    security_validation_total = Counter(
        "prompt_manager_security_validation_total",
        "Total number of security validations",
        ["endpoint", "status", "type"]
    )
    security_injection_detected_total = Counter(
        "prompt_manager_security_injection_detected_total",
        "Total number of prompt injection detections",
        ["endpoint", "pattern"]
    )
    security_validation_duration_seconds = Histogram(
        "prompt_manager_security_validation_duration_seconds",
        "Security validation duration in seconds",
        ["endpoint"]
    )
    security_rate_limit_hits_total = Counter(
        "prompt_manager_security_rate_limit_hits_total",
        "Total number of rate limit hits",
        ["endpoint", "client_id"]
    )
else:
    # Dummy metrics if Prometheus not available
    security_validation_total = None
    security_injection_detected_total = None
    security_validation_duration_seconds = None
    security_rate_limit_hits_total = None


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Security middleware for FastAPI that validates requests and detects prompt injections.
    
    Features:
    - Request body validation
    - Prompt injection detection
    - Security event logging
    - Prometheus metrics
    - Request ID tracking
    """
    
    def __init__(
        self,
        app: ASGIApp,
        security_module: Optional[SecurityModule] = None,
        enabled: bool = True,
        skip_paths: Optional[list] = None
    ):
        """
        Initialize security middleware.
        
        Args:
            app: ASGI application
            security_module: SecurityModule instance (creates default if None)
            enabled: Whether security is enabled
            skip_paths: List of paths to skip security checks (e.g., ["/health", "/metrics"])
        """
        super().__init__(app)
        self.enabled = enabled
        self.skip_paths = skip_paths or ["/health", "/metrics", "/docs", "/openapi.json", "/"]
        
        if not SECURITY_MODULE_AVAILABLE:
            logger.warning("prompt_security module not available. Security middleware disabled.")
            self.enabled = False
            self.security_module = None
        else:
            if security_module is None:
                # Create default SecurityModule
                from prompt_security import SecurityModule
                self.security_module = SecurityModule(strict_mode=True)
            else:
                self.security_module = security_module
    
    def _should_skip(self, path: str) -> bool:
        """Check if path should skip security checks."""
        return any(path.startswith(skip) for skip in self.skip_paths)
    
    def _extract_user_input(self, request: Request, body: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract user input from request body based on endpoint.
        
        Args:
            request: FastAPI request
            body: Request body as dictionary
            
        Returns:
            Dictionary of user input to validate
        """
        path = request.url.path
        
        # Extract user input based on endpoint
        if path == "/prompt/fill":
            # Validate params dictionary
            return body.get("params", {})
        elif path == "/prompt/compose":
            # Validate templates list (convert to dict for validation)
            templates = body.get("templates", [])
            return {"templates": "\n".join(templates) if isinstance(templates, list) else str(templates)}
        elif path == "/prompt/load-contexts":
            # Validate context paths
            paths = body.get("context_paths", [])
            return {"context_paths": "\n".join(paths) if isinstance(paths, list) else str(paths)}
        elif path == "/prompt/load":
            # Validate prompt path
            prompt_path = body.get("prompt_path", "")
            return {"prompt_path": prompt_path}
        else:
            # For other endpoints, validate entire body
            return body
    
    async def _validate_request(self, request: Request, body: Dict[str, Any]) -> Optional[JSONResponse]:
        """
        Validate request and detect prompt injections.
        
        Args:
            request: FastAPI request
            body: Request body as dictionary
            
        Returns:
            JSONResponse with error if validation fails, None if valid
        """
        if not self.enabled or not self.security_module:
            return None
        
        path = request.url.path
        start_time = time.time()
        
        try:
            # Extract user input
            user_input = self._extract_user_input(request, body)
            
            if not user_input:
                # No user input to validate
                return None
            
            # Validate input
            try:
                validated_input = self.security_module.validate(user_input)
                
                # Track validation success
                if PROMETHEUS_AVAILABLE and security_validation_total:
                    security_validation_total.labels(
                        endpoint=path,
                        status="success",
                        type="validation"
                    ).inc()
                
                # Detect injections in validated input
                for key, value in validated_input.items():
                    if isinstance(value, str):
                        detection = self.security_module.detect_injection(value)
                        
                        if not detection.is_safe:
                            # Injection detected
                            logger.warning(
                                f"Prompt injection detected",
                                extra={
                                    "request_id": request.state.request_id,
                                    "endpoint": path,
                                    "key": key,
                                    "flags": detection.flags,
                                    "risk_score": detection.risk_score,
                                    "patterns": detection.detected_patterns
                                }
                            )
                            
                            # Track injection detection
                            if PROMETHEUS_AVAILABLE and security_injection_detected_total:
                                for pattern in detection.detected_patterns[:3]:  # Limit to first 3 patterns
                                    security_injection_detected_total.labels(
                                        endpoint=path,
                                        pattern=pattern[:50]  # Truncate long patterns
                                    ).inc()
                            
                            # Raise exception in strict mode
                            if self.security_module.config.strict_mode:
                                raise InjectionDetectedError(
                                    f"Prompt injection detected in field '{key}': {', '.join(detection.flags[:3])}",
                                    detection
                                )
                            else:
                                # Log warning but continue in non-strict mode
                                logger.warning(
                                    f"Injection detected but continuing (non-strict mode)",
                                    extra={
                                        "request_id": request.state.request_id,
                                        "endpoint": path,
                                        "key": key
                                    }
                                )
                
                # Track validation duration
                duration = time.time() - start_time
                if PROMETHEUS_AVAILABLE and security_validation_duration_seconds:
                    security_validation_duration_seconds.labels(endpoint=path).observe(duration)
                
                return None  # Validation passed
                
            except ValidationError as e:
                # Validation failed
                logger.error(
                    f"Input validation failed",
                    extra={
                        "request_id": request.state.request_id,
                        "endpoint": path,
                        "errors": e.validation_result.errors,
                        "warnings": e.validation_result.warnings
                    }
                )
                
                # Track validation failure
                if PROMETHEUS_AVAILABLE and security_validation_total:
                    security_validation_total.labels(
                        endpoint=path,
                        status="failed",
                        type="validation"
                    ).inc()
                
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "error": "Validation failed",
                        "message": str(e),
                        "errors": e.validation_result.errors,
                        "warnings": e.validation_result.warnings,
                        "request_id": request.state.request_id
                    }
                )
            
            except InjectionDetectedError as e:
                # Injection detected in strict mode
                logger.error(
                    f"Prompt injection detected and blocked",
                    extra={
                        "request_id": request.state.request_id,
                        "endpoint": path,
                        "flags": e.detection_result.flags,
                        "risk_score": e.detection_result.risk_score,
                        "patterns": e.detection_result.detected_patterns
                    }
                )
                
                # Track injection detection
                if PROMETHEUS_AVAILABLE and security_injection_detected_total:
                    for pattern in e.detection_result.detected_patterns[:3]:
                        security_injection_detected_total.labels(
                            endpoint=path,
                            pattern=pattern[:50]
                        ).inc()
                
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={
                        "error": "Prompt injection detected",
                        "message": str(e),
                        "flags": e.detection_result.flags[:5],  # Limit to first 5 flags
                        "risk_score": e.detection_result.risk_score,
                        "request_id": request.state.request_id
                    }
                )
        
        except Exception as e:
            # Unexpected error during validation
            logger.exception(
                f"Unexpected error during security validation",
                extra={
                    "request_id": request.state.request_id,
                    "endpoint": path,
                    "error": str(e)
                }
            )
            
            # In production, you might want to allow the request through
            # or return a generic error. For now, we'll return 500.
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": "Security validation error",
                    "message": "An error occurred during security validation",
                    "request_id": request.state.request_id
                }
            )
    
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        """
        Process request through security middleware.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        # Generate request ID for tracking
        request.state.request_id = str(uuid.uuid4())
        
        # Skip security checks for certain paths
        if self._should_skip(request.url.path):
            return await call_next(request)
        
        # Only validate POST requests with body
        if request.method == "POST":
            try:
                # Read request body
                body = await request.json()
                
                # Validate request
                validation_response = await self._validate_request(request, body)
                if validation_response:
                    return validation_response
                
                # Replace request body with validated input (if needed)
                # Note: FastAPI doesn't easily allow modifying request body,
                # so we'll pass validated input through request.state
                request.state.validated_input = body
                
            except Exception as e:
                # If body parsing fails, let FastAPI handle it
                logger.debug(
                    f"Could not parse request body for security validation",
                    extra={
                        "request_id": request.state.request_id,
                        "endpoint": request.url.path,
                        "error": str(e)
                    }
                )
        
        # Continue to next middleware/handler
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Request-ID"] = request.state.request_id
        response.headers["X-Security-Enabled"] = str(self.enabled)
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware for security.
    
    Simple in-memory rate limiter based on client IP.
    For production, consider using Redis-based rate limiting.
    """
    
    def __init__(
        self,
        app: ASGIApp,
        requests_per_minute: int = 60,
        enabled: bool = True,
        skip_paths: Optional[list] = None
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            app: ASGI application
            requests_per_minute: Maximum requests per minute per client
            enabled: Whether rate limiting is enabled
            skip_paths: List of paths to skip rate limiting
        """
        super().__init__(app)
        self.enabled = enabled
        self.requests_per_minute = requests_per_minute
        self.skip_paths = skip_paths or ["/health", "/metrics", "/docs", "/openapi.json"]
        
        # In-memory rate limit store: {client_id: [(timestamp, ...), ...]}
        self._rate_limit_store: Dict[str, list] = {}
        self._cleanup_interval = 60  # Clean up old entries every 60 seconds
        self._last_cleanup = time.time()
    
    def _get_client_id(self, request: Request) -> str:
        """Get client identifier (IP address)."""
        # Try to get real IP from headers (if behind proxy)
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        # Fallback to direct client IP
        if request.client:
            return request.client.host
        
        return "unknown"
    
    def _should_skip(self, path: str) -> bool:
        """Check if path should skip rate limiting."""
        return any(path.startswith(skip) for skip in self.skip_paths)
    
    def _cleanup_old_entries(self):
        """Clean up old rate limit entries."""
        current_time = time.time()
        if current_time - self._last_cleanup < self._cleanup_interval:
            return
        
        cutoff_time = current_time - 60  # Keep last minute
        
        for client_id in list(self._rate_limit_store.keys()):
            timestamps = [
                ts for ts in self._rate_limit_store[client_id]
                if ts > cutoff_time
            ]
            
            if timestamps:
                self._rate_limit_store[client_id] = timestamps
            else:
                del self._rate_limit_store[client_id]
        
        self._last_cleanup = current_time
    
    def _check_rate_limit(self, client_id: str) -> Tuple[bool, int]:
        """
        Check if client has exceeded rate limit.
        
        Returns:
            Tuple of (allowed, remaining_requests)
        """
        current_time = time.time()
        cutoff_time = current_time - 60  # Last minute
        
        # Get timestamps for this client
        timestamps = self._rate_limit_store.get(client_id, [])
        
        # Filter to last minute
        recent_timestamps = [ts for ts in timestamps if ts > cutoff_time]
        
        # Check if limit exceeded
        if len(recent_timestamps) >= self.requests_per_minute:
            return False, 0
        
        # Add current request
        recent_timestamps.append(current_time)
        self._rate_limit_store[client_id] = recent_timestamps
        
        remaining = self.requests_per_minute - len(recent_timestamps)
        return True, remaining
    
    async def dispatch(self, request: Request, call_next: Callable) -> Any:
        """
        Process request through rate limit middleware.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        # Skip rate limiting for certain paths
        if self._should_skip(request.url.path):
            return await call_next(request)
        
        if not self.enabled:
            return await call_next(request)
        
        # Clean up old entries periodically
        self._cleanup_old_entries()
        
        # Get client ID
        client_id = self._get_client_id(request)
        
        # Check rate limit
        allowed, remaining = self._check_rate_limit(client_id)
        
        if not allowed:
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded",
                extra={
                    "request_id": getattr(request.state, "request_id", "unknown"),
                    "client_id": client_id,
                    "endpoint": request.url.path,
                    "limit": self.requests_per_minute
                }
            )
            
            # Track rate limit hit
            if PROMETHEUS_AVAILABLE and security_rate_limit_hits_total:
                security_rate_limit_hits_total.labels(
                    endpoint=request.url.path,
                    client_id=client_id[:50]  # Truncate long client IDs
                ).inc()
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Rate limit exceeded",
                    "message": f"Maximum {self.requests_per_minute} requests per minute",
                    "retry_after": 60,
                    "request_id": getattr(request.state, "request_id", "unknown")
                },
                headers={
                    "Retry-After": "60",
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0"
                }
            )
        
        # Continue to next middleware/handler
        response = await call_next(request)
        
        # Add rate limit headers
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        
        return response

