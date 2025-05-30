from celery import shared_task
from sqlalchemy import select, and_, func
from sqlalchemy.orm import selectinload
from datetime import datetime, date, timedelta
import structlog
import asyncio

from app.core.database import AsyncSessionLocal
from app.models.analytics import Analytics
from app.models.publication import Publication, PublicationStatus
from app.models.content import Content
from app.services.analytics_collectors import get_analytics_collector

logger = structlog.get_logger()


@shared_task
def collect_analytics_for_publication(publication_id: str):
    """특정 발행물의 분석 데이터를 수집합니다."""
    
    async def _collect():
        async with AsyncSessionLocal() as db:
            try:
                # Publication 정보 조회
                result = await db.execute(
                    select(Publication)
                    .options(
                        selectinload(Publication.blog_account),
                        selectinload(Publication.content)
                    )
                    .where(Publication.id == publication_id)
                )
                publication = result.scalar_one_or_none()
                
                if not publication or publication.status != PublicationStatus.PUBLISHED:
                    return
                
                # Analytics collector 생성
                collector = get_analytics_collector(
                    platform=publication.blog_account.platform
                )
                
                # 분석 데이터 수집
                analytics_data = await collector.collect(
                    platform_post_id=publication.platform_post_id,
                    platform_post_url=publication.platform_post_url
                )
                
                # Analytics 레코드 생성 또는 업데이트
                today = date.today()
                analytics_result = await db.execute(
                    select(Analytics).where(
                        and_(
                            Analytics.publication_id == publication_id,
                            Analytics.date == today
                        )
                    )
                )
                analytics = analytics_result.scalar_one_or_none()
                
                if not analytics:
                    analytics = Analytics(
                        content_id=publication.content_id,
                        publication_id=publication_id,
                        date=today
                    )
                    db.add(analytics)
                
                # 데이터 업데이트
                analytics.views = analytics_data.get("views", 0)
                analytics.unique_visitors = analytics_data.get("unique_visitors", 0)
                analytics.clicks = analytics_data.get("clicks", 0)
                analytics.shares = analytics_data.get("shares", 0)
                analytics.comments = analytics_data.get("comments", 0)
                analytics.likes = analytics_data.get("likes", 0)
                analytics.avg_time_on_page = analytics_data.get("avg_time_on_page", 0.0)
                analytics.bounce_rate = analytics_data.get("bounce_rate", 0.0)
                
                await db.commit()
                
                logger.info(
                    "Analytics collected successfully",
                    publication_id=publication_id,
                    views=analytics.views
                )
                
            except Exception as e:
                logger.error(
                    "Analytics collection failed",
                    publication_id=publication_id,
                    error=str(e)
                )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_collect())


@shared_task
def collect_all_analytics():
    """모든 발행된 콘텐츠의 분석 데이터를 수집합니다."""
    
    async def _collect_all():
        async with AsyncSessionLocal() as db:
            # 발행된 모든 Publication 조회
            result = await db.execute(
                select(Publication).where(
                    Publication.status == PublicationStatus.PUBLISHED
                )
            )
            publications = result.scalars().all()
            
            for publication in publications:
                collect_analytics_for_publication.delay(str(publication.id))
            
            logger.info(
                "Analytics collection scheduled for all publications",
                count=len(publications)
            )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_collect_all())


@shared_task
def generate_daily_report():
    """일일 성과 리포트를 생성합니다."""
    
    async def _generate_report():
        async with AsyncSessionLocal() as db:
            yesterday = date.today() - timedelta(days=1)
            
            # 어제의 전체 성과 집계
            result = await db.execute(
                select(
                    func.count(Analytics.id).label("total_posts"),
                    func.sum(Analytics.views).label("total_views"),
                    func.sum(Analytics.clicks).label("total_clicks"),
                    func.sum(Analytics.shares).label("total_shares"),
                    func.avg(Analytics.avg_time_on_page).label("avg_time_on_page"),
                    func.avg(Analytics.bounce_rate).label("avg_bounce_rate")
                ).where(Analytics.date == yesterday)
            )
            
            report_data = result.one()
            
            # 상위 콘텐츠 조회
            top_content_result = await db.execute(
                select(
                    Content.title,
                    Analytics.views,
                    Analytics.shares
                )
                .join(Analytics)
                .where(Analytics.date == yesterday)
                .order_by(Analytics.views.desc())
                .limit(10)
            )
            
            top_contents = []
            for row in top_content_result:
                top_contents.append({
                    "title": row.title,
                    "views": row.views,
                    "shares": row.shares
                })
            
            report = {
                "date": yesterday.isoformat(),
                "summary": {
                    "total_posts": report_data.total_posts or 0,
                    "total_views": report_data.total_views or 0,
                    "total_clicks": report_data.total_clicks or 0,
                    "total_shares": report_data.total_shares or 0,
                    "avg_time_on_page": report_data.avg_time_on_page or 0.0,
                    "avg_bounce_rate": report_data.avg_bounce_rate or 0.0
                },
                "top_contents": top_contents
            }
            
            logger.info(
                "Daily report generated",
                date=yesterday.isoformat(),
                total_views=report["summary"]["total_views"]
            )
            
            # TODO: 이메일로 리포트 전송
            
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_generate_report())


@shared_task
def collect_seo_rankings(content_id: str):
    """콘텐츠의 SEO 순위를 수집합니다."""
    
    async def _collect_seo():
        async with AsyncSessionLocal() as db:
            # Content 정보 조회
            result = await db.execute(
                select(Content).where(Content.id == content_id)
            )
            content = result.scalar_one_or_none()
            
            if not content:
                return
            
            # SEO 순위 수집 (Google Search Console API 사용)
            # TODO: Search Console API 구현
            
            logger.info(
                "SEO rankings collection scheduled",
                content_id=content_id
            )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_collect_seo())