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
# from app.core.supabase import get_supabase_client  # 임시 비활성화

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
    ai_model_used: str = "claude-4-sonnet"
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
            model="claude-4-sonnet-20250514",
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
            ai_model_used="claude-4-sonnet",
            featured_image=title_images[0],
            suggested_images={
                "title_based": title_images,
                "keyword_based": keyword_images
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"콘텐츠 생성 실패: {str(e)}")

async def search_images(query: str, count: int = 3) -> List[ImageInfo]:
    """Unsplash API를 사용한 키워드 기반 이미지 검색 (retry 로직 포함)"""
    
    # Unsplash API 설정
    unsplash_access_key = os.getenv("UNSPLASH_ACCESS_KEY")
    
    if not unsplash_access_key:
        print(f"Unsplash API 키가 설정되지 않음 - Lorem Picsum 사용")
        return await search_images_fallback(query, count)
    
    print(f"Unsplash API 키 확인됨: {unsplash_access_key[:10]}...")
    
    # Retry 설정
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"Unsplash API 시도 {attempt + 1}/{max_retries}")
            return await _search_images_single_attempt(query, count, unsplash_access_key)
        except Exception as e:
            print(f"시도 {attempt + 1} 실패: {str(e)}")
            if attempt == max_retries - 1:  # 마지막 시도
                print("모든 재시도 실패 - 백업 이미지 사용")
                return await search_images_fallback(query, count)
            await asyncio.sleep(1)  # 1초 대기 후 재시도

async def _search_images_single_attempt(query: str, count: int, unsplash_access_key: str) -> List[ImageInfo]:
    """단일 Unsplash API 호출 시도"""
    # 한국어 키워드를 영어로 간단 변환
    query_en = query
    korean_to_english = {
        "AI": "artificial intelligence",
        "인공지능": "artificial intelligence",
        "기술": "technology",
        "프로그래밍": "programming",
        "개발": "development",
        "소프트웨어": "software",
        "컴퓨터": "computer",
        "데이터": "data",
        "빅데이터": "big data",
        "머신러닝": "machine learning",
        "딥러닝": "deep learning",
        "웹": "web",
        "앱": "app",
        "모바일": "mobile",
        "클라우드": "cloud"
    }
    
    for ko, en in korean_to_english.items():
        if ko in query:
            query_en = query.replace(ko, en)
            break
    
    print(f"검색 쿼리 변환: '{query}' -> '{query_en}'")
    
    # 타임아웃 설정 - 연결 및 읽기 타임아웃 분리
    timeout = aiohttp.ClientTimeout(total=10, connect=3)
    connector = aiohttp.TCPConnector(
        ssl=False,  # SSL 검증 비활성화 (개발용)
        limit=10,
        force_close=True,
        enable_cleanup_closed=True
    )
    
    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        url = "https://api.unsplash.com/search/photos"
        # Client-ID 방식으로 변경 (공식 문서 권장)
        params = {
            "client_id": unsplash_access_key,
            "query": query_en,
            "per_page": count,
            "orientation": "landscape",
            "content_filter": "high",
            "order_by": "relevant"
        }
        
        print(f"Unsplash API 호출: query='{query_en}', count={count}")
        
        async with session.get(url, params=params) as response:
            # Rate limit 정보 확인
            remaining = response.headers.get('X-Ratelimit-Remaining', 'Unknown')
            limit = response.headers.get('X-Ratelimit-Limit', 'Unknown')
            print(f"Unsplash API Rate Limit: {remaining}/{limit}")
            
            if response.status == 200:
                data = await response.json()
                images = []
                
                for image in data.get("results", []):
                    images.append(ImageInfo(
                        id=image["id"],
                        url=image["urls"]["regular"],
                        thumb_url=image["urls"]["thumb"],
                        alt_text=image.get("alt_description", f"{query} 관련 이미지") or f"{query} 관련 이미지",
                        attribution={
                            "photographer": image["user"]["name"],
                            "source": "Unsplash",
                            "source_url": image["links"]["html"]
                        },
                        width=image["width"],
                        height=image["height"]
                    ))
                
                print(f"Unsplash API 성공: {len(images)}개 이미지 반환")
                return images if images else await search_images_fallback(query, count)
            elif response.status == 403:
                print("Unsplash API 권한 오류 - API 키 확인 필요")
                raise Exception("API 키 권한 오류")
            elif response.status == 429:
                print("Unsplash API Rate Limit 초과")
                raise Exception("Rate limit 초과")
            else:
                error_text = await response.text()
                print(f"Unsplash API 오류: {response.status} - {error_text}")
                raise Exception(f"HTTP {response.status}: {error_text}")

