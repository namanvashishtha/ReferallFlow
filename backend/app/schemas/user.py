from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from uuid import UUID


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    picture: Optional[str] = None


class UserCreate(UserBase):
    auth0_id: str


class UserUpdate(BaseModel):
    name: Optional[str] = None
    picture: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    auth0_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CredentialsUpdate(BaseModel):
    linkedin_profile_url: Optional[str] = None
    linkedin_username: Optional[str] = None
    linkedin_password: Optional[str] = None
    gmail: Optional[str] = None
    gmail_password: Optional[str] = None


class CredentialsResponse(BaseModel):
    id: UUID
    linkedin_profile_url: Optional[str] = None
    linkedin_username: Optional[str] = None
    gmail: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class Auth0UserInfo(BaseModel):
    sub: str
    email: str
    name: Optional[str] = None
    picture: Optional[str] = None
