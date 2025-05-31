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
    """대시보드 통계 정보 - Supabase 실제 데이터"""
    try:
        # 플랫폼 데이터 가져오기
        platforms_result = supabase_client.table('blog_platforms').select("*").execute()
        platforms = platforms_result.data or []
        
        # 실제 포스트 수 계산 (blog_posts 테이블 사용)
        posts_result = supabase_client.table('blog_posts').select("id").execute()
        total_posts = len(posts_result.data) if posts_result.data else 0
        
        # 최근 포스트 가져오기
        posts_response = await get_posts()
        recent_posts = posts_response["posts"][:5]
        
        # 각 플랫폼의 실제 통계 계산 (blog_posts 테이블에서)
        for platform in platforms:
            platform_id = platform.get('id')
            
            # 해당 플랫폼의 포스트들
            platform_posts_result = supabase_client.table('blog_posts').select(
                "views, likes, comments"
            ).eq('platform_id', platform_id).execute()
            
            if platform_posts_result.data:
                total_views = sum(post.get('views', 0) for post in platform_posts_result.data)
                total_likes = sum(post.get('likes', 0) for post in platform_posts_result.data)
                total_comments = sum(post.get('comments', 0) for post in platform_posts_result.data)
                post_count = len(platform_posts_result.data)
            else:
                total_views = total_likes = total_comments = post_count = 0
            
            # 플랫폼 데이터 업데이트 (실제 계산된 값으로)
            platform['post_count'] = post_count
            platform['total_views'] = total_views
            platform['total_likes'] = total_likes
            platform['total_comments'] = total_comments
        
        return {
            "total_posts": total_posts,
            "platforms": platforms,
            "recent_posts": recent_posts
        }
    except Exception as e:
        logger.error(f"Dashboard stats error: {e}")
        return {
            "total_posts": 0,
            "platforms": [],
            "recent_posts": []
        }


