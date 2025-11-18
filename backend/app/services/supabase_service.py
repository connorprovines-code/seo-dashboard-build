"""
Supabase service layer for database operations
Provides high-level methods for working with the SEO Dashboard data
"""
from supabase import Client
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class UserService:
    """Service for user-related database operations"""

    @staticmethod
    def get_by_email(db: Client, email: str) -> Optional[Dict]:
        """Get user by email"""
        try:
            result = db.table('users').select('*').eq('email', email).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting user by email: {e}")
            return None

    @staticmethod
    def create_user(db: Client, email: str, password_hash: str) -> Dict:
        """Create a new user"""
        result = db.table('users').insert({
            'email': email,
            'password_hash': password_hash,
            'api_credits_remaining': 0.00
        }).execute()
        return result.data[0]

    @staticmethod
    def get_by_id(db: Client, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        try:
            result = db.table('users').select('*').eq('id', user_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting user by ID: {e}")
            return None


class ProjectService:
    """Service for project-related database operations"""

    @staticmethod
    def get_user_projects(db: Client, user_id: str) -> List[Dict]:
        """Get all projects for a user"""
        result = db.table('projects')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', desc=True)\
            .execute()
        return result.data

    @staticmethod
    def create_project(db: Client, user_id: str, name: str, domain: str) -> Dict:
        """Create a new project"""
        result = db.table('projects').insert({
            'user_id': user_id,
            'name': name,
            'domain': domain,
            'gsc_connected': False
        }).execute()
        return result.data[0]

    @staticmethod
    def get_by_id(db: Client, project_id: str) -> Optional[Dict]:
        """Get project by ID"""
        try:
            result = db.table('projects').select('*').eq('id', project_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            return None

    @staticmethod
    def update_project(db: Client, project_id: str, data: Dict) -> Dict:
        """Update a project"""
        result = db.table('projects').update(data).eq('id', project_id).execute()
        return result.data[0]

    @staticmethod
    def delete_project(db: Client, project_id: str) -> bool:
        """Delete a project"""
        try:
            db.table('projects').delete().eq('id', project_id).execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting project: {e}")
            return False


class KeywordService:
    """Service for keyword-related database operations"""

    @staticmethod
    def get_project_keywords(db: Client, project_id: str) -> List[Dict]:
        """Get all keywords for a project"""
        result = db.table('keywords')\
            .select('*')\
            .eq('project_id', project_id)\
            .order('search_volume', desc=True)\
            .execute()
        return result.data

    @staticmethod
    def create_keyword(db: Client, project_id: str, keyword_data: Dict) -> Dict:
        """Create a new keyword"""
        data = {
            'project_id': project_id,
            **keyword_data
        }
        result = db.table('keywords').insert(data).execute()
        return result.data[0]

    @staticmethod
    def bulk_create_keywords(db: Client, project_id: str, keywords: List[Dict]) -> List[Dict]:
        """Bulk create keywords"""
        data = [{'project_id': project_id, **kw} for kw in keywords]
        result = db.table('keywords').insert(data).execute()
        return result.data

    @staticmethod
    def update_keyword(db: Client, keyword_id: str, data: Dict) -> Dict:
        """Update keyword data"""
        result = db.table('keywords').update(data).eq('id', keyword_id).execute()
        return result.data[0]

    @staticmethod
    def get_by_id(db: Client, keyword_id: str) -> Optional[Dict]:
        """Get keyword by ID"""
        try:
            result = db.table('keywords').select('*').eq('id', keyword_id).single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting keyword: {e}")
            return None


class RankTrackingService:
    """Service for rank tracking operations"""

    @staticmethod
    def get_keyword_ranks(db: Client, keyword_id: str, limit: int = 30) -> List[Dict]:
        """Get rank history for a keyword"""
        result = db.table('rank_tracking')\
            .select('*')\
            .eq('keyword_id', keyword_id)\
            .order('checked_at', desc=True)\
            .limit(limit)\
            .execute()
        return result.data

    @staticmethod
    def add_rank_check(db: Client, rank_data: Dict) -> Dict:
        """Record a new rank check"""
        result = db.table('rank_tracking').insert(rank_data).execute()
        return result.data[0]

    @staticmethod
    def get_latest_ranks(db: Client, project_id: str) -> List[Dict]:
        """Get latest rank for each keyword in a project"""
        # This would use a materialized view or custom query
        # For now, get all keywords and their latest rank
        keywords = db.table('keywords').select('*').eq('project_id', project_id).execute()

        result = []
        for kw in keywords.data:
            ranks = db.table('rank_tracking')\
                .select('*')\
                .eq('keyword_id', kw['id'])\
                .order('checked_at', desc=True)\
                .limit(1)\
                .execute()

            if ranks.data:
                result.append({
                    'keyword': kw,
                    'latest_rank': ranks.data[0]
                })

        return result


class ApiUsageService:
    """Service for API usage tracking"""

    @staticmethod
    def log_api_usage(db: Client, user_id: str, provider: str, endpoint: str, cost: float,
                      request_payload: Optional[Dict] = None, response_status: Optional[int] = None) -> Dict:
        """Log an API usage event"""
        result = db.table('api_usage_logs').insert({
            'user_id': user_id,
            'api_provider': provider,
            'endpoint': endpoint,
            'cost': cost,
            'request_payload': request_payload,
            'response_status': response_status
        }).execute()
        return result.data[0]

    @staticmethod
    def get_user_usage(db: Client, user_id: str, start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> List[Dict]:
        """Get API usage logs for a user"""
        query = db.table('api_usage_logs').select('*').eq('user_id', user_id)

        if start_date:
            query = query.gte('created_at', start_date.isoformat())
        if end_date:
            query = query.lte('created_at', end_date.isoformat())

        result = query.order('created_at', desc=True).execute()
        return result.data


class ApiCredentialService:
    """Service for managing API credentials"""

    @staticmethod
    def get_credentials(db: Client, user_id: str, provider: str) -> Optional[Dict]:
        """Get API credentials for a provider"""
        try:
            result = db.table('api_credentials')\
                .select('*')\
                .eq('user_id', user_id)\
                .eq('provider', provider)\
                .eq('is_active', True)\
                .single()\
                .execute()
            return result.data
        except Exception as e:
            logger.error(f"Error getting API credentials: {e}")
            return None

    @staticmethod
    def save_credentials(db: Client, user_id: str, provider: str,
                        credentials_encrypted: str) -> Dict:
        """Save or update API credentials"""
        # Upsert - insert or update if exists
        result = db.table('api_credentials').upsert({
            'user_id': user_id,
            'provider': provider,
            'credentials_encrypted': credentials_encrypted,
            'is_active': True,
            'last_verified_at': datetime.utcnow().isoformat()
        }).execute()
        return result.data[0]

    @staticmethod
    def delete_credentials(db: Client, user_id: str, provider: str) -> bool:
        """Delete API credentials"""
        try:
            db.table('api_credentials')\
                .update({'is_active': False})\
                .eq('user_id', user_id)\
                .eq('provider', provider)\
                .execute()
            return True
        except Exception as e:
            logger.error(f"Error deleting credentials: {e}")
            return False


# Export all services
__all__ = [
    'UserService',
    'ProjectService',
    'KeywordService',
    'RankTrackingService',
    'ApiUsageService',
    'ApiCredentialService'
]
