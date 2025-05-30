from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.blog_account import BlogAccount
from app.schemas.blog_account import (
    BlogAccountCreate, BlogAccountUpdate, BlogAccountResponse, BlogAccountVerify
)
from app.core.security import encryption_service
from app.services.blog_platforms import verify_blog_credentials

router = APIRouter()


@router.post("/", response_model=BlogAccountResponse)
async def create_blog_account(
    account_data: BlogAccountCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Verify credentials before saving
    is_valid = await verify_blog_credentials(
        platform=account_data.platform,
        credentials=account_data.auth_credentials
    )
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog credentials"
        )
    
    # Encrypt credentials
    encrypted_credentials = encryption_service.encrypt(
        str(account_data.auth_credentials)
    )
    
    blog_account = BlogAccount(
        user_id=current_user.id,
        platform=account_data.platform,
        account_name=account_data.account_name,
        blog_url=str(account_data.blog_url) if account_data.blog_url else None,
        auth_credentials={"encrypted": encrypted_credentials}
    )
    
    db.add(blog_account)
    await db.commit()
    await db.refresh(blog_account)
    
    return blog_account


@router.post("/verify", response_model=dict)
async def verify_blog_account(
    verify_data: BlogAccountVerify,
    current_user: User = Depends(get_current_user)
):
    is_valid = await verify_blog_credentials(
        platform=verify_data.platform,
        credentials=verify_data.auth_credentials
    )
    
    return {"valid": is_valid}


@router.get("/", response_model=List[BlogAccountResponse])
async def list_blog_accounts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(BlogAccount).where(BlogAccount.user_id == current_user.id)
    )
    accounts = result.scalars().all()
    
    return accounts


@router.get("/{account_id}", response_model=BlogAccountResponse)
async def get_blog_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(BlogAccount).where(
            and_(BlogAccount.id == account_id, BlogAccount.user_id == current_user.id)
        )
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog account not found"
        )
    
    return account


@router.put("/{account_id}", response_model=BlogAccountResponse)
async def update_blog_account(
    account_id: UUID,
    account_update: BlogAccountUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(BlogAccount).where(
            and_(BlogAccount.id == account_id, BlogAccount.user_id == current_user.id)
        )
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog account not found"
        )
    
    # Update fields if provided
    if account_update.account_name is not None:
        account.account_name = account_update.account_name
    
    if account_update.blog_url is not None:
        account.blog_url = str(account_update.blog_url)
    
    if account_update.status is not None:
        account.status = account_update.status
    
    if account_update.auth_credentials is not None:
        # Verify new credentials
        is_valid = await verify_blog_credentials(
            platform=account.platform,
            credentials=account_update.auth_credentials
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid blog credentials"
            )
        
        encrypted_credentials = encryption_service.encrypt(
            str(account_update.auth_credentials)
        )
        account.auth_credentials = {"encrypted": encrypted_credentials}
    
    await db.commit()
    await db.refresh(account)
    
    return account


@router.delete("/{account_id}")
async def delete_blog_account(
    account_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(BlogAccount).where(
            and_(BlogAccount.id == account_id, BlogAccount.user_id == current_user.id)
        )
    )
    account = result.scalar_one_or_none()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog account not found"
        )
    
    await db.delete(account)
    await db.commit()
    
    return {"message": "Blog account deleted successfully"}