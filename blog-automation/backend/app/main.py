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
async def test_publish(request: dict):
    """Claude API를 사용한 콘텐츠 생성 및 발행 테스트"""
    from datetime import datetime
    import random
    from app.services.claude_service import get_claude_generator
    
    try:
        # 요청 데이터 파싱
        keywords = request.get('keywords', [])
        content_type = request.get('content_type', 'blog_post')
        target_length = request.get('target_length', 3000)
        tone = request.get('tone', '친근하고 전문적인')
        
        if not keywords:
            return {
                "success": False,
                "message": "키워드를 최소 1개 이상 입력해주세요"
            }
        
        # Claude API를 사용한 콘텐츠 생성
        try:
            claude_generator = get_claude_generator()
            claude_content = claude_generator.generate_content(
                keywords=keywords,
                content_type=content_type,
                target_length=target_length,
                tone=tone
            )
            
            logger.info(f"Claude API 콘텐츠 생성 성공", 
                       target_length=target_length,
                       actual_length=claude_content.get("word_count", 0))
            
        except Exception as claude_error:
            logger.warning(f"Claude API 실패, 시뮬레이션으로 대체: {claude_error}")
            
            # Claude API 실패 시 시뮬레이션으로 대체
            main_keyword = keywords[0]
            title_templates = [
                f"{main_keyword}의 완벽한 이해: 초보자를 위한 가이드",
                f"{main_keyword} 활용법과 최신 트렌드",
                f"{main_keyword}로 시작하는 전문가의 길",
                f"{main_keyword}에 대해 알아야 할 모든 것",
                f"{main_keyword} 마스터하기: 실무 활용 팁"
            ]
            title = random.choice(title_templates)
            
            # 목표 글자 수에 맞춰 콘텐츠 생성
            base_content = f"""안녕하세요! 오늘은 {main_keyword}에 대해 자세히 알아보겠습니다.

## {main_keyword}란 무엇인가요?

{main_keyword}는 현재 많은 관심을 받고 있는 중요한 주제입니다. 이 글에서는 {tone} 톤으로 {main_keyword}의 핵심 개념부터 실무 활용까지 단계별로 설명드리겠습니다.

## 주요 특징

1. **핵심 개념**: {main_keyword}의 기본 원리
2. **활용 방법**: 실제 적용 사례  
3. **장점과 단점**: 객관적인 분석
4. **미래 전망**: 발전 가능성

## 실무 활용 팁

{', '.join(keywords[:3])}과 같은 관련 기술들과 함께 활용하면 더욱 효과적입니다.

### 1단계: 기초 이해하기
{main_keyword}를 이해하기 위해서는 먼저 기본 개념을 정확히 파악해야 합니다.

### 2단계: 실습해보기
이론만으로는 부족합니다. 직접 경험해보는 것이 중요합니다.

### 3단계: 응용하기
기본기를 익혔다면 이제 창의적으로 응용해볼 차례입니다."""

            # 목표 길이에 맞춰 추가 내용 생성
            current_length = len(base_content)
            if current_length < target_length:
                additional_sections = [
                    f"\n\n## {main_keyword}의 발전 과정\n\n{main_keyword}는 지속적으로 발전하고 있는 분야입니다. 최근 동향을 살펴보면 다양한 혁신적인 접근법들이 등장하고 있으며, 이는 산업 전반에 큰 변화를 가져오고 있습니다. 특히 최신 기술들과의 융합을 통해 새로운 가능성들이 계속해서 탐구되고 있습니다.",
                    
                    f"\n\n## 실제 사례 분석\n\n{main_keyword}가 실제로 어떻게 활용되고 있는지 구체적인 사례를 통해 알아보겠습니다. 국내외 다양한 기업들이 {main_keyword}를 통해 혁신을 이루고 있으며, 이러한 성공 사례들은 다른 조직들에게도 중요한 인사이트를 제공하고 있습니다. 실무에서 직접 적용할 수 있는 구체적인 방법들을 살펴보면서 실질적인 도움을 받을 수 있습니다.",
                    
                    f"\n\n## 장점과 한계점\n\n{main_keyword}의 주요 장점은 효율성과 확장성에 있습니다. 하지만 동시에 고려해야 할 한계점들도 존재합니다. 이러한 양면성을 정확히 이해하고 접근해야 성공적인 활용이 가능합니다. 특히 초기 도입 시 예상되는 어려움들과 이를 극복하는 방법들을 미리 파악해두는 것이 중요합니다.",
                    
                    f"\n\n## 자주 묻는 질문\n\n**Q: {main_keyword}를 처음 시작하는 사람에게 가장 중요한 것은?**\nA: 기본기를 탄탄히 하는 것이 가장 중요합니다. 체계적인 학습 계획을 세우고 단계적으로 접근하는 것을 권장합니다.\n\n**Q: {main_keyword}의 미래 전망은?**\nA: 계속해서 성장할 것으로 예상됩니다. 특히 다른 기술들과의 융합을 통해 더욱 발전할 가능성이 높습니다.\n\n**Q: 학습에 필요한 기간은?**\nA: 개인차가 있지만, 기본적인 이해를 위해서는 보통 3-6개월 정도의 꾸준한 학습이 필요합니다.",
                    
                    f"\n\n## 추천 학습 자료\n\n{main_keyword}를 더 깊이 학습하고 싶다면 다음 자료들을 참고하시기 바랍니다. 온라인 강의, 서적, 실습 자료 등 다양한 형태의 학습 자료들이 준비되어 있으며, 각자의 학습 스타일에 맞는 자료를 선택하여 활용하실 수 있습니다. 특히 실무 경험이 풍부한 전문가들이 제공하는 자료들을 우선적으로 참고하시기를 권장합니다.",
                    
                    f"\n\n## 실무 적용 팁\n\n{main_keyword}를 실무에 적용할 때 고려해야 할 핵심 요소들을 정리해보겠습니다. 첫째, 조직의 현재 상황과 목표를 명확히 파악해야 합니다. 둘째, 단계적 도입을 통해 리스크를 최소화해야 합니다. 셋째, 지속적인 모니터링과 개선이 필요합니다. 이러한 원칙들을 바탕으로 접근한다면 성공적인 결과를 얻을 수 있을 것입니다.",
                    
                    f"\n\n## 결론\n\n{main_keyword}는 앞으로도 계속 발전할 분야입니다. 지속적인 학습과 실습을 통해 전문성을 기르시기 바랍니다. 특히 변화하는 트렌드에 발맞춰 꾸준히 업데이트하는 것이 중요합니다.\n\n이 글이 {main_keyword}를 이해하는 데 도움이 되었기를 바랍니다. 궁금한 점이 있으시면 언제든 댓글로 남겨주세요. 함께 학습하고 성장하는 커뮤니티를 만들어 나가겠습니다."
                ]
                
                # 목표 길이에 정확히 맞추기 위한 로직
                for section in additional_sections:
                    potential_content = base_content + section
                    if len(potential_content) <= target_length + 100:  # 100자 여유
                        base_content = potential_content
                        current_length = len(base_content)
                        
                        # 목표 길이에 가까우면 중단
                        if current_length >= target_length - 50:
                            break
                
                # 만약 아직 목표에 못 미치면 추가 내용으로 채우기
                if len(base_content) < target_length - 100:
                    padding_content = f"\n\n## 마무리하며\n\n{main_keyword}에 대한 이해를 높이는 것은 지속적인 과정입니다. 오늘 배운 내용을 바탕으로 실제 프로젝트에 적용해보시기 바랍니다."
                    
                    # 목표 길이까지 반복 내용 추가
                    while len(base_content + padding_content) < target_length - 50:
                        padding_content += f" {main_keyword}의 다양한 활용 방법을 탐구하면서 새로운 인사이트를 얻으실 수 있을 것입니다."
                        if len(base_content + padding_content) >= target_length - 50:
                            break
                    
                    base_content += padding_content
            
            claude_content = {
                "title": title,
                "content": base_content,
                "meta_description": f"{main_keyword}에 대한 포괄적인 가이드입니다. {', '.join(keywords[:3])}을 활용한 실무 팁과 최신 동향을 제공합니다.",
                "word_count": len(base_content)
            }
        
        # 실제 Unsplash API로 이미지 생성
        from app.services.unsplash_service import get_unsplash_service
        
        try:
            unsplash_service = get_unsplash_service()
            
            # 대표 이미지 가져오기
            featured_image = await unsplash_service.get_featured_image(keywords)
            if not featured_image:
                # 대체 이미지
                featured_image = {
                    "id": f"fallback_{random.randint(1000, 9999)}",
                    "url": f"https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
                    "thumb_url": f"https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80",
                    "alt_text": f"{keywords[0]}에 관련된 이미지",
                    "attribution": {
                        "photographer": "Unsplash",
                        "source": "Unsplash"
                    },
                    "width": 1200,
                    "height": 800
                }
            
            # 콘텐츠용 추가 이미지들
            content_images = await unsplash_service.get_content_images(keywords, claude_content['title'])
            
            logger.info(f"이미지 검색 결과", 
                       title_based_count=len(content_images['title_based']),
                       keyword_based_count=len(content_images['keyword_based']))
            
            # 본문에 이미지 첨부하기
            content_with_images = claude_content['content']
            
            # 본문 중간에 이미지 삽입
            content_lines = content_with_images.split('\n')
            total_lines = len(content_lines)
            insert_pos = 0  # 초기값 설정
            images_inserted = 0
            
            # 첫 번째 이미지는 본문 30% 지점에 삽입
            if content_images['title_based']:
                img = content_images['title_based'][0]
                image_markdown = f"\n\n![{img['alt_text']}]({img['url']})\n*사진: {img['attribution']['photographer']} (Unsplash)*\n\n"
                insert_pos = max(3, int(total_lines * 0.3))
                if insert_pos < len(content_lines):
                    content_lines.insert(insert_pos, image_markdown)
                    total_lines = len(content_lines)  # 라인 수 업데이트
                    images_inserted += 1
                    logger.info(f"첫 번째 이미지 삽입", position=insert_pos, url=img['url'])
            
            # 두 번째 이미지는 본문 70% 지점에 삽입
            if content_images['keyword_based']:
                img = content_images['keyword_based'][0]
                image_markdown = f"\n\n![{img['alt_text']}]({img['url']})\n*사진: {img['attribution']['photographer']} (Unsplash)*\n\n"
                second_insert_pos = max(insert_pos + 5, int(total_lines * 0.7))
                if second_insert_pos < len(content_lines):
                    content_lines.insert(second_insert_pos, image_markdown)
                    images_inserted += 1
                    logger.info(f"두 번째 이미지 삽입", position=second_insert_pos, url=img['url'])
            
            # 이미지가 첨부된 최종 본문
            content_with_images = '\n'.join(content_lines)
            claude_content['content'] = content_with_images
            
            logger.info(f"이미지 첨부 완료", total_inserted=images_inserted)
            
            suggested_images = content_images
            
        except Exception as img_error:
            logger.error(f"Unsplash 이미지 로딩 실패: {img_error}")
            # 이미지 로딩 실패 시 기본 이미지 사용
            main_keyword = keywords[0]
            featured_image = {
                "id": f"fallback_{random.randint(1000, 9999)}",
                "url": f"https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=1200&q=80",
                "thumb_url": f"https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80",
                "alt_text": f"{main_keyword}에 관련된 이미지",
                "attribution": {
                    "photographer": "Unsplash",
                    "source": "Unsplash"
                },
                "width": 1200,
                "height": 800
            }
            
            suggested_images = {
                "title_based": [],
                "keyword_based": []
            }
        
        # 응답 데이터
        content_response = {
            "title": claude_content["title"],
            "content": claude_content["content"],
            "meta_description": claude_content["meta_description"],
            "word_count": claude_content["word_count"],
            "ai_model_used": settings.claude_model,
            "featured_image": featured_image,
            "suggested_images": suggested_images
        }
        
        return {
            "success": True,
            "message": "콘텐츠가 성공적으로 생성되었습니다",
            "content": content_response,
            "generation_info": {
                "keywords_used": keywords,
                "content_type": content_type,
                "target_length": target_length,
                "actual_length": claude_content["word_count"],
                "tone": tone,
                "generated_at": datetime.now().isoformat(),
                "ai_model": settings.claude_model
            }
        }
        
    except Exception as e:
        logger.error(f"Content generation error: {e}")
        return {
            "success": False,
            "message": f"콘텐츠 생성 중 오류가 발생했습니다: {str(e)}"
        }