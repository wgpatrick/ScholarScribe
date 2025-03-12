from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import os
import time
import logging

from .api.api import api_router
from .utils.logging_config import setup_logging, get_logger, log_structured_error

# Setup centralized logging system
setup_logging()
logger = get_logger(__name__)

app = FastAPI(
    title="ScholarScribe API", 
    description="API for academic paper parsing, structured data extraction, and annotations",
    version="0.1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Add middleware for request timing and logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests with timing information."""
    start_time = time.time()
    
    # Process the request
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        
        # Log request details
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"- Status: {response.status_code} "
            f"- Time: {process_time:.4f}s"
        )
        
        return response
    except Exception as e:
        # Log any errors during request processing
        process_time = time.time() - start_time
        log_structured_error(
            logger, 
            error=e, 
            module="http_middleware",
            context={
                "method": request.method,
                "url": str(request.url),
                "client": request.client.host if request.client else "unknown",
                "process_time": f"{process_time:.4f}s",
            }
        )
        raise

# Error handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed responses."""
    error_details = exc.errors()
    log_structured_error(
        logger,
        error=exc,
        module="request_validation",
        context={
            "errors": error_details,
            "body": str(exc.body),
            "url": str(request.url)
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": error_details,
            "message": "Validation error in request data"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions with structured logging."""
    log_structured_error(
        logger,
        error=exc,
        module="server_error",
        context={
            "method": request.method,
            "url": str(request.url),
            "client": request.client.host if request.client else "unknown",
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": str(exc),
            "message": "An unexpected error occurred"
        }
    )

@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy", 
        "service": "ScholarScribe API",
        "version": app.version
    }

# Application startup event
@app.on_event("startup")
async def startup_event():
    """Perform tasks on application startup."""
    environment = os.environ.get("APP_ENV", "development")
    logger.info(f"Application startup in {environment} environment")
    # Here you can add initialization of services, database connections, etc.

# Application shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Perform tasks on application shutdown."""
    logger.info("Application shutdown")
    # Here you can add cleanup tasks, close connections, etc.

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
