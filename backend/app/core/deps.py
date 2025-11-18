"""Dependencies for FastAPI routes"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase import Client
from typing import Optional

from app.core.database import get_db
from app.core.security import decode_access_token
from app.services.supabase_service import UserService

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Client = Depends(get_db)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    Raises HTTP 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception

    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise credentials_exception

    # Get user from database
    user = UserService.get_by_id(db, user_id)
    if user is None:
        raise credentials_exception

    return user


def get_current_user_id(current_user: dict = Depends(get_current_user)) -> str:
    """
    Dependency to get current user's ID.
    """
    return str(current_user['id'])
