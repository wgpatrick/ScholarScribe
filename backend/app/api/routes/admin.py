"""
Admin routes for the ScholarScribe API.

These routes provide administrative functionality, including error monitoring.
"""
from fastapi import APIRouter, Request, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, JSONResponse
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

# Import the logging utilities
from app.utils.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)

# Create router
router = APIRouter()

# Simple API key check for admin access
def verify_admin_key(request: Request):
    """
    Verify the admin API key from the X-API-Key header.
    This is a simple security measure for development/demo purposes.
    In production, use a more robust authentication mechanism.
    """
    api_key = request.headers.get("X-API-Key")
    expected_key = os.environ.get("ADMIN_API_KEY", "admin-dev-key")
    
    if not api_key or api_key != expected_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key"
        )
    return True

@router.get("/admin/dashboard", response_class=HTMLResponse)
async def get_error_dashboard(_: bool = Depends(verify_admin_key)):
    """
    Serve the error monitoring dashboard.
    
    This endpoint returns an HTML page for monitoring and analyzing application errors.
    """
    try:
        # Read the dashboard HTML file
        dashboard_path = Path(__file__).parent.parent.parent / "utils" / "error_dashboard.html"
        with open(dashboard_path, "r") as f:
            dashboard_html = f.read()
        
        return HTMLResponse(content=dashboard_html)
    except Exception as e:
        logger.error(f"Failed to serve error dashboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not load error dashboard"
        )

@router.get("/admin/errors")
async def get_errors(
    hours: Optional[int] = 24,
    level: Optional[str] = None,
    _: bool = Depends(verify_admin_key)
):
    """
    Get error logs from the application.
    
    Args:
        hours: Number of hours to look back (default: 24)
        level: Filter by log level (e.g., ERROR, WARNING, CRITICAL)
        
    Returns:
        List of error records
    """
    try:
        # In a real implementation, this would query a database or parse log files
        # For this demo, we'll return sample data
        
        # Sample error data - in a real implementation, parse from log files
        sample_errors = [
            {
                "timestamp": (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                "level": "ERROR",
                "error_type": "ValueError",
                "module": "pdf_parsing.llama_parse_client",
                "message": "Failed to parse PDF: Invalid file format",
                "traceback": "File \"app/services/pdf_parsing/llama_parse_client.py\", line 120, in parse_pdf\n    result = client.parse_pdf(pdf_path)\nFile \"app/services/pdf_parsing/direct_llama_client.py\", line 85, in parse_pdf\n    raise ValueError(\"Invalid file format\")\nValueError: Invalid file format",
                "context": {
                    "file": "document123.pdf",
                    "size": "2.3MB"
                }
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                "level": "CRITICAL",
                "error_type": "ConnectionError",
                "module": "services.storage",
                "message": "Failed to connect to LocalStack S3",
                "traceback": "File \"app/services/storage.py\", line 87, in store_file\n    response = s3_client.upload_file(file_path, bucket, key)\nFile \"boto3/s3/upload.py\", line 145, in upload_file\n    raise ConnectionError(\"Could not connect to endpoint\")\nConnectionError: Could not connect to endpoint",
                "context": {
                    "endpoint": "http://localstack:4566",
                    "bucket": "scholarscribe-documents"
                }
            },
            {
                "timestamp": (datetime.utcnow() - timedelta(hours=12)).isoformat(),
                "level": "WARNING",
                "error_type": "TimeoutWarning",
                "module": "services.pdf_parsing.direct_llama_client",
                "message": "LlamaCloud API request timed out after 30s",
                "traceback": "File \"app/services/pdf_parsing/direct_llama_client.py\", line 102, in _poll_status\n    response = requests.get(url, timeout=30)\nTimeoutWarning: Request timed out after 30 seconds",
                "context": {
                    "job_id": "8ca883c6-616d-4227-b6c6-b8eee41b42b9",
                    "attempts": "3"
                }
            }
        ]
        
        # Filter by time
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        filtered_errors = [
            error for error in sample_errors 
            if datetime.fromisoformat(error["timestamp"]) > cutoff_time
        ]
        
        # Filter by level if specified
        if level:
            level = level.upper()
            filtered_errors = [
                error for error in filtered_errors 
                if error["level"] == level
            ]
        
        return {
            "errors": filtered_errors,
            "total": len(filtered_errors),
            "filter": {
                "hours": hours,
                "level": level
            },
            "as_of": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Failed to get error logs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve error logs"
        )

@router.get("/admin/system-status")
async def get_system_status(_: bool = Depends(verify_admin_key)):
    """
    Get the overall system status.
    
    Returns:
        Dict: System status information
    """
    try:
        # In a real implementation, check actual services
        # For this demo, return sample data
        return {
            "status": "operational",
            "components": {
                "api": {
                    "status": "healthy",
                    "uptime": "3d 12h 45m",
                    "requests_per_minute": 25
                },
                "database": {
                    "status": "healthy",
                    "connection_pool": "10/20"
                },
                "storage": {
                    "status": "healthy",
                    "space_used": "1.2GB"
                },
                "llm_services": {
                    "llamacloud": {
                        "status": "operational",
                        "recent_errors": 0
                    },
                    "openai": {
                        "status": "operational",
                        "recent_errors": 0
                    }
                }
            },
            "as_of": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not retrieve system status"
        )