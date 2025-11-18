"""
Database configuration for Vercel deployment
Supports connection pooling optimized for serverless environments
"""
import os
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import NullPool
import logging

logger = logging.getLogger(__name__)

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")

# Fix postgres:// to postgresql:// if needed (some platforms use old format)
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Vercel/Serverless optimization: Use NullPool to prevent connection pooling
# This is important for serverless environments where connections should not persist
# between function invocations
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,  # No connection pooling for serverless
    echo=os.getenv("SQL_ECHO", "false").lower() == "true",  # SQL query logging
    pool_pre_ping=True,  # Verify connections before using
    connect_args={
        "connect_timeout": 10,
        "options": "-c timezone=utc",
    },
)

# For local development with traditional connection pooling (optional)
if os.getenv("ENVIRONMENT") == "development":
    engine = create_engine(
        DATABASE_URL,
        pool_size=5,
        max_overflow=10,
        pool_pre_ping=True,
        echo=os.getenv("SQL_ECHO", "false").lower() == "true",
        connect_args={
            "connect_timeout": 10,
            "options": "-c timezone=utc",
        },
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get database session.

    Usage:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    This should only be used in development.
    For production, use Alembic migrations.
    """
    import app.models  # Import models to register them

    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


def check_db_connection():
    """
    Check if database connection is working.
    Useful for health checks in serverless environments.
    """
    try:
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False
