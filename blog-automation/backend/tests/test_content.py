import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import uuid4

from app.models.content import Content, ContentStatus
from app.models.user import User


class TestContent:
    """콘텐츠 관련 테스트"""
    
    async def test_create_content(
        self, 
        client: AsyncClient, 
        auth_headers: dict,
        db_session: AsyncSession
    ):
        """콘텐츠 생성 테스트"""
        response = await client.post(
            "/api/v1/contents/",
            json={
                "title": "Test Blog Post",
                "keywords": ["test", "blog"],
                "content_type": "blog_post"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Blog Post"
        assert data["keywords"] == ["test", "blog"]
        assert data["status"] == "draft"
    
    async def test_generate_content(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """콘텐츠 생성 API 테스트"""
        response = await client.post(
            "/api/v1/contents/generate",
            json={
                "keywords": ["Python", "FastAPI"],
                "content_type": "blog_post",
                "target_length": 1000,
                "style_preset": "technical"
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["keywords"] == ["Python", "FastAPI"]
        assert data["status"] == "draft"
    
    async def test_list_contents(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession
    ):
        """콘텐츠 목록 조회 테스트"""
        # 테스트 콘텐츠 생성
        content1 = Content(
            user_id=test_user.id,
            title="Test Content 1",
            content="Test content body",
            keywords=["test1"],
            status=ContentStatus.DRAFT
        )
        content2 = Content(
            user_id=test_user.id,
            title="Test Content 2",
            content="Test content body 2",
            keywords=["test2"],
            status=ContentStatus.PUBLISHED
        )
        
        db_session.add_all([content1, content2])
        await db_session.commit()
        
        # 전체 목록 조회
        response = await client.get("/api/v1/contents/", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        
        # 상태별 필터링
        response = await client.get(
            "/api/v1/contents/?status=draft",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Content 1"
    
    async def test_get_content(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession
    ):
        """콘텐츠 상세 조회 테스트"""
        content = Content(
            user_id=test_user.id,
            title="Test Content",
            content="Test content body",
            keywords=["test"]
        )
        db_session.add(content)
        await db_session.commit()
        await db_session.refresh(content)
        
        response = await client.get(
            f"/api/v1/contents/{content.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Content"
        assert data["id"] == str(content.id)
    
    async def test_get_nonexistent_content(
        self,
        client: AsyncClient,
        auth_headers: dict
    ):
        """존재하지 않는 콘텐츠 조회 테스트"""
        nonexistent_id = str(uuid4())
        response = await client.get(
            f"/api/v1/contents/{nonexistent_id}",
            headers=auth_headers
        )
        
        assert response.status_code == 404
    
    async def test_update_content(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession
    ):
        """콘텐츠 수정 테스트"""
        content = Content(
            user_id=test_user.id,
            title="Original Title",
            content="Original content",
            keywords=["original"]
        )
        db_session.add(content)
        await db_session.commit()
        await db_session.refresh(content)
        
        response = await client.put(
            f"/api/v1/contents/{content.id}",
            json={
                "title": "Updated Title",
                "keywords": ["updated", "test"]
            },
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["keywords"] == ["updated", "test"]
    
    async def test_delete_content(
        self,
        client: AsyncClient,
        auth_headers: dict,
        test_user: User,
        db_session: AsyncSession
    ):
        """콘텐츠 삭제 테스트"""
        content = Content(
            user_id=test_user.id,
            title="To Be Deleted",
            content="This will be deleted",
            keywords=["delete"]
        )
        db_session.add(content)
        await db_session.commit()
        await db_session.refresh(content)
        
        response = await client.delete(
            f"/api/v1/contents/{content.id}",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        # 삭제 확인
        result = await db_session.execute(
            select(Content).where(Content.id == content.id)
        )
        deleted_content = result.scalar_one_or_none()
        assert deleted_content is None
    
    async def test_unauthorized_access(self, client: AsyncClient):
        """인증되지 않은 접근 테스트"""
        response = await client.get("/api/v1/contents/")
        assert response.status_code == 401