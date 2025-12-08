"""Database Configuration and Session Management"""

import logging
from typing import AsyncGenerator
from sqlalchemy.orm import declarative_base

logger = logging.getLogger(__name__)

# Base class for models (required for ORM)
Base = declarative_base()

# For now, we're using in-memory storage and will integrate PostgreSQL later
# This allows the proofs API to work without a database


async def get_db():
    """Dependency to get database session - placeholder for now."""
    # Will be replaced with actual database session when PostgreSQL is set up
    yield None


async def init_db():
    """Initialize database tables - placeholder for now."""
    try:
        logger.info("✅ Database initialization skipped (in-memory mode)")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


async def close_db():
    """Close database connections - placeholder for now."""
    logger.info("✅ Database connections closed")