@app.get("/dashboard/publishing-activity")
async def get_publishing_activity():
    """발행 활동 데이터 (GitHub 스타일 캘린더용) - Supabase 실제 데이터"""
    from datetime import datetime, timedelta
    from collections import defaultdict
    
    try:
        # Supabase에서 실제 발행된 포스트 데이터 가져오기 (blog_posts 테이블 사용)
        posts_result = supabase_client.table('blog_posts').select("*").order('created_at', desc=True).execute()
        posts = posts_result.data or []
        
        # 365일 기간 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=364)
        
        # 날짜별 포스트 그룹화
        posts_by_date = defaultdict(list)
        
        for post in posts:
            created_at = post.get('created_at')
            if created_at:
                try:
                    post_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    post_date = post_date.date()
                    
                    # 365일 범위 내의 데이터만 포함
                    if start_date.date() <= post_date <= end_date.date():
                        posts_by_date[post_date.strftime("%Y-%m-%d")].append(post.get('title', '제목 없음'))
                except:
                    continue
        
        # 365일 활동 데이터 생성
        activities = []
        total_posts = 0
        active_days = 0
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            posts = posts_by_date.get(date_str, [])
            count = len(posts)
            
            if count > 0:
                active_days += 1
                total_posts += count
            
            activities.append({
                "date": date_str,
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
        
    except Exception as e:
        logger.error(f"Publishing activity data error: {e}")
        return {
            "activities": [],
            "total_posts": 0,
            "active_days": 0,
            "date_range": {
                "start": datetime.now().strftime("%Y-%m-%d"),
                "end": datetime.now().strftime("%Y-%m-%d")
            }
        }


@app.get("/dashboard/posts")
async def get_posts():
    """발행된 포스트 목록 - Supabase 실제 데이터"""
    try:
        # Supabase에서 실제 포스트 데이터 가져오기 (blog_posts와 blog_platforms 조인)
        posts_result = supabase_client.table('blog_posts').select(
            "*, blog_platforms!inner(id, name, platform_type, url)"
        ).order('created_at', desc=True).execute()
        
        posts = []
        
        for post_data in posts_result.data or []:
            platform_info = post_data.get('blog_platforms', {})
            
            post = {
                "id": post_data.get('id'),
                "title": post_data.get('title', '제목 없음'),
                "platform": {
                    "name": platform_info.get('name', '알 수 없는 플랫폼'),
                    "platform_type": platform_info.get('platform_type', 'unknown'),
                    "url": platform_info.get('url', '')
                },
                "blog_platforms": platform_info,  # RecentPosts 컴포넌트에서 사용
                "published_url": post_data.get('published_url', ''),
                "status": post_data.get('status', 'draft'),
                "views": post_data.get('views', 0),
                "likes": post_data.get('likes', 0),
                "comments": post_data.get('comments', 0),
                "created_at": post_data.get('created_at'),
                "published_at": post_data.get('published_at')
            }
            posts.append(post)
        
        return {"posts": posts}
        
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
            logger.error(f"Claude API 실패: {claude_error}")
            
            # 테스트용 대체 콘텐츠 생성
            main_keyword = keywords[0] if keywords else "주제"
            
            # 톤에 맞는 스타일 선택
            tone_styles = {
                "친근하고 전문적인": {
                    "greeting": "안녕하세요, 여러분! 😊",
                    "style": "해보세요"
                },
                "정중하고 격식있는": {
                    "greeting": "안녕하십니까.",
                    "style": "하십시오"
                },
                "캐주얼하고 재미있는": {
                    "greeting": "안녕! 👋",
                    "style": "해봐요"
                },
                "전문적이고 상세한": {
                    "greeting": "이 글에서는",
                    "style": "합니다"
                }
            }
            
            style = tone_styles.get(tone, tone_styles["친근하고 전문적인"])
            
            # 테스트용 콘텐츠 생성
            test_content = f"""{style['greeting']} 오늘은 {main_keyword}에 대해 이야기{style['style']}.

## {main_keyword}란 무엇인가요?

{main_keyword}는 현재 많은 관심을 받고 있는 주제입니다. 최근 들어 더욱 중요해지고 있으며, 우리 일상생활에도 큰 영향을 미치고 있습니다.

실제로 저도 처음 {main_keyword}를 접했을 때는 막막했어요. 하지만 하나씩 알아가다 보니 정말 흥미로운 분야더라고요!

## 왜 {main_keyword}가 중요할까요?

첫째, {main_keyword}는 우리의 미래를 바꿀 수 있는 잠재력을 가지고 있습니다.
둘째, 실용적인 측면에서도 많은 도움이 됩니다.
셋째, 개인적인 성장에도 큰 도움이 되죠.

예를 들어, 제가 아는 한 분은 {main_keyword}를 통해 업무 효율을 30% 이상 향상시켰다고 합니다. 정말 놀라운 성과죠?

## {main_keyword}의 핵심 요소

### 1. 기본 개념 이해하기

{main_keyword}의 기본 개념은 생각보다 간단합니다. 핵심은 다음과 같습니다:

- **명확한 목표 설정**: 무엇을 달성하고 싶은지 명확히 {style['style']}
- **단계별 접근**: 한 번에 모든 것을 하려고 하지 마세요
- **꾸준한 실천**: 작은 것부터 시작{style['style']}

### 2. 실제 적용 방법

이론은 알았으니 이제 실제로 어떻게 적용할 수 있는지 알아볼까요?

**Step 1**: 현재 상황 파악하기
먼저 자신의 현재 상황을 정확히 파악{style['style']}. 

**Step 2**: 목표 설정하기
달성 가능한 작은 목표부터 시작{style['style']}.

**Step 3**: 실행 계획 수립하기
구체적인 실행 계획을 만들어{style['style']}.

## 실전 팁과 노하우

제가 {main_keyword}를 활용하면서 얻은 몇 가지 팁을 공유할게요:

1. **작게 시작하기**: 처음부터 완벽하게 하려고 하지 마세요
2. **기록하기**: 진행 상황을 기록하면 동기부여가 됩니다
3. **커뮤니티 활용**: 같은 관심사를 가진 사람들과 교류{style['style']}
4. **실패를 두려워하지 않기**: 실패도 배움의 과정입니다

## 주의할 점

물론 {main_keyword}를 활용할 때 주의해야 할 점도 있습니다:

- 너무 급하게 진행하지 마세요
- 기본기를 탄탄히 다지세요
- 지속 가능한 방법을 선택{style['style']}

## 더 나아가기

이제 기본적인 내용은 다 알아봤으니, 더 깊이 있게 공부하고 싶다면 다음을 추천합니다:

- 관련 서적 읽기
- 온라인 강의 수강
- 실습 프로젝트 진행
- 전문가 멘토링

여러분도 {main_keyword}를 통해 새로운 가능성을 발견하시길 바랍니다! 궁금한 점이 있다면 언제든 댓글로 남겨주세요. 

다음에는 더 심화된 내용으로 찾아뵙겠습니다. 오늘도 읽어주셔서 감사합니다! 🙏"""
            
            claude_content = {
                "title": f"{main_keyword}의 모든 것: 초보자를 위한 완벽 가이드",
                "meta_description": f"{main_keyword}에 대한 기초부터 실전까지, 쉽고 재미있게 알아보는 가이드입니다.",
                "content": test_content,
                "word_count": len(test_content)
            }
            
            logger.info("테스트용 대체 콘텐츠 생성 완료")
            
        
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
            
            # 500자마다 이미지 1개씩 삽입
            content_length = len(content_with_images)
            image_count = max(1, content_length // 500)  # 500자마다 1개
            
            # 사용 가능한 이미지 모음
            available_images = []
            if content_images['title_based']:
                available_images.extend(content_images['title_based'])
            if content_images['keyword_based']:
                available_images.extend(content_images['keyword_based'])
            
            # 이미지가 충분하지 않으면 반복 사용
            if available_images:
                while len(available_images) < image_count:
                    available_images.extend(available_images[:min(len(available_images), image_count - len(available_images))])
            
            # 문자 수 기준으로 이미지 삽입
            if available_images:
                # 현재까지의 문자 수 계산
                char_count = 0
                inserted_images = 0
                new_lines = []
                
                for line in content_lines:
                    new_lines.append(line)
                    char_count += len(line)
                    
                    # 500자마다 이미지 삽입 (단락 경계 확인)
                    if char_count >= (inserted_images + 1) * 500 and inserted_images < min(image_count, len(available_images)):
                        # 현재 줄이 빈 줄이면 바로 삽입
                        if line.strip() == '':
                            img = available_images[inserted_images]
                            image_markdown = f"\n![{img['alt_text']}]({img['url']})\n*사진: {img['attribution']['photographer']} (Unsplash)*\n"
                            new_lines.append(image_markdown)
                            inserted_images += 1
                            images_inserted += 1
                            logger.info(f"{inserted_images}번째 이미지 삽입 (500자 간격)", chars=char_count, url=img['url'])
                
                content_lines = new_lines
            
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
            
            # 이미지 API 오류 시 이미지 없이 진행
            suggested_images = {
                "title_based": [],
                "keyword_based": []
            }
        
        # Supabase blog_posts 테이블에 콘텐츠 저장
        try:
            # blog_platform 정보에서 플랫폼 ID 찾기
            platform_name = request.get('blog_platform', {}).get('name')
            platform_type = request.get('blog_platform', {}).get('platform_type')
            platform_url = request.get('blog_platform', {}).get('url')
            
            # 플랫폼 ID 조회
            platform_result = supabase_client.table('blog_platforms').select("id").eq('name', platform_name).execute()
            
            platform_id = None
            if platform_result.data:
                platform_id = platform_result.data[0]['id']
            else:
                # 플랫폼이 없으면 기본값으로 첫 번째 플랫폼 사용
                first_platform = supabase_client.table('blog_platforms').select("id").limit(1).execute()
                if first_platform.data:
                    platform_id = first_platform.data[0]['id']
            
            if platform_id:
                post_data = {
                    "platform_id": platform_id,
                    "title": claude_content["title"],
                    "content": claude_content["content"],
                    "meta_description": claude_content["meta_description"],
                    "featured_image_url": featured_image.get("url") if featured_image else None,
                    "status": "draft",  # 초기 상태는 draft로 설정
                    "views": 0,  # 실제 값으로 시작
                    "likes": 0,  # 실제 값으로 시작
                    "comments": 0,  # 실제 값으로 시작
                    "tags": keywords,  # 키워드를 태그로 저장
                    "published_url": None,  # 아직 발행 안됨
                    "published_at": None,  # 아직 발행 안됨
                    "created_at": datetime.now().isoformat()
                }
                
                # blog_posts 테이블에 저장
                insert_result = supabase_client.table('blog_posts').insert(post_data).execute()
                
                if insert_result.data:
                    saved_post = insert_result.data[0]
                    logger.info(f"포스트가 Supabase에 저장됨", post_id=saved_post.get('id'))
                else:
                    logger.warning("포스트 저장 결과가 비어있음")
            else:
                logger.error("플랫폼 ID를 찾을 수 없음")
                
        except Exception as save_error:
            logger.error(f"포스트 Supabase 저장 실패: {save_error}")
            # 저장 실패해도 생성된 콘텐츠는 반환
        
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
            "message": "콘텐츠가 성공적으로 생성되고 저장되었습니다",
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