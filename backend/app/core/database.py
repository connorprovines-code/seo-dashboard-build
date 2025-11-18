"""Database configuration - Supabase client"""
from supabase import create_client, Client
from typing import Generator
from sqlalchemy.ext.declarative import declarative_base

from app.core.config import settings

# Dummy Base for backwards compatibility with existing models
# Models are no longer used but routers still import them
Base = declarative_base()

# Create Supabase client
_supabase_client: Client = None


def get_supabase() -> Client:
    """
    Get or create Supabase client singleton.
    Returns the Supabase client instance.
    """
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = create_client(
            supabase_url=settings.SUPABASE_URL,
            supabase_key=settings.SUPABASE_ANON_KEY
        )
    return _supabase_client


def get_db() -> Generator[Client, None, None]:
    """
    Dependency to get Supabase client.
    Yields a Supabase client for use in route handlers.
    """
    client = get_supabase()
    try:
        yield client
    finally:
        # Supabase client doesn't need explicit cleanup
        pass


def init_db() -> None:
    """
    Initialize Supabase connection.
    Note: Tables should be created via Supabase dashboard or migrations.
    """
    # Test connection
    client = get_supabase()
    # Supabase handles connection pooling automatically
    pass
