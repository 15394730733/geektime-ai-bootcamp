"""
Database Query Tool - FastAPI Backend
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
import uvicorn
import logging

from app.api.v1.api import api_router
from app.core.config import settings
from app.services.startup import startup_service
from app.utils.response import APIResponse

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager."""
    logger.info("Starting Database Query Tool backend")

    # Initialize application with startup data loading
    try:
        logger.info("Initializing application and loading startup data...")
        startup_result = await startup_service.initialize_application()
        
        if startup_result["success"]:
            logger.info("Application startup completed successfully")
            logger.info(f"Database initialized: {startup_result['database_initialized']}")
            logger.info(f"Connections loaded: {startup_result['connections_loaded']}")
            
            if startup_result["warnings"]:
                for warning in startup_result["warnings"]:
                    logger.warning(warning)
        else:
            logger.error("Application startup completed with errors:")
            for error in startup_result["errors"]:
                logger.error(f"  - {error}")
            
            # Still allow the app to start even with some errors
            # unless it's a critical database initialization failure
            if not startup_result["database_initialized"]:
                logger.critical("Database initialization failed - cannot start application")
                raise RuntimeError("Critical startup failure: database initialization failed")
            
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        logger.error(f"Exception type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

    yield
    logger.info("Shutting down Database Query Tool backend")

# Create FastAPI application
app = FastAPI(
    title="Database Query Tool API",
    description="REST API for database exploration and SQL query execution",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors and return consistent API response format."""
    # Convert validation errors to serializable format
    errors = []
    for error in exc.errors():
        error_dict = {
            "type": error.get("type"),
            "loc": error.get("loc"),
            "msg": error.get("msg"),
            "input": error.get("input")
        }
        # Handle non-serializable context
        if "ctx" in error and error["ctx"]:
            error_dict["ctx"] = str(error["ctx"])
        errors.append(error_dict)
    
    error_response = APIResponse.error_response(
        message="Validation failed",
        error_code="VALIDATION_ERROR",
        details=errors
    )
    return JSONResponse(
        status_code=422,
        content=error_response.model_dump()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions and return consistent API response format."""
    # Determine error code based on status code
    error_code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED", 
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        409: "CONFLICT",
        500: "INTERNAL_ERROR",
        503: "SERVICE_UNAVAILABLE"
    }
    
    error_code = error_code_map.get(exc.status_code, "UNKNOWN_ERROR")
    
    error_response = APIResponse.error_response(
        message=str(exc.detail),
        error_code=error_code,
        details=None
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error_response.model_dump()
    )

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "database-query-tool"}

@app.get("/startup-status")
async def get_startup_status():
    """Get application startup status and loaded data information."""
    return await startup_service.get_startup_status()

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
