"""
Centralized logging configuration for ScholarScribe.

This module provides a consistent logging setup that:
1. Outputs logs to both console and file
2. Configures appropriate log levels
3. Formats logs with timestamps and other relevant information
4. Provides structured logging capabilities for error tracking
"""
import os
import sys
import json
import logging
import traceback
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# Default log level (can be overridden by environment variable)
DEFAULT_LOG_LEVEL = "INFO"
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}

# Get log level from environment or use default
log_level_name = os.environ.get("LOG_LEVEL", DEFAULT_LOG_LEVEL).upper()
LOG_LEVEL = LOG_LEVELS.get(log_level_name, logging.INFO)

# Log file path
LOG_FILE = os.path.abspath("app.log")

class ErrorInfo:
    """Class to collect and format error information for structured logging."""
    
    def __init__(
        self, 
        error: Exception, 
        module: str = None, 
        context: Dict[str, Any] = None,
        user_id: str = None
    ):
        """
        Initialize error information.
        
        Args:
            error: The exception that occurred
            module: The module where the error occurred
            context: Additional context information about the error
            user_id: Optional user ID for user-specific errors
        """
        self.timestamp = datetime.utcnow().isoformat()
        self.error_type = error.__class__.__name__
        self.error_message = str(error)
        self.module = module or "unknown"
        self.traceback = traceback.format_exc()
        self.context = context or {}
        self.user_id = user_id
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert error info to a dictionary."""
        return {
            "timestamp": self.timestamp,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "module": self.module,
            "traceback": self.traceback,
            "context": self.context,
            "user_id": self.user_id
        }
    
    def to_json(self) -> str:
        """Convert error info to a JSON string."""
        return json.dumps(self.to_dict(), default=str, indent=2)

class ScholarScribeFormatter(logging.Formatter):
    """Custom formatter that handles both regular logs and structured error logs."""
    
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
    
    def format(self, record):
        """Format log records, with special handling for structured errors."""
        # Check if this is a structured error log (ErrorInfo)
        if hasattr(record, 'error_info') and isinstance(record.error_info, dict):
            # Format structured error logs differently
            return f"{self.formatTime(record)} - {record.name} - {record.levelname} - " \
                   f"ERROR [{record.error_info.get('error_type', 'Unknown')}]: " \
                   f"{record.error_info.get('error_message', 'No message')} " \
                   f"(module: {record.error_info.get('module', 'unknown')})"
        
        # Regular log formatting
        return super().format(record)

def setup_logging():
    """Configure the logging system for the application."""
    # Create logs directory if needed
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(LOG_LEVEL)
    
    # Clear any existing handlers
    if root_logger.handlers:
        for handler in root_logger.handlers:
            root_logger.removeHandler(handler)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(LOG_LEVEL)
    console_handler.setFormatter(ScholarScribeFormatter())
    root_logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(LOG_LEVEL)
    file_handler.setFormatter(ScholarScribeFormatter())
    root_logger.addHandler(file_handler)
    
    # Configure library loggers to avoid excessive messages
    for logger_name in [
        "urllib3", "botocore", "boto3", "s3transfer", 
        "sqlalchemy.engine", "asyncio", "fiona", "httpx"
    ]:
        lib_logger = logging.getLogger(logger_name)
        lib_logger.setLevel(logging.WARNING)
    
    # Log startup information
    root_logger.info(f"Logging initialized with level: {log_level_name}")
    root_logger.info(f"Log file: {LOG_FILE}")

def log_structured_error(
    logger: logging.Logger,
    error: Exception,
    module: str = None,
    context: Dict[str, Any] = None,
    user_id: str = None,
    level: int = logging.ERROR
):
    """
    Log a structured error with detailed information.
    
    Args:
        logger: The logger to use
        error: The exception that occurred
        module: The module where the error occurred
        context: Additional context information about the error
        user_id: Optional user ID for user-specific errors
        level: The log level to use (default: ERROR)
    """
    error_info = ErrorInfo(
        error=error,
        module=module,
        context=context,
        user_id=user_id
    )
    
    # Attach error info to the log record
    extra = {'error_info': error_info.to_dict()}
    
    # Log with basic message and structured data
    logger.log(
        level,
        f"Error in {module or 'unknown'}: {error.__class__.__name__}: {str(error)}",
        extra=extra
    )
    
    # Also log detailed JSON for programmatic analysis
    logger.log(
        level,
        f"STRUCTURED_ERROR: {error_info.to_json()}"
    )
    
    return error_info

def get_logger(name: str) -> logging.Logger:
    """
    Get a configured logger instance.
    
    Args:
        name: The name for the logger (typically __name__)
        
    Returns:
        A configured logger instance
    """
    return logging.getLogger(name)