from typing import Optional, List
from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from uuid import UUID

from app.models.publication import PublicationStatus


class PublicationBase(BaseModel):
    content_id: UUID
    blog_account_id: UUID


class PublicationCreate(PublicationBase):
    pass


class PublicationUpdate(BaseModel):
    status: Optional[PublicationStatus] = None
    platform_post_id: Optional[str] = None
    platform_post_url: Optional[HttpUrl] = None
    error_message: Optional[str] = None


class PublicationResponse(PublicationBase):
    id: UUID
    platform_post_id: Optional[str]
    platform_post_url: Optional[HttpUrl]
    status: PublicationStatus
    published_at: Optional[datetime]
    error_message: Optional[str]
    retry_count: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PublishRequest(BaseModel):
    content_id: UUID
    blog_account_ids: List[UUID] = Field(..., min_items=1)
    publish_immediately: bool = True