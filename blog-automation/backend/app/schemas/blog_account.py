from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from uuid import UUID

from app.models.blog_account import BlogPlatform, AccountStatus


class BlogAccountBase(BaseModel):
    platform: BlogPlatform
    account_name: str = Field(..., max_length=255)
    blog_url: Optional[HttpUrl] = None


class BlogAccountCreate(BlogAccountBase):
    auth_credentials: Dict[str, Any]


class BlogAccountUpdate(BaseModel):
    account_name: Optional[str] = Field(None, max_length=255)
    blog_url: Optional[HttpUrl] = None
    auth_credentials: Optional[Dict[str, Any]] = None
    status: Optional[AccountStatus] = None


class BlogAccountResponse(BlogAccountBase):
    id: UUID
    user_id: UUID
    status: AccountStatus
    last_sync_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BlogAccountVerify(BaseModel):
    platform: BlogPlatform
    auth_credentials: Dict[str, Any]