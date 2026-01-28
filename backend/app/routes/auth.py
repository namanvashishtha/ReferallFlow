from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
import httpx

from app.db.database import get_db
from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.schemas.user import (
    TokenResponse,
    Auth0UserInfo,
    CredentialsUpdate,
    UserResponse,
    CredentialsResponse,
)
from app.services.auth_service import AuthService, CredentialService
from app.models.user import User

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


@router.post("/auth0-callback", response_model=TokenResponse)
async def auth0_callback(
    token: str,
    db: Session = Depends(get_db),
):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"https://{settings.AUTH0_DOMAIN}/userinfo",
                headers={"Authorization": f"Bearer {token}"},
            )
            response.raise_for_status()
        except httpx.HTTPError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Auth0 token",
            )
    
    user_info = Auth0UserInfo(**response.json())
    user = AuthService.get_or_create_user(db, user_info)
    
    access_token_expires = timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires,
    )
    
    user_schema = UserResponse.from_orm(user)
    return TokenResponse(
        access_token=access_token,
        user=user_schema,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.post("/credentials", response_model=dict)
async def save_user_credentials(
    credentials: CredentialsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cred = CredentialService.save_credentials(
        db, str(current_user.id), credentials
    )
    return {
        "status": "success",
        "message": "Credentials saved securely",
        "credential_id": str(cred.id),
    }


@router.get("/credentials", response_model=dict)
async def get_user_credentials(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cred = CredentialService.get_credentials(db, str(current_user.id))
    
    if not cred:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No credentials found",
        )
    
    decrypted = CredentialService.decrypt_credentials(cred)
    return {
        "id": str(cred.id),
        "linkedin_profile_url": cred.linkedin_profile_url,
        "linkedin_username": decrypted["linkedin_username"],
        "gmail": decrypted["gmail"],
        "created_at": cred.created_at,
        "updated_at": cred.updated_at,
    }


@router.put("/credentials", response_model=dict)
async def update_user_credentials(
    credentials: CredentialsUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cred = CredentialService.save_credentials(
        db, str(current_user.id), credentials
    )
    return {
        "status": "success",
        "message": "Credentials updated securely",
        "credential_id": str(cred.id),
    }
