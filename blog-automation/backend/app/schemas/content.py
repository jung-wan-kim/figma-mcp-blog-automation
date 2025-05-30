from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from uuid import UUID

from app.models.content import ContentStatus, ContentType


class ContentBase(BaseModel):
    title: str = Field(..., max_length=500)
    content_type: ContentType = ContentType.BLOG_POST
    keywords: List[str] = []
    target_keywords: List[str] = []
    style_preset: Optional[str] = None


class ContentCreate(ContentBase):
    scheduled_at: Optional[datetime] = None


class ContentUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    content: Optional[str] = None
    content_type: Optional[ContentType] = None
    meta_description: Optional[str] = None
    keywords: Optional[List[str]] = None
    target_keywords: Optional[List[str]] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[ContentStatus] = None


class ContentGenerate(BaseModel):
    keywords: List[str] = Field(..., min_items=1)
    content_type: ContentType = ContentType.BLOG_POST
    style_preset: Optional[str] = None
    target_length: int = Field(1500, ge=500, le=5000)
    tone: Optional[str] = None
    include_images: bool = True


class ContentResponse(ContentBase):
    id: UUID
    user_id: UUID
    content: str
    meta_description: Optional[str]
    seo_score: int
    readability_score: int
    word_count: int
    status: ContentStatus
    ai_model_used: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ContentWithPublications(ContentResponse):
    publications: List["PublicationResponse"] = []
    
    class Config:
        from_attributes = True