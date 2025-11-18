"""
SEO Dashboard - FastAPI Main Application
Optimized for Vercel serverless deployment
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import logging
from datetime import datetime

# Import database
from app.core.database import check_db_connection

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Optional: Sentry integration
if os.getenv("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.fastapi import FastApiIntegration

    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        integrations=[FastApiIntegration()],
        environment=os.getenv("ENVIRONMENT", "production"),
        traces_sample_rate=0.1,
    )
    logger.info("Sentry error tracking initialized")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting SEO Dashboard API...")
    logger.info(f"Environment: {os.getenv('ENVIRONMENT', 'development')}")

    # Check database connection
    if check_db_connection():
        logger.info("Database connection successful")
    else:
        logger.error("Database connection failed!")

    yield

    # Shutdown
    logger.info("Shutting down SEO Dashboard API...")


# Create FastAPI app
app = FastAPI(
    title="SEO Dashboard API",
    description="Affordable SEO tracking and analysis platform",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """
    Health check endpoint for monitoring
    """
    db_status = check_db_connection()

    return {
        "status": "healthy" if db_status else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "checks": {
            "database": "connected" if db_status else "disconnected",
        }
    }


# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": "SEO Dashboard API",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "health": "/api/health"
    }


# Error handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Global error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if os.getenv("ENVIRONMENT") == "development" else "An error occurred"
        }
    )


# Import and include routers (to be created)
# from app.routers import auth, projects, keywords, rank_tracking, api_credentials
# app.include_router(auth.router)
# app.include_router(projects.router)
# app.include_router(keywords.router)
# app.include_router(rank_tracking.router)
# app.include_router(api_credentials.router)


# For Vercel deployment
# Vercel will use this handler
handler = app


# For local development
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
