"""
Supabase client configuration for SEO Dashboard
Simplified database access using Supabase Python client
"""
import os
from supabase import create_client, Client
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_ANON_KEY environment variables are required")

# Create Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_supabase() -> Client:
    """
    Get Supabase client instance.

    Usage in FastAPI:
        @app.get("/items")
        def read_items(db: Client = Depends(get_supabase)):
            return db.table('items').select('*').execute()
    """
    return supabase


def check_db_connection() -> bool:
    """
    Check if Supabase connection is working.
    Useful for health checks.
    """
    try:
        # Try a simple query to verify connection
        result = supabase.table('users').select('id').limit(1).execute()
        return True
    except Exception as e:
        logger.error(f"Supabase connection failed: {e}")
        return False


# Helper functions for common operations
class SupabaseHelpers:
    """Helper methods for common Supabase operations"""

    @staticmethod
    def get_by_id(table: str, id: str):
        """Get a single record by ID"""
        return supabase.table(table).select('*').eq('id', id).single().execute()

    @staticmethod
    def get_all(table: str, filters: dict = None, order_by: str = None):
        """Get all records with optional filters"""
        query = supabase.table(table).select('*')

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        if order_by:
            query = query.order(order_by)

        return query.execute()

    @staticmethod
    def insert(table: str, data: dict):
        """Insert a new record"""
        return supabase.table(table).insert(data).execute()

    @staticmethod
    def update(table: str, id: str, data: dict):
        """Update a record by ID"""
        return supabase.table(table).update(data).eq('id', id).execute()

    @staticmethod
    def delete(table: str, id: str):
        """Delete a record by ID"""
        return supabase.table(table).delete().eq('id', id).execute()

    @staticmethod
    def upsert(table: str, data: dict):
        """Insert or update a record"""
        return supabase.table(table).upsert(data).execute()


# Export commonly used items
__all__ = ['supabase', 'get_supabase', 'check_db_connection', 'SupabaseHelpers']
