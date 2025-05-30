from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
import structlog

from app.core.database import get_db
from app.models.blog_platform import BlogPlatform
from app.models.publication import Publication
from app.schemas.blog_platform import (
    BlogPlatformCreate,
    BlogPlatformUpdate, 
    BlogPlatformResponse,
    BlogPlatformStats
)

logger = structlog.get_logger()
router = APIRouter()


@router.post("/", response_model=BlogPlatformResponse)
async def create_blog_platform(
    platform_data: BlogPlatformCreate,
    db: AsyncSession = Depends(get_db)
):
    """새로운 블로그 플랫폼 등록"""
    try:
        # 중복 확인
        stmt = select(BlogPlatform).where(
            BlogPlatform.url == platform_data.url
        )
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="이미 등록된 블로그 주소입니다"
            )
        
        platform = BlogPlatform(**platform_data.model_dump())
        db.add(platform)
        await db.commit()
        await db.refresh(platform)
        
        logger.info("블로그 플랫폼 등록", platform_id=platform.id, url=platform.url)
        return platform
        
    except Exception as e:
        await db.rollback()
        logger.error("블로그 플랫폼 등록 실패", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="블로그 플랫폼 등록에 실패했습니다"
        )


@router.get("/", response_model=List[BlogPlatformResponse])
async def list_blog_platforms(
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """등록된 블로그 플랫폼 목록 조회"""
    try:
        stmt = select(BlogPlatform)
        if is_active is not None:
            stmt = stmt.where(BlogPlatform.is_active == is_active)
        stmt = stmt.order_by(BlogPlatform.created_at.desc())
        
        result = await db.execute(stmt)
        platforms = result.scalars().all()
        
        return platforms
        
    except Exception as e:
        logger.error("블로그 플랫폼 목록 조회 실패", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="블로그 플랫폼 목록을 가져올 수 없습니다"
        )


@router.get("/{platform_id}", response_model=BlogPlatformResponse)
async def get_blog_platform(
    platform_id: int,
    db: AsyncSession = Depends(get_db)
):
    """특정 블로그 플랫폼 상세 조회"""
    try:
        stmt = select(BlogPlatform).where(BlogPlatform.id == platform_id)
        result = await db.execute(stmt)
        platform = result.scalar_one_or_none()
        
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="블로그 플랫폼을 찾을 수 없습니다"
            )
        
        return platform
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("블로그 플랫폼 조회 실패", platform_id=platform_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="블로그 플랫폼 정보를 가져올 수 없습니다"
        )


@router.get("/{platform_id}/stats", response_model=BlogPlatformStats)
async def get_platform_stats(
    platform_id: int,
    db: AsyncSession = Depends(get_db)
):
    """블로그 플랫폼 통계 조회"""
    try:
        # 플랫폼 존재 확인
        platform_stmt = select(BlogPlatform).where(BlogPlatform.id == platform_id)
        platform_result = await db.execute(platform_stmt)
        platform = platform_result.scalar_one_or_none()
        
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="블로그 플랫폼을 찾을 수 없습니다"
            )
        
        # 발행 통계 조회
        from sqlalchemy import func, case
        
        stats_stmt = select(
            func.count(Publication.id).label("total_posts"),
            func.count(case((Publication.status == "published", 1))).label("published_posts"),
            func.count(case((Publication.status == "failed", 1))).label("failed_posts"),
            func.sum(Publication.views).label("total_views"),
            func.sum(Publication.likes).label("total_likes"),
            func.sum(Publication.comments).label("total_comments")
        ).where(Publication.platform_id == platform_id)
        
        stats_result = await db.execute(stats_stmt)
        stats = stats_result.first()
        
        return BlogPlatformStats(
            platform_id=platform_id,
            platform_name=platform.name,
            total_posts=stats.total_posts or 0,
            published_posts=stats.published_posts or 0,
            failed_posts=stats.failed_posts or 0,
            total_views=stats.total_views or 0,
            total_likes=stats.total_likes or 0,
            total_comments=stats.total_comments or 0,
            last_post_at=platform.last_post_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("플랫폼 통계 조회 실패", platform_id=platform_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="플랫폼 통계를 가져올 수 없습니다"
        )


@router.put("/{platform_id}", response_model=BlogPlatformResponse)
async def update_blog_platform(
    platform_id: int,
    platform_data: BlogPlatformUpdate,
    db: AsyncSession = Depends(get_db)
):
    """블로그 플랫폼 정보 수정"""
    try:
        stmt = select(BlogPlatform).where(BlogPlatform.id == platform_id)
        result = await db.execute(stmt)
        platform = result.scalar_one_or_none()
        
        if not platform:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="블로그 플랫폼을 찾을 수 없습니다"
            )
        
        # 업데이트
        update_data = platform_data.model_dump(exclude_unset=True)
        if update_data:
            await db.execute(
                update(BlogPlatform)
                .where(BlogPlatform.id == platform_id)
                .values(**update_data)
            )
            await db.commit()
            await db.refresh(platform)
        
        logger.info("블로그 플랫폼 수정", platform_id=platform_id)
        return platform
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("블로그 플랫폼 수정 실패", platform_id=platform_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="블로그 플랫폼 수정에 실패했습니다"
        )


@router.delete("/{platform_id}")
async def delete_blog_platform(
    platform_id: int,
    db: AsyncSession = Depends(get_db)
):
    """블로그 플랫폼 삭제"""
    try:
        # 관련 발행 내역 확인
        pub_stmt = select(func.count(Publication.id)).where(
            Publication.platform_id == platform_id
        )
        pub_result = await db.execute(pub_stmt)
        pub_count = pub_result.scalar()
        
        if pub_count > 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"이 플랫폼에 {pub_count}개의 발행 내역이 있어 삭제할 수 없습니다"
            )
        
        # 플랫폼 삭제
        await db.execute(
            delete(BlogPlatform).where(BlogPlatform.id == platform_id)
        )
        await db.commit()
        
        logger.info("블로그 플랫폼 삭제", platform_id=platform_id)
        return {"message": "블로그 플랫폼이 삭제되었습니다"}
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("블로그 플랫폼 삭제 실패", platform_id=platform_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="블로그 플랫폼 삭제에 실패했습니다"
        )