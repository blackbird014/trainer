"""
Logging System for PromptManager

Provides structured logging with support for:
- File logging (JSON format for easy parsing)
- Database logging (extensible)
- Prometheus metrics integration
- Multiple log levels
- Contextual information
"""

import logging
import json
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class LogLevel(Enum):
    """Log levels."""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        # Add any additional attributes
        for key, value in record.__dict__.items():
            if key not in ["name", "msg", "args", "created", "filename", 
                          "levelname", "levelno", "lineno", "module", 
                          "msecs", "message", "pathname", "process", 
                          "processName", "relativeCreated", "thread", 
                          "threadName", "exc_info", "exc_text", "stack_info",
                          "extra_fields"]:
                log_data[key] = value
        
        return json.dumps(log_data, default=str)


class PromptManagerLogger:
    """Logger for PromptManager with structured logging and metrics."""
    
    def __init__(self, 
                 name: str = "prompt_manager",
                 log_file: Optional[str] = None,
                 log_level: LogLevel = LogLevel.INFO,
                 enable_console: bool = True,
                 enable_json: bool = True,
                 enable_metrics: bool = True):
        """
        Initialize logger.
        
        Args:
            name: Logger name
            log_file: Optional path to log file
            log_level: Logging level
            enable_console: Enable console output
            enable_json: Use JSON formatting
            enable_metrics: Enable Prometheus metrics
        """
        self.name = name
        self.logger = logging.getLogger(name)
        self.logger.setLevel(log_level.value)
        
        # Prevent duplicate handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(log_level.value)
            if enable_json:
                console_handler.setFormatter(JSONFormatter())
            else:
                console_handler.setFormatter(
                    logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )
                )
            self.logger.addHandler(console_handler)
        
        # File handler
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(log_level.value)
            if enable_json:
                file_handler.setFormatter(JSONFormatter())
            else:
                file_handler.setFormatter(
                    logging.Formatter(
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                    )
                )
            self.logger.addHandler(file_handler)
        
        # Prometheus metrics (if enabled)
        self.metrics_enabled = enable_metrics
        self._metrics = {}
        
        if enable_metrics:
            try:
                from prometheus_client import Counter, Histogram, Gauge
                self._metrics = {
                    "operations_total": Counter(
                        "prompt_manager_operations_total",
                        "Total number of operations",
                        ["operation", "status"]
                    ),
                    "operation_duration_seconds": Histogram(
                        "prompt_manager_operation_duration_seconds",
                        "Operation duration in seconds",
                        ["operation"]
                    ),
                    "tokens_total": Counter(
                        "prompt_manager_tokens_total",
                        "Total tokens processed",
                        ["operation", "type"]
                    ),
                    "cost_total": Counter(
                        "prompt_manager_cost_total",
                        "Total cost in USD",
                        ["operation", "model"]
                    ),
                    "cache_hits_total": Counter(
                        "prompt_manager_cache_hits_total",
                        "Total cache hits",
                        ["cache_type"]
                    ),
                    "cache_misses_total": Counter(
                        "prompt_manager_cache_misses_total",
                        "Total cache misses",
                        ["cache_type"]
                    ),
                }
            except ImportError:
                self.logger.warning(
                    "prometheus_client not installed. Metrics disabled.",
                    extra={"extra_fields": {"metrics_enabled": False}}
                )
                self.metrics_enabled = False
    
    def _log_with_metrics(self, level: int, msg: str, extra: Optional[Dict[str, Any]] = None, 
                         operation: Optional[str] = None, duration: Optional[float] = None,
                         tokens: Optional[int] = None, cost: Optional[float] = None):
        """Log with metrics tracking."""
        # Add extra fields
        log_extra = extra or {}
        if operation:
            log_extra["operation"] = operation
        if duration is not None:
            log_extra["duration_seconds"] = duration
        if tokens is not None:
            log_extra["tokens"] = tokens
        if cost is not None:
            log_extra["cost_usd"] = cost
        
        # Log with extra fields
        self.logger.log(level, msg, extra={"extra_fields": log_extra})
        
        # Update metrics
        if self.metrics_enabled and self._metrics:
            if operation:
                status = "success" if level < logging.ERROR else "error"
                self._metrics["operations_total"].labels(
                    operation=operation, status=status
                ).inc()
                
                if duration is not None:
                    self._metrics["operation_duration_seconds"].labels(
                        operation=operation
                    ).observe(duration)
                
                if tokens is not None:
                    token_type = log_extra.get("token_type", "input")
                    self._metrics["tokens_total"].labels(
                        operation=operation, type=token_type
                    ).inc(tokens)
                
                if cost is not None:
                    model = log_extra.get("model", "unknown")
                    self._metrics["cost_total"].labels(
                        operation=operation, model=model
                    ).inc(cost)
    
    def debug(self, msg: str, **kwargs):
        """Log debug message."""
        self._log_with_metrics(logging.DEBUG, msg, kwargs)
    
    def info(self, msg: str, operation: Optional[str] = None, 
             duration: Optional[float] = None, tokens: Optional[int] = None,
             cost: Optional[float] = None, **kwargs):
        """Log info message."""
        self._log_with_metrics(logging.INFO, msg, kwargs, operation, duration, tokens, cost)
    
    def warning(self, msg: str, **kwargs):
        """Log warning message."""
        self._log_with_metrics(logging.WARNING, msg, kwargs)
    
    def error(self, msg: str, operation: Optional[str] = None, **kwargs):
        """Log error message."""
        self._log_with_metrics(logging.ERROR, msg, kwargs, operation)
    
    def critical(self, msg: str, **kwargs):
        """Log critical message."""
        self._log_with_metrics(logging.CRITICAL, msg, kwargs)
    
    def track_cache_hit(self, cache_type: str):
        """Track cache hit."""
        if self.metrics_enabled and "cache_hits_total" in self._metrics:
            self._metrics["cache_hits_total"].labels(cache_type=cache_type).inc()
    
    def track_cache_miss(self, cache_type: str):
        """Track cache miss."""
        if self.metrics_enabled and "cache_misses_total" in self._metrics:
            self._metrics["cache_misses_total"].labels(cache_type=cache_type).inc()
    
    def get_metrics_endpoint(self):
        """Get Prometheus metrics endpoint handler."""
        if not self.metrics_enabled:
            return None
        
        try:
            from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
            from flask import Response
            
            def metrics_handler():
                return Response(
                    generate_latest(),
                    mimetype=CONTENT_TYPE_LATEST
                )
            
            return metrics_handler
        except ImportError:
            return None


