from celery import shared_task
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from datetime import datetime
import structlog
import asyncio

from app.core.database import AsyncSessionLocal
from app.models.publication import Publication, PublicationStatus
from app.models.content import Content, ContentStatus
from app.models.blog_account import BlogAccount
from app.services.publishers import get_publisher
from app.core.security import encryption_service

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3)
def publish_content_task(self, publication_id: str):
    """콘텐츠를 블로그 플랫폼에 발행합니다."""
    
    async def _publish():
        async with AsyncSessionLocal() as db:
            try:
                # Publication 정보 조회
                result = await db.execute(
                    select(Publication)
                    .options(
                        selectinload(Publication.content),
                        selectinload(Publication.blog_account)
                    )
                    .where(Publication.id == publication_id)
                )
                publication = result.scalar_one_or_none()
                
                if not publication:
                    logger.error("Publication not found", publication_id=publication_id)
                    return
                
                # 발행 상태 업데이트
                publication.status = PublicationStatus.PENDING
                await db.commit()
                
                # 인증 정보 복호화
                encrypted_creds = publication.blog_account.auth_credentials.get("encrypted")
                decrypted_creds = encryption_service.decrypt(encrypted_creds)
                credentials = eval(decrypted_creds)  # JSON으로 저장하는 것이 더 안전함
                
                # Publisher 인스턴스 생성
                publisher = get_publisher(
                    platform=publication.blog_account.platform,
                    credentials=credentials
                )
                
                # 콘텐츠 발행
                result = await publisher.publish(
                    title=publication.content.title,
                    content=publication.content.content,
                    meta_description=publication.content.meta_description,
                    keywords=publication.content.keywords
                )
                
                if result["success"]:
                    publication.status = PublicationStatus.PUBLISHED
                    publication.platform_post_id = result.get("post_id")
                    publication.platform_post_url = result.get("url")
                    publication.published_at = datetime.utcnow()
                    
                    # 콘텐츠 상태 업데이트
                    publication.content.status = ContentStatus.PUBLISHED
                    
                    logger.info(
                        "Content published successfully",
                        publication_id=publication_id,
                        platform=publication.blog_account.platform,
                        url=result.get("url")
                    )
                else:
                    publication.status = PublicationStatus.FAILED
                    publication.error_message = result.get("error", "Unknown error")
                    
                    logger.error(
                        "Content publication failed",
                        publication_id=publication_id,
                        error=result.get("error")
                    )
                
                await db.commit()
                
            except Exception as e:
                logger.error(
                    "Publication task failed",
                    publication_id=publication_id,
                    error=str(e)
                )
                
                # 발행 실패 상태 업데이트
                publication.status = PublicationStatus.FAILED
                publication.error_message = str(e)
                publication.retry_count += 1
                await db.commit()
                
                # 재시도
                if self.request.retries < self.max_retries:
                    raise self.retry(exc=e, countdown=300 * (2 ** self.request.retries))
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_publish())


@shared_task
def publish_scheduled_content():
    """스케줄된 콘텐츠를 발행합니다."""
    
    async def _publish_scheduled():
        async with AsyncSessionLocal() as db:
            now = datetime.utcnow()
            
            # 발행 예정인 콘텐츠 조회
            result = await db.execute(
                select(Content).where(
                    and_(
                        Content.status == ContentStatus.SCHEDULED,
                        Content.scheduled_at <= now
                    )
                )
            )
            contents = result.scalars().all()
            
            for content in contents:
                # 연결된 블로그 계정으로 발행
                pub_result = await db.execute(
                    select(BlogAccount).where(
                        BlogAccount.user_id == content.user_id
                    )
                )
                accounts = pub_result.scalars().all()
                
                for account in accounts:
                    # Publication 레코드 생성
                    publication = Publication(
                        content_id=content.id,
                        blog_account_id=account.id
                    )
                    db.add(publication)
                    await db.commit()
                    await db.refresh(publication)
                    
                    # 발행 태스크 실행
                    publish_content_task.delay(str(publication.id))
            
            logger.info(
                "Scheduled content publishing initiated",
                count=len(contents)
            )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_publish_scheduled())


@shared_task
def retry_failed_publications():
    """실패한 발행 작업을 재시도합니다."""
    
    async def _retry_failed():
        async with AsyncSessionLocal() as db:
            # 재시도 가능한 실패 발행 조회
            result = await db.execute(
                select(Publication).where(
                    and_(
                        Publication.status == PublicationStatus.FAILED,
                        Publication.retry_count < 3
                    )
                )
            )
            publications = result.scalars().all()
            
            for publication in publications:
                publish_content_task.delay(str(publication.id))
            
            logger.info(
                "Failed publication retry initiated",
                count=len(publications)
            )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_retry_failed())