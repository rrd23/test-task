from pydantic import BaseModel, validator
from typing import List, Optional
from datetime import datetime
from .user import User
from ..models.models import NotificationStatus

class CampaignUserStatus(BaseModel):
    user: User
    status: NotificationStatus  # ✅ Исправлено: используем enum вместо str
    sent_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CampaignCreate(BaseModel):
    text: str
    user_ids: List[int]
    
    @validator('text')
    def validate_text(cls, v):
        if len(v.strip()) == 0:
            raise ValueError('Text cannot be empty')
        if len(v) > 1000:
            raise ValueError('Text too long (max 1000 characters)')
        return v.strip()
    
    @validator('user_ids')
    def validate_user_ids(cls, v):
        if len(v) == 0:
            raise ValueError('At least one user_id required')
        if len(v) > 1000:
            raise ValueError('Too many users (max 1000)')
        return v

class Campaign(BaseModel):
    id: int
    text: str
    created_at: datetime
    users: List[CampaignUserStatus] = []

    class Config:
        from_attributes = True

class CampaignStatus(BaseModel):
    id: int
    status: str
    total_notifications: int
    sent_notifications: int
    failed_notifications: int
    pending_notifications: int
    created_at: datetime
    completed_at: Optional[datetime] = None