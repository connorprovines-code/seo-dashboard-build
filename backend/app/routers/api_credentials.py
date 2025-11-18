"""API Credentials router"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import json

from app.core.database import get_db
from app.core.deps import get_current_user
from app.core.security import encrypt_data, decrypt_data
from app.models.user import User
from app.models.api_credential import ApiCredential
from app.schemas.api_credential import (
    ApiCredentialCreate,
    ApiCredentialResponse,
    ApiCredentialCheck
)
from app.services.dataforseo import DataForSEOService

router = APIRouter(prefix="/api/credentials", tags=["credentials"])


@router.post("/setup/{provider}", status_code=status.HTTP_201_CREATED)
async def setup_api_credentials(
    provider: str,
    credentials_data: dict,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Store and test API credentials for a provider.
    Credentials are encrypted before storage.
    """
    valid_providers = ["dataforseo", "google", "anthropic"]
    if provider not in valid_providers:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid provider. Must be one of: {valid_providers}"
        )

    # Test credentials before saving
    try:
        if provider == "dataforseo":
            login = credentials_data.get("login")
            password = credentials_data.get("password")

            if not login or not password:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="DataForSEO requires 'login' and 'password'"
                )

            service = DataForSEOService(login, password)
            test_result = await service.test_credentials()

            if not test_result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid credentials: {test_result.get('error')}"
                )

        # Add validation for other providers here
        # elif provider == "google":
        #     test_result = await test_google_oauth(credentials_data.get("access_token"))
        # elif provider == "anthropic":
        #     test_result = await test_anthropic_key(credentials_data.get("api_key"))

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to validate credentials: {str(e)}"
        )

    # Encrypt credentials
    encrypted = encrypt_data(json.dumps(credentials_data))

    # Store in database (upsert)
    cred_record = db.query(ApiCredential)\
        .filter(
            ApiCredential.user_id == current_user.id,
            ApiCredential.provider == provider
        )\
        .first()

    if cred_record:
        # Update existing
        cred_record.credentials_encrypted = encrypted
        cred_record.is_active = True
        cred_record.last_verified_at = datetime.utcnow()
    else:
        # Create new
        cred_record = ApiCredential(
            user_id=current_user.id,
            provider=provider,
            credentials_encrypted=encrypted,
            is_active=True,
            last_verified_at=datetime.utcnow()
        )
        db.add(cred_record)

    db.commit()
    db.refresh(cred_record)

    return {
        "success": True,
        "provider": provider,
        "message": f"{provider} credentials saved successfully",
        "credential": ApiCredentialResponse.from_orm(cred_record)
    }


@router.get("/check/{provider}", response_model=ApiCredentialCheck)
async def check_credentials_exist(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Check if user has credentials for a provider.
    Used by frontend to determine if setup modal should show.
    """
    cred = db.query(ApiCredential)\
        .filter(
            ApiCredential.user_id == current_user.id,
            ApiCredential.provider == provider,
            ApiCredential.is_active == True
        )\
        .first()

    return ApiCredentialCheck(
        exists=cred is not None,
        provider=provider,
        last_verified=cred.last_verified_at if cred else None
    )


@router.get("/{provider}", response_model=ApiCredentialResponse)
async def get_credentials(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get API credentials for a provider (returns metadata only, not actual credentials)"""
    cred = db.query(ApiCredential)\
        .filter(
            ApiCredential.user_id == current_user.id,
            ApiCredential.provider == provider,
            ApiCredential.is_active == True
        )\
        .first()

    if not cred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No credentials found for provider: {provider}"
        )

    return cred


@router.delete("/{provider}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_credentials(
    provider: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove stored API credentials"""
    db.query(ApiCredential)\
        .filter(
            ApiCredential.user_id == current_user.id,
            ApiCredential.provider == provider
        )\
        .update({"is_active": False})

    db.commit()
    return None


def get_user_dataforseo_service(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> DataForSEOService:
    """
    Dependency to get DataForSEO service for current user.
    Raises 404 if credentials not found.
    """
    cred = db.query(ApiCredential)\
        .filter(
            ApiCredential.user_id == current_user.id,
            ApiCredential.provider == "dataforseo",
            ApiCredential.is_active == True
        )\
        .first()

    if not cred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="DataForSEO credentials not configured. Please add your API credentials in settings."
        )

    # Decrypt credentials
    try:
        credentials = json.loads(decrypt_data(cred.credentials_encrypted))
        return DataForSEOService(
            login=credentials["login"],
            password=credentials["password"]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load credentials: {str(e)}"
        )
