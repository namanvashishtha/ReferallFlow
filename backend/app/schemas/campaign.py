from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from app.models.campaign import CampaignStatus


class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    target_companies: Optional[List[str]] = None
    email_template: Optional[str] = None
    personalization_prompt: Optional[str] = None
    is_ab_test: bool = False
    template_variants: Optional[List[str]] = None


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    target_companies: Optional[List[str]] = None
    email_template: Optional[str] = None
    personalization_prompt: Optional[str] = None
    is_ab_test: Optional[bool] = None
    template_variants: Optional[List[str]] = None
    scheduled_time: Optional[datetime] = None


class CampaignResponse(CampaignBase):
    id: UUID
    user_id: UUID
    status: CampaignStatus
    scheduled_time: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContactBase(BaseModel):
    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    position: Optional[str] = None
    linkedin_profile: Optional[str] = None


class ContactCreate(ContactBase):
    pass


class ContactResponse(ContactBase):
    id: UUID
    campaign_id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True


class EmailLogResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    contact_id: UUID
    email_subject: str
    status: str
    sent_at: Optional[datetime] = None
    is_opened: bool
    opened_at: Optional[datetime] = None
    is_replied: bool
    replied_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
