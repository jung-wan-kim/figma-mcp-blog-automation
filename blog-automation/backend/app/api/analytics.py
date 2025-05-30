from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from datetime import date, datetime, timedelta
from uuid import UUID

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.analytics import Analytics
from app.models.content import Content
from app.schemas.analytics import AnalyticsResponse, AnalyticsSummary

router = APIRouter()


@router.get("/content/{content_id}", response_model=List[AnalyticsResponse])
async def get_content_analytics(
    content_id: UUID,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify content ownership
    content_result = await db.execute(
        select(Content).where(
            and_(Content.id == content_id, Content.user_id == current_user.id)
        )
    )
    if not content_result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    query = select(Analytics).where(Analytics.content_id == content_id)
    
    if start_date:
        query = query.where(Analytics.date >= start_date)
    
    if end_date:
        query = query.where(Analytics.date <= end_date)
    
    query = query.order_by(Analytics.date.desc())
    
    result = await db.execute(query)
    analytics = result.scalars().all()
    
    return analytics


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    start_date: date = Query(..., description="Start date for analytics period"),
    end_date: date = Query(..., description="End date for analytics period"),
    content_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Build base query
    query = select(
        func.sum(Analytics.views).label("total_views"),
        func.sum(Analytics.clicks).label("total_clicks"),
        func.sum(Analytics.shares).label("total_shares"),
        func.avg(Analytics.avg_time_on_page).label("average_time_on_page"),
        func.avg(Analytics.bounce_rate).label("average_bounce_rate")
    ).join(Content).where(
        and_(
            Content.user_id == current_user.id,
            Analytics.date >= start_date,
            Analytics.date <= end_date
        )
    )
    
    if content_id:
        query = query.where(Analytics.content_id == content_id)
    
    result = await db.execute(query)
    summary_data = result.one()
    
    return AnalyticsSummary(
        total_views=summary_data.total_views or 0,
        total_clicks=summary_data.total_clicks or 0,
        total_shares=summary_data.total_shares or 0,
        average_time_on_page=summary_data.average_time_on_page or 0.0,
        average_bounce_rate=summary_data.average_bounce_rate or 0.0,
        period_start=start_date,
        period_end=end_date
    )


@router.get("/trending", response_model=List[dict])
async def get_trending_content(
    days: int = Query(7, ge=1, le=30, description="Number of days to look back"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    start_date = datetime.now().date() - timedelta(days=days)
    
    query = select(
        Content.id,
        Content.title,
        func.sum(Analytics.views).label("total_views"),
        func.sum(Analytics.shares).label("total_shares"),
        func.avg(Analytics.avg_time_on_page).label("avg_time_on_page")
    ).join(Analytics).where(
        and_(
            Content.user_id == current_user.id,
            Analytics.date >= start_date
        )
    ).group_by(Content.id, Content.title).order_by(
        func.sum(Analytics.views).desc()
    ).limit(limit)
    
    result = await db.execute(query)
    trending = []
    
    for row in result:
        trending.append({
            "content_id": row.id,
            "title": row.title,
            "total_views": row.total_views or 0,
            "total_shares": row.total_shares or 0,
            "avg_time_on_page": row.avg_time_on_page or 0.0
        })
    
    return trending