from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, HttpUrl, Field


class BlogPlatformBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="플랫폼 이름")
    platform_type: str = Field(..., description="플랫폼 타입 (wordpress, tistory, naver)")
    url: str = Field(..., description="블로그 주소")
    username: Optional[str] = Field(None, max_length=100, description="사용자명")
    config: Optional[Dict[str, Any]] = Field(None, description="플랫폼별 추가 설정")


class BlogPlatformCreate(BlogPlatformBase):
    api_key: Optional[str] = Field(None, description="API 키")
    access_token: Optional[str] = Field(None, description="액세스 토큰")


class BlogPlatformUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    username: Optional[str] = Field(None, max_length=100)
    api_key: Optional[str] = None
    access_token: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class BlogPlatformResponse(BlogPlatformBase):
    id: int
    is_active: bool
    is_verified: bool
    last_verified_at: Optional[datetime]
    total_posts: int
    last_post_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class BlogPlatformStats(BaseModel):
    platform_id: int
    platform_name: str
    total_posts: int
    published_posts: int
    failed_posts: int
    total_views: int
    total_likes: int
    total_comments: int
    last_post_at: Optional[datetime]