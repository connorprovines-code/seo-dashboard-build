"""Application configuration using Pydantic settings"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # App Config
    APP_NAME: str = "SEO Dashboard"
    VERSION: str = "0.1.0"
    DEBUG: bool = Field(default=False)
    ENVIRONMENT: str = Field(default="development")

    # Server
    BACKEND_URL: str = Field(default="http://localhost:8000")
    FRONTEND_URL: str = Field(default="http://localhost:3000")

    # Supabase
    SUPABASE_URL: str = Field(..., description="Supabase project URL")
    SUPABASE_ANON_KEY: str = Field(..., description="Supabase anon/public key")

    # Redis
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # JWT Authentication
    SECRET_KEY: str = Field(..., description="Secret key for JWT signing")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRE_MINUTES: int = Field(default=43200)  # 30 days

    # DataForSEO API (Optional - users provide their own)
    DATAFORSEO_LOGIN: Optional[str] = None
    DATAFORSEO_PASSWORD: Optional[str] = None

    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: str = Field(default="http://localhost:8000/api/auth/google/callback")

    # Anthropic API (Phase 3)
    ANTHROPIC_API_KEY: Optional[str] = None

    # Email (Phase 2)
    SENDGRID_API_KEY: Optional[str] = None

    # Encryption
    ENCRYPTION_KEY: str = Field(..., description="Key for encrypting API credentials")

    # CORS
    ALLOWED_ORIGINS: list[str] = Field(default=["http://localhost:3000"])

    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
