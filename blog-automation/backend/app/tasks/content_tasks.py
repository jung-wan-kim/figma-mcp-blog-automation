from celery import shared_task
from sqlalchemy import select
import structlog
import asyncio

from app.core.database import AsyncSessionLocal
from app.models.content import Content, ContentStatus
from app.services.content_generator import ContentGeneratorService

logger = structlog.get_logger()


@shared_task(bind=True, max_retries=3)
def generate_content_task(
    self,
    content_id: str,
    keywords: list,
    content_type: str,
    style_preset: str = None,
    target_length: int = 1500,
    tone: str = None
):
    """콘텐츠를 비동기적으로 생성합니다."""
    
    async def _generate():
        async with AsyncSessionLocal() as db:
            try:
                # 콘텐츠 레코드 조회
                result = await db.execute(
                    select(Content).where(Content.id == content_id)
                )
                content = result.scalar_one_or_none()
                
                if not content:
                    logger.error("Content not found", content_id=content_id)
                    return
                
                # 콘텐츠 생성
                generator = ContentGeneratorService()
                generated_data = await generator.generate_content(
                    keywords=keywords,
                    content_type=content_type,
                    style_preset=style_preset,
                    target_length=target_length,
                    tone=tone
                )
                
                # 콘텐츠 업데이트
                content.title = generated_data["title"]
                content.content = generated_data["content"]
                content.meta_description = generated_data["meta_description"]
                content.seo_score = generated_data["seo_score"]
                content.readability_score = generated_data["readability_score"]
                content.word_count = generated_data["word_count"]
                content.ai_model_used = generated_data["ai_model_used"]
                content.status = ContentStatus.DRAFT
                
                await db.commit()
                
                logger.info(
                    "Content generated successfully",
                    content_id=content_id,
                    title=content.title
                )
                
            except Exception as e:
                logger.error(
                    "Content generation failed",
                    content_id=content_id,
                    error=str(e)
                )
                # 재시도
                raise self.retry(exc=e, countdown=60 * (2 ** self.request.retries))
    
    # 비동기 함수 실행
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_generate())


@shared_task
def schedule_content_generation_batch(user_id: str, batch_size: int = 5):
    """배치로 콘텐츠를 생성합니다."""
    
    async def _schedule_batch():
        async with AsyncSessionLocal() as db:
            # 생성 대기 중인 콘텐츠 조회
            result = await db.execute(
                select(Content).where(
                    Content.user_id == user_id,
                    Content.status == ContentStatus.DRAFT,
                    Content.content == ""
                ).limit(batch_size)
            )
            contents = result.scalars().all()
            
            for content in contents:
                generate_content_task.delay(
                    content_id=str(content.id),
                    keywords=content.keywords,
                    content_type=content.content_type.value,
                    style_preset=content.style_preset
                )
            
            logger.info(
                "Batch content generation scheduled",
                user_id=user_id,
                count=len(contents)
            )
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(_schedule_batch())