class DatabaseLogHandler(logging.Handler):
    """Database log handler (extensible)."""
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize database handler.
        
        Args:
            connection_string: Database connection string
        """
        super().__init__()
        self.connection_string = connection_string
        # In production, initialize database connection here
    
    def emit(self, record: logging.LogRecord):
        """Emit log record to database."""
        # Extract log data
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        # In production, insert into database
        # Example: self.db.insert("logs", log_data)
        pass


def setup_logger(name: str = "prompt_manager",
                 log_file: Optional[str] = None,
                 log_level: LogLevel = LogLevel.INFO,
                 enable_console: bool = True,
                 enable_json: bool = True,
                 enable_metrics: bool = True,
                 enable_database: bool = False,
                 db_connection: Optional[str] = None) -> PromptManagerLogger:
    """
    Setup logger with configuration.
    
    Args:
        name: Logger name
        log_file: Optional log file path
        log_level: Logging level
        enable_console: Enable console output
        enable_json: Use JSON formatting
        enable_metrics: Enable Prometheus metrics
        enable_database: Enable database logging
        db_connection: Database connection string
        
    Returns:
        Configured PromptManagerLogger instance
    """
    logger = PromptManagerLogger(
        name=name,
        log_file=log_file,
        log_level=log_level,
        enable_console=enable_console,
        enable_json=enable_json,
        enable_metrics=enable_metrics
    )
    
    # Add database handler if enabled
    if enable_database:
        db_handler = DatabaseLogHandler(connection_string=db_connection)
        db_handler.setLevel(log_level.value)
        if enable_json:
            db_handler.setFormatter(JSONFormatter())
        logger.logger.addHandler(db_handler)
    
    return logger

