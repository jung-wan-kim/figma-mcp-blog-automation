from typing import Optional, Dict
from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID


class AnalyticsBase(BaseModel):
    content_id: UUID
    publication_id: Optional[UUID] = None
    date: date


class AnalyticsResponse(AnalyticsBase):
    id: UUID
    
    # Traffic metrics
    views: int
    unique_visitors: int
    clicks: int
    
    # Engagement metrics
    shares: int
    comments: int
    likes: int
    avg_time_on_page: float
    bounce_rate: float
    
    # SEO metrics
    keyword_rankings: Optional[Dict[str, int]]
    search_impressions: int
    search_clicks: int
    
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AnalyticsSummary(BaseModel):
    total_views: int
    total_clicks: int
    total_shares: int
    average_time_on_page: float
    average_bounce_rate: float
    period_start: date
    period_end: date