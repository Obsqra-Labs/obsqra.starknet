"""
Obsqra Backend - Verifiable AI Infrastructure for DeFi
FastAPI + PostgreSQL + ML Models
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.config import settings
from app.database import init_db
from app.api import router as api_router
from app.ml.scheduler import start_ml_scheduler
from app.workers.atlantic_worker import start_atlantic_poller

# Configure logging
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    logger.info("🚀 Starting Obsqra Backend...")
    
    # Initialize database
    await init_db()
    logger.info("✅ Database initialized")
    
    # Start ML scheduler for periodic updates
    scheduler_task = start_ml_scheduler()
    logger.info("✅ ML scheduler started")

    # Start Atlantic poller (if configured)
    atlantic_task = start_atlantic_poller()
    if atlantic_task:
        logger.info("✅ Atlantic poller started")
    else:
        logger.info("ℹ️ Atlantic poller not started (no API key configured)")
    
    yield
    
    # Cleanup on shutdown
    logger.info("🛑 Shutting down Obsqra Backend...")


# Create FastAPI app
app = FastAPI(
    title="Obsqra Backend API",
    description="Verifiable AI Infrastructure for DeFi Risk Prediction & Optimization",
    version="1.0.0",
    lifespan=lifespan,
)

# Add middleware
# Filter out "*" from CORS_ORIGINS if present (can't use with allow_credentials=True)
cors_origins = [origin for origin in settings.CORS_ORIGINS if origin != "*"]
if not cors_origins:
    # If no origins specified, allow all (but disable credentials)
    cors_origins = ["*"]
    allow_creds = False
else:
    allow_creds = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_creds,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Only apply TrustedHostMiddleware if not allowing all hosts
# In development, we allow all hosts to avoid 400 errors
if settings.TRUSTED_HOSTS and "*" not in settings.TRUSTED_HOSTS:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.TRUSTED_HOSTS)
else:
    logger.info("⚠️  TrustedHostMiddleware disabled (allowing all hosts)")

# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/health", tags=["System"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "obsqra-backend",
        "version": "1.0.0",
    }


@app.get("/", tags=["System"])
async def root():
    """Root endpoint."""
    return {
        "message": "Obsqra Backend API",
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
    )
