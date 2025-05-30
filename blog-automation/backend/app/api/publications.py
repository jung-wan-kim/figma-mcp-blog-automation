from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from uuid import UUID

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.publication import Publication
from app.models.content import Content
from app.models.blog_account import BlogAccount
from app.schemas.publication import PublicationResponse, PublishRequest
from app.tasks.publishing_tasks import publish_content_task

router = APIRouter()


@router.post("/publish", response_model=List[PublicationResponse])
async def publish_content(
    publish_request: PublishRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify content ownership
    content_result = await db.execute(
        select(Content).where(
            and_(Content.id == publish_request.content_id, Content.user_id == current_user.id)
        )
    )
    content = content_result.scalar_one_or_none()
    
    if not content:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )
    
    # Verify blog account ownership
    account_result = await db.execute(
        select(BlogAccount).where(
            and_(
                BlogAccount.id.in_(publish_request.blog_account_ids),
                BlogAccount.user_id == current_user.id
            )
        )
    )
    accounts = account_result.scalars().all()
    
    if len(accounts) != len(publish_request.blog_account_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="One or more blog accounts not found"
        )
    
    # Create publication records
    publications = []
    for account_id in publish_request.blog_account_ids:
        publication = Publication(
            content_id=publish_request.content_id,
            blog_account_id=account_id
        )
        db.add(publication)
        publications.append(publication)
    
    await db.commit()
    
    # Trigger async publishing tasks
    if publish_request.publish_immediately:
        for publication in publications:
            await db.refresh(publication)
            publish_content_task.delay(str(publication.id))
    
    return publications


@router.get("/", response_model=List[PublicationResponse])
async def list_publications(
    content_id: Optional[UUID] = None,
    blog_account_id: Optional[UUID] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = select(Publication).options(
        selectinload(Publication.content),
        selectinload(Publication.blog_account)
    ).join(Content).where(Content.user_id == current_user.id)
    
    if content_id:
        query = query.where(Publication.content_id == content_id)
    
    if blog_account_id:
        query = query.where(Publication.blog_account_id == blog_account_id)
    
    query = query.offset(skip).limit(limit).order_by(Publication.created_at.desc())
    
    result = await db.execute(query)
    publications = result.scalars().all()
    
    return publications


@router.get("/{publication_id}", response_model=PublicationResponse)
async def get_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Publication).options(
            selectinload(Publication.content),
            selectinload(Publication.blog_account)
        ).join(Content).where(
            and_(Publication.id == publication_id, Content.user_id == current_user.id)
        )
    )
    publication = result.scalar_one_or_none()
    
    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found"
        )
    
    return publication


@router.post("/{publication_id}/retry")
async def retry_publication(
    publication_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(Publication).options(
            selectinload(Publication.content)
        ).join(Content).where(
            and_(Publication.id == publication_id, Content.user_id == current_user.id)
        )
    )
    publication = result.scalar_one_or_none()
    
    if not publication:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publication not found"
        )
    
    if publication.status not in ["failed", "error"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only retry failed publications"
        )
    
    # Reset status and trigger retry
    publication.status = "retrying"
    publication.retry_count += 1
    await db.commit()
    
    publish_content_task.delay(str(publication.id))
    
    return {"message": "Publication retry initiated"}