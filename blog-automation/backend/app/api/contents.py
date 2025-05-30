from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.content import Content, ContentStatus
from app.schemas.content import (
    ContentCreate, ContentUpdate, ContentResponse, 
    ContentWithPublications, ContentGenerate
)
from app.services.content_generator import ContentGeneratorService
from app.tasks.content_tasks import generate_content_task

router = APIRouter()


@router.post("/", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    content = Content(
        user_id=current_user.id,
        title=content_data.title,
        content="",  # Will be generated
        content_type=content_data.content_type,
        keywords=content_data.keywords,
        target_keywords=content_data.target_keywords,
        style_preset=content_data.style_preset,
        scheduled_at=content_data.scheduled_at,
        status=ContentStatus.DRAFT
    )
    
    db.add(content)
    await db.commit()
    await db.refresh(content)
    
    return content


@router.post("/generate", response_model=ContentResponse)
async def generate_content(
    generate_data: ContentGenerate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Create content record
    content = Content(
        user_id=current_user.id,
        title="",  # Will be generated
        content="",  # Will be generated
        content_type=generate_data.content_type,
        keywords=generate_data.keywords,
        target_keywords=generate_data.keywords,
        style_preset=generate_data.style_preset,
        status=ContentStatus.DRAFT
    )
    
    db.add(content)
    await db.commit()
    await db.refresh(content)
    
    # Trigger async content generation
    generate_content_task.delay(
        content_id=str(content.id),
        keywords=generate_data.keywords,
        content_type=generate_data.content_type.value,
        style_preset=generate_data.style_preset,
        target_length=generate_data.target_length,
        tone=generate_data.tone
    )
    
    return content


@router.get("/", response_model=List[ContentResponse])
async def list_contents(
    status: Optional[ContentStatus] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Content).where(Content.user_id == current_user.id)
    
    if status:
        query = query.where(Content.status == status)
    
    query = query.offset(skip).limit(limit).order_by(Content.created_at.desc())
    
    result = await db.execute(query)
    contents = result.scalars().all()
    
    return contents


@router.get("/{content_id}", response_model=ContentWithPublications)
async def get_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Content).where(
            and_(Content.id == content_id, Content.user_id == current_user.id)
        )
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    return content


@router.put("/{content_id}", response_model=ContentResponse)
async def update_content(
    content_id: UUID,
    content_update: ContentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Content).where(
            and_(Content.id == content_id, Content.user_id == current_user.id)
        )
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Update fields if provided
    update_data = content_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(content, field, value)
    
    await db.commit()
    await db.refresh(content)
    
    return content


@router.delete("/{content_id}")
async def delete_content(
    content_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Content).where(
            and_(Content.id == content_id, Content.user_id == current_user.id)
        )
    )
    content = result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    await db.delete(content)
    await db.commit()
    
    return {"message": "Content deleted successfully"}