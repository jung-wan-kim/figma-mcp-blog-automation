#!/usr/bin/env python3
"""
간단한 테스트 서버 - Claude API 연동 테스트용
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from anthropic import Anthropic
import os
from dotenv import load_dotenv
import aiohttp
from app.core.supabase import get_supabase_client

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="Blog Automation Test API",
    description="Claude API 테스트용 간단한 서버",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 모든 오리진 허용 (개발 환경)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Claude 클라이언트 초기화 (선택적)
try:
    claude_client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY")) if os.getenv("CLAUDE_API_KEY") else None
except Exception as e:
    print(f"Claude 클라이언트 초기화 실패: {e}")
    claude_client = None

class ContentRequest(BaseModel):
    keywords: List[str]
    content_type: str = "blog_post"
    target_length: int = 3000  # 기본 3000자로 변경
    tone: Optional[str] = "친근하고 전문적인"

class ImageInfo(BaseModel):
    id: str
    url: str
    thumb_url: str
    alt_text: str
    attribution: Dict[str, str]
    width: int
    height: int

class ContentResponse(BaseModel):
    title: str
    content: str
    meta_description: str
    word_count: int
    ai_model_used: str = "claude-3-sonnet"
    featured_image: ImageInfo
    suggested_images: Dict[str, List[ImageInfo]]

class BlogPlatformInfo(BaseModel):
    name: str
    platform_type: str  # wordpress, tistory, naver
    url: str
    username: Optional[str] = None
    is_active: bool = True

class PublishRequest(BaseModel):
    keywords: List[str]
    content_type: str = "blog_post"
    target_length: int = 3000
    tone: Optional[str] = "친근하고 전문적인"
    blog_platform: BlogPlatformInfo
    
class PublishResponse(BaseModel):
    content: ContentResponse
    platform: BlogPlatformInfo
    status: str
    published_url: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "🤖 AI 블로그 자동화 시스템 테스트 서버",
        "status": "running",
        "claude_api": "connected" if os.getenv("CLAUDE_API_KEY") else "not configured"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "claude_available": bool(os.getenv("CLAUDE_API_KEY"))}

@app.post("/test/generate", response_model=ContentResponse)
async def test_generate_content(request: ContentRequest):
    """Claude API를 사용해서 간단한 콘텐츠 생성 테스트"""
    
    if not os.getenv("CLAUDE_API_KEY"):
        raise HTTPException(status_code=500, detail="Claude API 키가 설정되지 않았습니다")
    
    try:
        # 간단한 프롬프트로 콘텐츠 생성
        prompt = f"""
        다음 키워드를 바탕으로 {request.target_length}자 분량의 블로그 글을 작성해주세요:
        
        키워드: {', '.join(request.keywords)}
        콘텐츠 유형: {request.content_type}
        톤앤매너: {request.tone}
        
        다음 형식으로 작성해주세요:
        
        제목: [SEO 친화적인 제목]
        
        메타설명: [150자 이내의 메타 설명]
        
        본문:
        [HTML 태그를 사용한 구조화된 본문 내용]
        
        요구사항:
        - 자연스러운 한국어 사용
        - HTML 태그로 구조화 (<h2>, <p>, <ul> 등)
        - 키워드를 자연스럽게 포함
        - 독자에게 유용한 실용적 정보 제공
        """
        
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content_text = response.content[0].text
        
        # 응답 파싱 (간단한 방식)
        lines = content_text.split('\n')
        title = ""
        meta_description = ""
        content_body = ""
        
        parsing_content = False
        for line in lines:
            if line.startswith("제목:"):
                title = line.replace("제목:", "").strip()
            elif line.startswith("메타설명:"):
                meta_description = line.replace("메타설명:", "").strip()
            elif line.startswith("본문:"):
                parsing_content = True
            elif parsing_content:
                content_body += line + "\n"
        
        # 기본값 설정
        if not title:
            title = f"{request.keywords[0]}에 대한 완벽 가이드"
        if not meta_description:
            meta_description = f"{request.keywords[0]}에 대해 알아야 할 모든 것을 정리했습니다."
        if not content_body:
            content_body = content_text
        
        # 이미지 검색
        title_images = await search_images(title, count=2)
        keyword_images = await search_images(" ".join(request.keywords), count=2)
        
        # 단어 수 계산 (간단한 방식)
        word_count = len(content_body.split())
        
        return ContentResponse(
            title=title,
            content=content_body.strip(),
            meta_description=meta_description,
            word_count=word_count,
            ai_model_used="claude-3-sonnet",
            featured_image=title_images[0],
            suggested_images={
                "title_based": title_images,
                "keyword_based": keyword_images
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"콘텐츠 생성 실패: {str(e)}")

async def search_images(query: str, count: int = 3) -> List[ImageInfo]:
    """이미지 검색 (기본 이미지 반환)"""
    default_images = [
        ImageInfo(
            id="default_1",
            url="https://via.placeholder.com/800x600/4A90E2/FFFFFF?text=Blog+Image+1",
            thumb_url="https://via.placeholder.com/300x200/4A90E2/FFFFFF?text=Blog+Image+1",
            alt_text="블로그 이미지 1",
            attribution={"photographer": "Placeholder", "source": "Placeholder"},
            width=800, height=600
        ),
        ImageInfo(
            id="default_2", 
            url="https://via.placeholder.com/800x600/50C878/FFFFFF?text=Blog+Image+2",
            thumb_url="https://via.placeholder.com/300x200/50C878/FFFFFF?text=Blog+Image+2",
            alt_text="블로그 이미지 2",
            attribution={"photographer": "Placeholder", "source": "Placeholder"},
            width=800, height=600
        ),
        ImageInfo(
            id="default_3",
            url="https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Blog+Image+3", 
            thumb_url="https://via.placeholder.com/300x200/FF6B6B/FFFFFF?text=Blog+Image+3",
            alt_text="블로그 이미지 3",
            attribution={"photographer": "Placeholder", "source": "Placeholder"},
            width=800, height=600
        )
    ]
    return default_images[:count]

@app.get("/test/claude")
async def test_claude_connection():
    """Claude API 연결 테스트"""
    
    if not claude_client:
        return {"status": "error", "message": "Claude API 키가 설정되지 않았거나 클라이언트 초기화에 실패했습니다"}
    
    try:
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "안녕하세요! Claude API 연결 테스트입니다. 간단히 인사해주세요."}],
            temperature=0.3
        )
        
        return {
            "status": "success",
            "message": "Claude API 연결 성공!",
            "response": response.content[0].text
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Claude API 연결 실패: {str(e)}"
        }

# Supabase 클라이언트 초기화
supabase = get_supabase_client()

# 임시 발행 내역 저장소 (실제로는 데이터베이스 사용)
published_posts = []

@app.post("/test/publish", response_model=PublishResponse)
async def test_publish_content(request: PublishRequest):
    """콘텐츠 생성 및 블로그 발행 시뮬레이션"""
    
    try:
        # 1. 콘텐츠 생성
        content_request = ContentRequest(
            keywords=request.keywords,
            content_type=request.content_type,
            target_length=request.target_length,
            tone=request.tone
        )
        
        content_response = await test_generate_content(content_request)
        
        # 2. 블로그 발행 시뮬레이션
        published_url = f"{request.blog_platform.url}/posts/{len(published_posts) + 1}"
        
        # 발행 내역 저장
        published_post = {
            "id": len(published_posts) + 1,
            "title": content_response.title,
            "content": content_response.content,
            "platform": request.blog_platform.model_dump(),
            "published_url": published_url,
            "published_at": "2024-01-01T00:00:00Z",
            "status": "published",
            "views": 0,
            "likes": 0,
            "comments": 0
        }
        published_posts.append(published_post)
        
        return PublishResponse(
            content=content_response,
            platform=request.blog_platform,
            status="published",
            published_url=published_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"발행 실패: {str(e)}")

@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """대시보드 통계 조회 - Supabase에서 데이터 조회"""
    try:
        # Supabase에서 블로그 플랫폼 조회
        try:
            platforms_response = supabase.table("blog_platforms").select("*").execute()
            platforms = platforms_response.data if platforms_response.data else []
        except Exception as e:
            print(f"플랫폼 조회 오류 (테이블이 없을 수 있음): {e}")
            platforms = []
        
        # Supabase에서 최근 게시물 조회
        try:
            posts_response = supabase.table("blog_posts").select("*").order("created_at", desc=True).limit(5).execute()
            recent_posts = posts_response.data if posts_response.data else []
        except Exception as e:
            print(f"게시물 조회 오류 (테이블이 없을 수 있음): {e}")
            recent_posts = []
        
        # 총 게시물 수 조회
        try:
            total_posts_response = supabase.table("blog_posts").select("id", count="exact").execute()
            total_posts = total_posts_response.count if total_posts_response.count else 0
        except Exception as e:
            print(f"게시물 수 조회 오류: {e}")
            total_posts = 0
        
        return {
            "total_posts": total_posts,
            "platforms": platforms,
            "recent_posts": recent_posts
        }
    except Exception as e:
        # Supabase 연결 실패 시 기본값 반환
        print(f"Supabase 연결 오류: {e}")
        return {
            "total_posts": 0,
            "platforms": [],
            "recent_posts": []
        }

@app.get("/dashboard/posts")
async def get_published_posts():
    """발행된 글 목록 조회 - Supabase에서 조회"""
    try:
        # Supabase에서 게시물 조회 (플랫폼 정보와 함께)
        response = supabase.table("blog_posts").select("*, blog_platforms(*)").order("created_at", desc=True).execute()
        posts = response.data if response.data else []
        
        # 데이터 형식 변환 (프론트엔드 호환)
        formatted_posts = []
        for post in posts:
            platform_info = post.get('blog_platforms', {})
            formatted_posts.append({
                "id": post.get('id'),
                "title": post.get('title'),
                "content": post.get('content'),
                "platform": {
                    "name": platform_info.get('name', ''),
                    "platform_type": platform_info.get('platform_type', ''),
                    "url": platform_info.get('url', ''),
                    "username": platform_info.get('username', '')
                },
                "published_url": post.get('published_url', ''),
                "published_at": post.get('published_at', post.get('created_at')),
                "status": post.get('status', 'draft'),
                "views": post.get('views', 0),
                "likes": post.get('likes', 0),
                "comments": post.get('comments', 0)
            })
        
        return {
            "posts": formatted_posts,
            "total": len(formatted_posts)
        }
    except Exception as e:
        print(f"게시물 목록 조회 오류: {e}")
        return {
            "posts": [],
            "total": 0
        }

@app.get("/dashboard/platforms")
async def get_platforms():
    """등록된 플랫폼 목록 - Supabase에서 조회"""
    try:
        response = supabase.table("blog_platforms").select("*").execute()
        return {"platforms": response.data if response.data else []}
    except Exception as e:
        print(f"플랫폼 조회 오류: {e}")
        return {"platforms": []}

@app.post("/dashboard/platforms")
async def add_platform(platform_data: dict):
    """새 블로그 플랫폼 추가"""
    try:
        response = supabase.table("blog_platforms").insert({
            "name": platform_data["name"],
            "platform_type": platform_data["type"],
            "url": platform_data["url"],
            "username": platform_data.get("username", ""),
            "post_count": 0,
            "total_views": 0,
            "total_likes": 0
        }).execute()
        
        return {"success": True, "platform": response.data[0]}
    except Exception as e:
        print(f"플랫폼 추가 오류: {e}")
        raise HTTPException(status_code=500, detail=f"플랫폼 추가 실패: {str(e)}")

@app.post("/dashboard/posts")
async def save_post(post_data: dict):
    """새 게시물을 Supabase에 저장"""
    try:
        response = supabase.table("blog_posts").insert({
            "title": post_data["title"],
            "content": post_data["content"],
            "platform_id": post_data.get("platform_id"),
            "published_url": post_data.get("published_url", ""),
            "status": post_data.get("status", "published"),
            "views": post_data.get("views", 0),
            "likes": post_data.get("likes", 0),
            "comments": post_data.get("comments", 0),
            "tags": post_data.get("tags", []),
            "meta_description": post_data.get("meta_description", "")
        }).execute()
        
        return {"success": True, "post": response.data[0]}
    except Exception as e:
        print(f"게시물 저장 오류: {e}")
        raise HTTPException(status_code=500, detail=f"게시물 저장 실패: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 블로그 자동화 테스트 서버 시작!")
    print("📖 API 문서: http://localhost:8000/docs")
    print("🤖 Claude API 테스트: http://localhost:8000/test/claude")
    uvicorn.run(app, host="0.0.0.0", port=8000)