async def search_images_fallback(query: str, count: int = 3) -> List[ImageInfo]:
    """Unsplash API 실패 시 Lorem Picsum을 사용한 백업 이미지 검색"""
    images = []
    
    # 쿼리를 기반으로 일관된 이미지를 생성하기 위해 해시 사용
    query_hash = hash(query) % 1000
    
    for i in range(count):
        # 각 이미지마다 다른 시드 사용
        image_seed = (query_hash + i * 100) % 1000
        
        images.append(ImageInfo(
            id=f"picsum_{query_hash}_{i}",
            url=f"https://picsum.photos/800/600?random={image_seed}",
            thumb_url=f"https://picsum.photos/300/200?random={image_seed}",
            alt_text=f"{query} 관련 이미지 {i+1}",
            attribution={"photographer": "Lorem Picsum", "source": "https://picsum.photos"},
            width=800, height=600
        ))
    
    return images

@app.get("/test/claude")
async def test_claude_connection():
    """Claude API 연결 테스트"""
    
    if not claude_client:
        return {"status": "error", "message": "Claude API 키가 설정되지 않았거나 클라이언트 초기화에 실패했습니다"}
    
    try:
        response = claude_client.messages.create(
            model="claude-4-sonnet-20250514",
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
try:
    from app.core.supabase import get_supabase_client
    supabase = get_supabase_client()
    print("✅ Supabase 클라이언트 초기화 성공")
except Exception as e:
    print(f"❌ Supabase 클라이언트 초기화 실패: {e}")
    supabase = None

# 임시 발행 내역 저장소 (실제로는 데이터베이스 사용)
published_posts = []

@app.get("/dashboard/publishing-activity")
async def get_publishing_activity():
    """발행 활동 데이터 반환 (GitHub 잔디 스타일) - Supabase 데이터 사용"""
    try:
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        # 12개월 범위: 현재 날짜가 오른쪽 끝에 오도록
        today = datetime.now().date()
        
        # 12개월 전 계산 (대략 52주)
        start_date = today - timedelta(days=52 * 7)  # 52주 전
        end_date = today
        
        # 날짜별 발행 수 집계
        activity_by_date = defaultdict(int)
        posts_by_date = defaultdict(list)
        
        # Supabase에서 게시물 데이터 가져오기
        posts_data = []
        if supabase:
            try:
                # 날짜 범위 내의 게시물만 조회
                response = supabase.table("blog_posts").select("title, created_at, published_at").execute()
                posts_data = response.data if response.data else []
                print(f"📊 Supabase에서 {len(posts_data)}개 게시물 조회")
            except Exception as e:
                print(f"❌ Supabase 게시물 조회 오류: {e}")
                # Supabase 실패 시 메모리 데이터 사용
                posts_data = published_posts
        else:
            print("⚠️ Supabase 미연결 - 메모리 데이터 사용")
            posts_data = published_posts
        
        # 게시물 데이터에서 날짜별로 집계
        for post in posts_data:
            try:
                # published_at 또는 created_at 사용
                post_date_str = post.get('published_at') or post.get('created_at')
                if post_date_str:
                    if isinstance(post_date_str, str):
                        # ISO 형식 날짜 파싱
                        if 'T' in post_date_str:
                            post_date = datetime.fromisoformat(post_date_str.replace('Z', '+00:00')).date()
                        else:
                            post_date = datetime.fromisoformat(post_date_str).date()
                    else:
                        post_date = post_date_str.date() if hasattr(post_date_str, 'date') else today
                else:
                    post_date = today
                    
                # 날짜 범위 확인
                if start_date <= post_date <= end_date:
                    date_key = post_date.isoformat()
                    activity_by_date[date_key] += 1
                    posts_by_date[date_key].append(post.get('title', '제목 없음'))
                    
            except Exception as e:
                print(f"❌ 날짜 파싱 오류: {e}, post: {post}")
                continue
        
        # 모든 날짜에 대해 데이터 생성
        activities = []
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.isoformat()
            activities.append({
                "date": date_str,
                "count": activity_by_date.get(date_str, 0),
                "posts": posts_by_date.get(date_str, [])
            })
            current_date += timedelta(days=1)
        
        total_posts = len(posts_data)
        active_days = len([a for a in activities if a["count"] > 0])
        
        print(f"📈 발행 활동 통계: 총 {total_posts}개 포스트, {active_days}일 활성")
        
        return {
            "activities": activities,
            "total_posts": total_posts,
            "active_days": active_days,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        
    except Exception as e:
        print(f"❌ 발행 활동 조회 오류: {str(e)}")
        # 오류 시 빈 데이터 반환
        today = datetime.now().date()
        start_date = today - timedelta(days=52 * 7)
        end_date = today
        
        return {
            "activities": [],
            "total_posts": 0,
            "active_days": 0,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

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
        
        # Claude API가 없으면 더미 콘텐츠 생성
        if not claude_client:
            # 이미지 검색 먼저 실행
            title_images = await search_images(request.keywords[0], count=3)
            keyword_images = await search_images(" ".join(request.keywords), count=2)
            
            # 본문에 이미지를 배치한 콘텐츠 생성
            sections = []
            
            # 기본 섹션들
            sections.append(f"<h2>🤖 AI가 생성한 {request.keywords[0]} 완벽 가이드</h2>")
            sections.append(f"<p>안녕하세요! 오늘은 <strong>{request.keywords[0]}</strong>에 대해 {request.tone} 스타일로 자세히 알아보겠습니다. 이 글은 총 {request.target_length}자 분량으로 작성되어 초보자부터 전문가까지 모든 수준의 독자에게 유용한 정보를 제공합니다.</p>")
            
            # 첫 번째 이미지 배치
            if title_images:
                sections.append(f'<div style="text-align: center; margin: 20px 0;"><img src="{title_images[0].url}" alt="{title_images[0].alt_text}" style="max-width: 100%; height: auto; border-radius: 8px;" /></div>')
            
            sections.append(f"<h3>📚 {request.keywords[0]}란 무엇인가?</h3>")
            sections.append(f"<p>{request.keywords[0]}는 현재 가장 주목받고 있는 분야 중 하나입니다. 이 기술이 등장한 배경부터 현재의 발전 상황까지, 그리고 앞으로의 전망까지 종합적으로 살펴보겠습니다. 특히 {request.content_type} 형태로 정리하여 독자 여러분이 쉽게 이해할 수 있도록 구성했습니다.</p>")
            
            sections.append(f"<h3>🚀 {request.keywords[0]}의 핵심 개념</h3>")
            sections.append(f"<p>{request.keywords[0]}를 이해하기 위해서는 먼저 기본 개념을 명확히 해야 합니다. 이 분야의 전문가들이 공통적으로 강조하는 핵심 원리들을 정리해보겠습니다.</p>")
            sections.append("<ul>")
            sections.append(f"<li><strong>기본 원리:</strong> {request.keywords[0]}의 핵심이 되는 원리와 작동 메커니즘을 이해하는 것이 가장 중요합니다.</li>")
            sections.append(f"<li><strong>실용적 접근:</strong> 이론적 지식과 함께 실제 적용 사례를 통해 {request.keywords[0]}를 체험해보는 것이 필요합니다.</li>")
            sections.append(f"<li><strong>지속적 학습:</strong> {request.keywords[0]} 분야는 빠르게 발전하고 있어 지속적인 학습과 업데이트가 필수입니다.</li>")
            sections.append(f"<li><strong>커뮤니티 참여:</strong> 관련 커뮤니티에 참여하여 다른 전문가들과 지식을 공유하고 토론하는 것이 중요합니다.</li>")
            sections.append("</ul>")
            
            # 두 번째 이미지 배치
            if len(title_images) > 1:
                sections.append(f'<div style="text-align: center; margin: 20px 0;"><img src="{title_images[1].url}" alt="{title_images[1].alt_text}" style="max-width: 100%; height: auto; border-radius: 8px;" /></div>')
            
            sections.append(f"<h3>🔍 {request.keywords[0]}의 실무 활용법</h3>")
            sections.append(f"<p>이론을 넘어서 실제 업무나 프로젝트에서 {request.keywords[0]}를 어떻게 활용할 수 있는지 구체적인 방법들을 알아보겠습니다. 다양한 산업 분야에서의 적용 사례와 함께 실무에서 바로 사용할 수 있는 팁들을 제공합니다.</p>")
            
            sections.append("<ol>")
            sections.append(f"<li><strong>계획 수립:</strong> {request.keywords[0]}를 도입하기 전에 명확한 목표와 계획을 수립해야 합니다. 현재 상황을 분석하고 달성하고자 하는 목표를 구체적으로 정의하는 것이 성공의 첫걸음입니다.</li>")
            sections.append(f"<li><strong>단계별 적용:</strong> 한 번에 모든 것을 바꾸려 하지 말고 단계별로 점진적으로 {request.keywords[0]}를 적용해 나가는 것이 현명합니다. 작은 성공을 축적하면서 점차 확대해 나가세요.</li>")
            sections.append(f"<li><strong>성과 측정:</strong> {request.keywords[0]} 도입 후 정기적으로 성과를 측정하고 평가해야 합니다. 객관적인 지표를 통해 개선점을 찾고 지속적으로 최적화해 나가세요.</li>")
            sections.append("</ol>")
            
            sections.append(f"<h3>💡 {request.keywords[0]}의 최신 트렌드</h3>")
            sections.append(f"<p>{request.keywords[0]} 분야는 매우 빠르게 발전하고 있습니다. 최근의 주요 트렌드와 앞으로 주목해야 할 발전 방향들을 정리해보겠습니다. 이러한 트렌드를 미리 파악하고 준비한다면 경쟁 우위를 확보할 수 있을 것입니다.</p>")
            
            # 세 번째 이미지 배치
            if keyword_images:
                sections.append(f'<div style="text-align: center; margin: 20px 0;"><img src="{keyword_images[0].url}" alt="{keyword_images[0].alt_text}" style="max-width: 100%; height: auto; border-radius: 8px;" /></div>')
            
            sections.append(f"<h4>🔥 주요 트렌드</h4>")
            sections.append(f"<p>현재 {request.keywords[0]} 분야에서 가장 주목받고 있는 트렌드들을 살펴보면, 자동화와 지능화가 핵심 키워드로 떠오르고 있습니다. 또한 사용자 경험 개선과 접근성 향상도 중요한 관심사가 되고 있습니다.</p>")
            
            sections.append(f"<h3>🛠️ {request.keywords[0]} 구현 가이드</h3>")
            sections.append(f"<p>실제로 {request.keywords[0]}를 구현하고 적용하는 과정에서 알아두면 유용한 팁들과 주의사항들을 정리했습니다. 초보자도 따라할 수 있도록 단계별로 상세히 설명하겠습니다.</p>")
            
            sections.append(f"<blockquote><p><strong>전문가 팁:</strong> {request.keywords[0]}를 처음 시작하는 분들은 너무 복잡한 것부터 시도하지 마세요. 기본기를 탄탄히 다진 후에 고급 기능들을 하나씩 추가해 나가는 것이 성공의 비결입니다.</p></blockquote>")
            
            sections.append(f"<h3>📊 {request.keywords[0]}의 성과 측정</h3>")
            sections.append(f"<p>{request.keywords[0]}를 도입한 후에는 반드시 그 효과를 측정하고 평가해야 합니다. 정량적 지표와 정성적 평가를 모두 활용하여 종합적으로 판단하는 것이 중요합니다.</p>")
            
            # 네 번째 이미지 배치
            if len(title_images) > 2:
                sections.append(f'<div style="text-align: center; margin: 20px 0;"><img src="{title_images[2].url}" alt="{title_images[2].alt_text}" style="max-width: 100%; height: auto; border-radius: 8px;" /></div>')
            
            sections.append(f"<h3>🔧 {request.keywords[0]} 도구 및 리소스</h3>")
            sections.append(f"<p>{request.keywords[0]}를 효과적으로 활용하기 위해서는 적절한 도구와 리소스를 활용하는 것이 중요합니다. 현재 시장에서 사용할 수 있는 다양한 도구들을 소개하고, 각각의 특징과 장단점을 비교해보겠습니다.</p>")
            
            sections.append(f"<h4>📱 필수 도구들</h4>")
            sections.append("<ul>")
            sections.append(f"<li><strong>기본 도구:</strong> {request.keywords[0]}를 시작하는 데 반드시 필요한 기본적인 도구들입니다. 대부분 무료로 사용할 수 있어 초보자에게 적합합니다.</li>")
            sections.append(f"<li><strong>고급 도구:</strong> 더 전문적인 작업을 위한 고급 도구들로, 유료 버전도 있지만 그만큼 강력한 기능을 제공합니다.</li>")
            sections.append(f"<li><strong>통합 솔루션:</strong> {request.keywords[0]}의 전 과정을 관리할 수 있는 통합 플랫폼들입니다. 팀 작업에 특히 유용합니다.</li>")
            sections.append("</ul>")
            
            sections.append(f"<h3>📚 {request.keywords[0]} 학습 자료</h3>")
            sections.append(f"<p>{request.keywords[0]}를 깊이 있게 학습하고 싶은 분들을 위해 추천 학습 자료들을 정리했습니다. 온라인 강의부터 전문 서적까지 다양한 형태의 자료들을 수준별로 분류하여 소개합니다.</p>")
            
            sections.append(f"<h3>🎯 결론 및 향후 전망</h3>")
            sections.append(f"<p>{request.keywords[0]}는 앞으로도 계속 발전할 분야입니다. 이 글에서 다룬 내용들을 바탕으로 여러분만의 {request.keywords[0]} 활용 방안을 수립해보시기 바랍니다. 지속적인 학습과 실습을 통해 이 분야의 전문가로 성장하실 수 있을 것입니다.</p>")
            
            sections.append(f"<p>특히 {request.tone} 관점에서 접근할 때, {request.keywords[0]}의 진정한 가치를 발견할 수 있습니다. 이론과 실무를 균형 있게 조합하여 실질적인 성과를 달성하시기 바랍니다.</p>")
            
            sections.append(f"<p>마지막으로, {request.keywords[0]}에 관심을 가지고 이 글을 끝까지 읽어주신 여러분께 감사드립니다. 앞으로도 더 유용한 정보로 찾아뵙겠습니다. 궁금한 점이 있으시면 언제든 댓글로 문의해주세요!</p>")
            
            dummy_content = "\n".join(sections)
            
            # 실제 글자 수 계산 (HTML 태그 제외)
            import re
            clean_text = re.sub(r'<[^>]+>', '', dummy_content)
            actual_word_count = len(clean_text.replace(' ', '').replace('\n', ''))
            
            # 대표 이미지 설정 (첫 번째 title_image 사용)
            if title_images:
                featured_image = title_images[0]
            else:
                # 백업용 Lorem Picsum 이미지
                featured_image = ImageInfo(
                    id="picsum_fallback",
                    url="https://picsum.photos/800/600?random=1",
                    thumb_url="https://picsum.photos/300/200?random=1",
                    alt_text=f"{request.keywords[0]} 관련 이미지",
                    attribution={"photographer": "Lorem Picsum", "source": "https://picsum.photos"},
                    width=800, height=600
                )
            
            content_response = ContentResponse(
                title=f"{request.keywords[0]} 완벽 가이드 - 전문가가 알려주는 핵심 포인트",
                content=dummy_content.strip(),
                meta_description=f"{request.keywords[0]}에 대한 전문적이고 상세한 가이드입니다. 기초부터 고급까지 모든 내용을 다룹니다.",
                word_count=actual_word_count,
                ai_model_used="unsplash-integrated",
                featured_image=featured_image,
                suggested_images={
                    "title_based": [],
                    "keyword_based": []
                }
            )
        else:
            content_response = await test_generate_content(content_request)
        
        # 2. 블로그 발행 시뮬레이션
        published_url = f"{request.blog_platform.url}/posts/{len(published_posts) + 1}"
        
        # 발행 내역 저장
        from datetime import datetime
        published_post = {
            "id": len(published_posts) + 1,
            "title": content_response.title,
            "content": content_response.content,
            "platform": request.blog_platform.model_dump(),
            "published_url": published_url,
            "published_at": datetime.now().isoformat() + "Z",
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
        
        # Supabase에서 최근 게시물 조회 (플랫폼 정보와 함께)
        try:
            posts_response = supabase.table("blog_posts").select("*, blog_platforms(*)").order("created_at", desc=True).limit(5).execute()
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