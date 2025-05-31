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
        
        # 실제 콘텐츠 수 계산
        contents_result = supabase_client.table('contents').select("id").execute()
        total_posts = len(contents_result.data) if contents_result.data else 0
        
        # 최근 포스트 가져오기
        posts_response = await get_posts()
        recent_posts = posts_response["posts"][:5]
        
        # 각 플랫폼의 실제 통계 계산
        for platform in platforms:
            platform_id = platform.get('id')
            
            # 해당 플랫폼의 계정 수
            accounts_result = supabase_client.table('blog_accounts').select("id").eq('platform_id', platform_id).execute()
            account_count = len(accounts_result.data) if accounts_result.data else 0
            
            # 해당 플랫폼의 발행 통계
            if accounts_result.data:
                account_ids = [acc['id'] for acc in accounts_result.data]
                publications_result = supabase_client.table('publications').select(
                    "views, likes, comments"
                ).in_('blog_account_id', account_ids).execute()
                
                if publications_result.data:
                    total_views = sum(pub.get('views', 0) for pub in publications_result.data)
                    total_likes = sum(pub.get('likes', 0) for pub in publications_result.data)
                    total_comments = sum(pub.get('comments', 0) for pub in publications_result.data)
                    post_count = len(publications_result.data)
                else:
                    total_views = total_likes = total_comments = post_count = 0
            else:
                total_views = total_likes = total_comments = post_count = account_count = 0
            
            # 플랫폼 데이터 업데이트
            platform['account_count'] = account_count
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
        # Supabase에서 실제 발행된 포스트 데이터 가져오기
        contents_result = supabase_client.table('contents').select("*").order('created_at', desc=True).execute()
        contents = contents_result.data or []
        
        # 365일 기간 설정
        end_date = datetime.now()
        start_date = end_date - timedelta(days=364)
        
        # 날짜별 포스트 그룹화
        posts_by_date = defaultdict(list)
        
        for content in contents:
            created_at = content.get('created_at')
            if created_at:
                try:
                    content_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    content_date = content_date.date()
                    
                    # 365일 범위 내의 데이터만 포함
                    if start_date.date() <= content_date <= end_date.date():
                        posts_by_date[content_date.strftime("%Y-%m-%d")].append(content.get('title', '제목 없음'))
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
        # Supabase에서 실제 콘텐츠 데이터 가져오기
        contents_result = supabase_client.table('contents').select("*").order('created_at', desc=True).execute()
        contents = contents_result.data or []
        
        # publications 테이블에서 발행 정보 가져오기
        publications_result = supabase_client.table('publications').select("*").execute()
        publications = publications_result.data or []
        
        # blog_accounts와 blog_platforms 조인하여 플랫폼 정보 가져오기
        accounts_result = supabase_client.table('blog_accounts').select(
            "id, platform_id, account_name, blog_platforms(platform_type, name)"
        ).execute()
        accounts = accounts_result.data or []
        
        # 포스트 데이터 변환
        posts = []
        
        for content in contents:
            # 해당 콘텐츠의 발행 정보 찾기
            content_publications = [p for p in publications if p.get('content_id') == content.get('id')]
            
            if content_publications:
                for pub in content_publications:
                    # 계정 정보 찾기
                    account = next((a for a in accounts if a.get('id') == pub.get('blog_account_id')), None)
                    
                    platform_info = account.get('blog_platforms', {}) if account else {}
                    
                    post = {
                        "id": content.get('id'),
                        "title": content.get('title', '제목 없음'),
                        "platform": platform_info.get('platform_type', 'unknown'),
                        "platform_name": platform_info.get('name', account.get('account_name', '알 수 없는 플랫폼') if account else '알 수 없는 플랫폼'),
                        "status": pub.get('status', 'draft'),
                        "views": pub.get('views', 0),
                        "likes": pub.get('likes', 0),
                        "comments": pub.get('comments', 0),
                        "created_at": content.get('created_at'),
                        "published_at": pub.get('published_at'),
                        "url": pub.get('published_url', '')
                    }
                    posts.append(post)
            else:
                # 발행되지 않은 콘텐츠도 포함
                post = {
                    "id": content.get('id'),
                    "title": content.get('title', '제목 없음'),
                    "platform": 'draft',
                    "platform_name": '임시저장',
                    "status": 'draft',
                    "views": 0,
                    "likes": 0,
                    "comments": 0,
                    "created_at": content.get('created_at'),
                    "published_at": None,
                    "url": ''
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
            return {
                "success": False,
                "message": f"Claude API 호출 실패: {str(claude_error)}"
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
        
        # Supabase에 콘텐츠 저장
        try:
            content_data = {
                "title": claude_content["title"],
                "content": claude_content["content"],
                "meta_description": claude_content["meta_description"],
                "keywords": keywords,
                "content_type": content_type,
                "word_count": claude_content["word_count"],
                "tone": tone,
                "ai_model_used": settings.claude_model,
                "featured_image_url": featured_image.get("url") if featured_image else None,
                "status": "generated",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            # contents 테이블에 저장
            insert_result = supabase_client.table('contents').insert(content_data).execute()
            
            if insert_result.data:
                saved_content = insert_result.data[0]
                logger.info(f"콘텐츠가 Supabase에 저장됨", content_id=saved_content.get('id'))
            else:
                logger.warning("콘텐츠 저장 결과가 비어있음")
                
        except Exception as save_error:
            logger.error(f"콘텐츠 Supabase 저장 실패: {save_error}")
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