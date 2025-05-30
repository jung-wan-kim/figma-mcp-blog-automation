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
    """발행 활동 데이터 (GitHub 스타일 캘린더용) - Supabase 기반"""
    from datetime import datetime, timedelta
    import random
    
    try:
        # Supabase에서 blog_platforms 데이터 기반으로 활동 시뮬레이션
        platforms_result = supabase_client.table('blog_platforms').select("*").execute()
        platforms = platforms_result.data or []
        
        # 플랫폼별 총 포스트 수 합계
        total_platform_posts = sum(platform.get('post_count', 0) for platform in platforms)
        
        # 현재 날짜 기준으로 365일 전부터의 데이터 생성
        end_date = datetime.now()
        start_date = end_date - timedelta(days=364)
        
        activities = []
        total_posts = 0
        active_days = 0
        
        # 실제 플랫폼 데이터를 기반으로 현실적인 활동 패턴 생성
        posts_per_day_avg = total_platform_posts / 365 if total_platform_posts > 0 else 0.1
        
        current_date = start_date
        while current_date <= end_date:
            # 플랫폼 데이터 기반으로 포스트 수 결정
            if posts_per_day_avg > 0:
                # 포아송 분포를 근사한 랜덤 생성
                base_chance = min(posts_per_day_avg * 3, 0.4)  # 최대 40% 확률
                count = 0
                
                # 주말에는 활동 감소
                if current_date.weekday() >= 5:
                    base_chance *= 0.5
                
                if random.random() < base_chance:
                    count = random.choices([1, 2, 3], weights=[0.7, 0.2, 0.1])[0]
            else:
                count = 0
            
            posts = []
            if count > 0:
                active_days += 1
                total_posts += count
                # 실제 플랫폼 이름을 기반으로 포스트 제목 생성
                platform_names = [p.get('name', '블로그') for p in platforms]
                sample_titles = [
                    f"{random.choice(platform_names)}에서 공유하는 AI 기술 트렌드",
                    f"{random.choice(platform_names)} 개발 팁과 노하우",
                    f"데이터 과학 입문 - {random.choice(platform_names)}",
                    f"웹 개발 베스트 프랙티스 by {random.choice(platform_names)}",
                    f"{random.choice(platform_names)}의 최신 기술 분석"
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
            "platforms_data": {
                "total_platform_posts": total_platform_posts,
                "connected_platforms": len(platforms)
            },
            "date_range": {
                "start": start_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
        }
        
    except Exception as e:
        logger.error(f"Publishing activity data error: {e}")
        # 에러 시 기본 빈 데이터 반환
        return {
            "activities": [],
            "total_posts": 0,
            "active_days": 0,
            "platforms_data": {
                "total_platform_posts": 0,
                "connected_platforms": 0
            },
            "date_range": {
                "start": datetime.now().strftime("%Y-%m-%d"),
                "end": datetime.now().strftime("%Y-%m-%d")
            }
        }


@app.get("/dashboard/posts")
async def get_posts():
    """발행된 포스트 목록 - Supabase 플랫폼 데이터 기반"""
    from datetime import datetime, timedelta
    import random
    
    try:
        # Supabase에서 실제 플랫폼 데이터 가져오기
        platforms_result = supabase_client.table('blog_platforms').select("*").execute()
        platforms = platforms_result.data or []
        
        if not platforms:
            return {"posts": []}
        
        # 플랫폼 데이터 기반으로 포스트 생성
        posts = []
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
        
        # 각 플랫폼별로 최근 포스트 생성
        post_id = 1
        for platform in platforms:
            platform_post_count = platform.get('post_count', 0)
            recent_posts_count = min(platform_post_count, random.randint(3, 8))  # 플랫폼당 3-8개 최근 포스트
            
            for i in range(recent_posts_count):
                days_ago = random.randint(0, 30)  # 최근 30일
                created_date = datetime.now() - timedelta(days=days_ago)
                
                post = {
                    "id": f"post_{post_id}",
                    "title": random.choice(titles),
                    "platform": platform.get('platform_type', 'unknown'),
                    "platform_name": platform.get('name', '알 수 없는 플랫폼'),
                    "platform_url": platform.get('url', ''),
                    "status": "published",
                    "views": random.randint(
                        max(1, platform.get('total_views', 100) // 10),
                        platform.get('total_views', 100)
                    ),
                    "likes": random.randint(
                        max(1, platform.get('total_likes', 10) // 5),
                        platform.get('total_likes', 10)
                    ),
                    "comments": random.randint(0, 15),
                    "created_at": created_date.isoformat(),
                    "published_at": created_date.isoformat(),
                    "url": f"{platform.get('url', '')}/post-{post_id}"
                }
                posts.append(post)
                post_id += 1
        
        # 날짜순으로 정렬 (최신순)
        posts.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {
            "posts": posts
        }
        
    except Exception as e:
        logger.error(f"Posts data error: {e}")
        return {"posts": []}


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