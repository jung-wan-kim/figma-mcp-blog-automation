from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
# from app.api import auth, users, contents, blog_accounts, publications, analytics
from app.core.database import supabase_client


# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up Blog Automation System")
    
    # Test Supabase connection
    try:
        result = supabase_client.table('blog_platforms').select("*").limit(1).execute()
        logger.info(f"Supabase connection successful, found {len(result.data)} blog platforms")
    except Exception as e:
        logger.error(f"Supabase connection failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Blog Automation System")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (Temporarily disabled - need to update to Supabase)
# TODO: Update these routers to use Supabase instead of SQLAlchemy
# app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
# app.include_router(users.router, prefix=f"{settings.api_prefix}/users", tags=["users"])
# app.include_router(contents.router, prefix=f"{settings.api_prefix}/contents", tags=["contents"])
# app.include_router(blog_accounts.router, prefix=f"{settings.api_prefix}/blog-accounts", tags=["blog-accounts"])
# app.include_router(publications.router, prefix=f"{settings.api_prefix}/publications", tags=["publications"])
# app.include_router(analytics.router, prefix=f"{settings.api_prefix}/analytics", tags=["analytics"])


@app.get("/")
async def root():
    return {"message": "Welcome to Blog Automation System API"}


@app.get("/health")
async def health_check():
    try:
        # Check Supabase connection
        result = supabase_client.table('blog_platforms').select("count").execute()
        return {
            "status": "healthy",
            "supabase": "connected",
            "database": "ready"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "supabase": "error",
            "error": str(e)
        }


# Dashboard endpoints (temporary mock data)
@app.get("/dashboard/stats")
async def get_dashboard_stats():
    """대시보드 통계 정보"""
    try:
        # Get platforms data
        platforms_result = supabase_client.table('blog_platforms').select("*").execute()
        platforms = platforms_result.data or []
        
        # 실제 포스트 데이터를 가져와서 계산
        posts_response = await get_posts()
        recent_posts = posts_response["posts"][:5]  # 최근 5개만
        total_posts = len(posts_response["posts"])
        
        return {
            "total_posts": total_posts,
            "platforms": platforms,
            "recent_posts": recent_posts
        }
    except Exception as e:
        return {
            "total_posts": 0,
            "platforms": [],
            "recent_posts": []
        }


@app.get("/dashboard/publishing-activity")
async def get_publishing_activity():
    """발행 활동 데이터 (GitHub 스타일 캘린더용)"""
    from datetime import datetime, timedelta
    import random
    
    # 현재 날짜 기준으로 365일 전부터의 데이터 생성
    end_date = datetime.now()
    start_date = end_date - timedelta(days=364)  # 365일 (0부터 364까지)
    
    activities = []
    total_posts = 0
    active_days = 0
    
    # 매일의 활동 데이터 생성
    current_date = start_date
    while current_date <= end_date:
        # 랜덤하게 포스트 수 결정 (0-3개, 가중치로 0이 많이 나오도록)
        weights = [0.7, 0.15, 0.1, 0.05]  # 0개: 70%, 1개: 15%, 2개: 10%, 3개: 5%
        count = random.choices([0, 1, 2, 3], weights=weights)[0]
        
        # 주말에는 활동이 적도록 조정
        if current_date.weekday() >= 5:  # 토요일, 일요일
            count = random.choices([0, 1], weights=[0.8, 0.2])[0]
        
        posts = []
        if count > 0:
            active_days += 1
            total_posts += count
            # 샘플 포스트 제목 생성
            sample_titles = [
                "AI 기술 트렌드 분석",
                "React 개발 팁",
                "데이터 과학 입문",
                "웹 개발 베스트 프랙티스",
                "머신러닝 알고리즘",
                "블록체인 기술 이해",
                "클라우드 컴퓨팅 가이드",
                "소프트웨어 아키텍처",
                "DevOps 실무",
                "프론트엔드 최적화"
            ]
            posts = random.sample(sample_titles, min(count, len(sample_titles)))
        
        activities.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "count": count,
            "posts": posts
        })
        
        current_date += timedelta(days=1)
    
    return {
        "activities": activities,
        "total_posts": total_posts,
        "active_days": active_days,
        "date_range": {
            "start": start_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        }
    }


@app.get("/dashboard/posts")
async def get_posts():
    """발행된 포스트 목록"""
    from datetime import datetime, timedelta
    import random
    
    # 최근 30일간의 발행된 글 목록 생성
    posts = []
    platforms = ["tistory", "wordpress", "naver"]
    titles = [
        "AI 기술 트렌드 2024: 생성형 AI의 미래",
        "React 18의 새로운 기능들과 성능 최적화",
        "데이터 과학 입문: Python으로 시작하는 분석",
        "웹 개발 베스트 프랙티스와 보안 가이드",
        "머신러닝 알고리즘 비교 분석",
        "블록체인 기술의 실제 활용 사례",
        "클라우드 네이티브 아키텍처 설계",
        "DevOps 자동화 도구 비교",
        "프론트엔드 성능 최적화 전략",
        "마이크로서비스 패턴과 모범 사례",
        "GraphQL vs REST API 선택 가이드",
        "도커와 쿠버네티스 실무 활용",
        "자바스크립트 ES2024 새로운 기능들",
        "UI/UX 디자인 트렌드와 사용자 경험",
        "사이버 보안 위협과 대응 방안"
    ]
    
    # 최근 2주간 랜덤하게 포스트 생성 (총 10-15개)
    for i in range(random.randint(10, 15)):
        days_ago = random.randint(0, 14)
        created_date = datetime.now() - timedelta(days=days_ago)
        
        post = {
            "id": f"post_{i+1}",
            "title": random.choice(titles),
            "platform": random.choice(platforms),
            "status": "published",
            "views": random.randint(50, 1000),
            "likes": random.randint(5, 100),
            "comments": random.randint(0, 25),
            "created_at": created_date.isoformat(),
            "published_at": created_date.isoformat(),
            "url": f"https://example-{random.choice(platforms)}.com/post-{i+1}"
        }
        posts.append(post)
    
    # 날짜순으로 정렬 (최신순)
    posts.sort(key=lambda x: x['created_at'], reverse=True)
    
    return {
        "posts": posts
    }


@app.get("/dashboard/platforms")
async def get_platforms():
    """연결된 플랫폼 목록"""
    try:
        result = supabase_client.table('blog_platforms').select("*").execute()
        return {
            "platforms": result.data
        }
    except Exception as e:
        return {
            "platforms": [],
            "error": str(e)
        }


@app.post("/dashboard/platforms")
async def add_platform(platform: dict):
    """새 플랫폼 추가"""
    return {
        "success": False,
        "message": "API implementation pending"
    }


@app.post("/test/publish")
async def test_publish(content: dict):
    """테스트 발행"""
    return {
        "success": False,
        "message": "API implementation pending"
    }