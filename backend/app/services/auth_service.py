from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserCredentials
from app.schemas.user import UserCreate, Auth0UserInfo, CredentialsUpdate
from app.utils.encryption import credential_encryption
from typing import Optional
from datetime import datetime


class AuthService:
    @staticmethod
    def get_or_create_user(db: Session, auth0_info: Auth0UserInfo) -> User:
        user = db.query(User).filter(User.auth0_id == auth0_info.sub).first()
        
        if user:
            return user
        
        user = User(
            auth0_id=auth0_info.sub,
            email=auth0_info.email,
            name=auth0_info.name,
            picture=auth0_info.picture,
        )
        db.add(user)
        try:
            db.commit()
            db.refresh(user)
        except IntegrityError:
            db.rollback()
            user = db.query(User).filter(User.auth0_id == auth0_info.sub).first()
        
        return user
    
    @staticmethod
    def get_user_by_auth0_id(db: Session, auth0_id: str) -> Optional[User]:
        return db.query(User).filter(User.auth0_id == auth0_id).first()
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()


class CredentialService:
    @staticmethod
    def save_credentials(db: Session, user_id: str, credentials_data: CredentialsUpdate) -> UserCredentials:
        existing_cred = db.query(UserCredentials).filter(
            UserCredentials.user_id == user_id
        ).first()
        
        if existing_cred:
            if credentials_data.linkedin_username:
                existing_cred.linkedin_username_encrypted = credential_encryption.encrypt(
                    credentials_data.linkedin_username
                )
            if credentials_data.linkedin_password:
                existing_cred.linkedin_password_encrypted = credential_encryption.encrypt(
                    credentials_data.linkedin_password
                )
            if credentials_data.gmail:
                existing_cred.gmail_encrypted = credential_encryption.encrypt(
                    credentials_data.gmail
                )
            if credentials_data.gmail_password:
                existing_cred.gmail_password_encrypted = credential_encryption.encrypt(
                    credentials_data.gmail_password
                )
            if credentials_data.linkedin_profile_url:
                existing_cred.linkedin_profile_url = credentials_data.linkedin_profile_url
            
            existing_cred.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(existing_cred)
            return existing_cred
        
        new_cred = UserCredentials(
            user_id=user_id,
            linkedin_profile_url=credentials_data.linkedin_profile_url,
            linkedin_username_encrypted=credential_encryption.encrypt(
                credentials_data.linkedin_username
            ) if credentials_data.linkedin_username else None,
            linkedin_password_encrypted=credential_encryption.encrypt(
                credentials_data.linkedin_password
            ) if credentials_data.linkedin_password else None,
            gmail_encrypted=credential_encryption.encrypt(
                credentials_data.gmail
            ) if credentials_data.gmail else None,
            gmail_password_encrypted=credential_encryption.encrypt(
                credentials_data.gmail_password
            ) if credentials_data.gmail_password else None,
        )
        db.add(new_cred)
        db.commit()
        db.refresh(new_cred)
        return new_cred
    
    @staticmethod
    def get_credentials(db: Session, user_id: str) -> Optional[UserCredentials]:
        return db.query(UserCredentials).filter(
            UserCredentials.user_id == user_id
        ).first()
    
    @staticmethod
    def decrypt_credentials(credentials: UserCredentials) -> dict:
        return {
            "linkedin_profile_url": credentials.linkedin_profile_url,
            "linkedin_username": credential_encryption.decrypt(
                credentials.linkedin_username_encrypted
            ) if credentials.linkedin_username_encrypted else None,
            "linkedin_password": credential_encryption.decrypt(
                credentials.linkedin_password_encrypted
            ) if credentials.linkedin_password_encrypted else None,
            "gmail": credential_encryption.decrypt(
                credentials.gmail_encrypted
            ) if credentials.gmail_encrypted else None,
            "gmail_password": credential_encryption.decrypt(
                credentials.gmail_password_encrypted
            ) if credentials.gmail_password_encrypted else None,
        }
