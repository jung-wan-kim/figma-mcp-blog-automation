#!/usr/bin/env python3
"""
Supabase 샘플 데이터 추가
"""

from supabase import create_client, Client
import json
from datetime import datetime

# Supabase 설정
SUPABASE_URL = "https://eupjjwgxrzxmddnumxyd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1cGpqd2d4cnp4bWRkbnVteHlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg1ODA2ODksImV4cCI6MjA2NDE1NjY4OX0.Z9-K6ktYOCGnAmV6cYWaYSu6HHwIuiWE0rV7ovDvVw8"

# Supabase 클라이언트 생성
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def add_sample_platforms():
    """샘플 블로그 플랫폼 추가"""
    sample_platforms = [
        {
            "name": "AI 기술 블로그",
            "platform_type": "tistory",
            "url": "https://ai-tech.tistory.com",
            "username": "aitech",
            "post_count": 5,
            "total_views": 1250,
            "total_likes": 89
        },
        {
            "name": "디지털 마케팅 워드프레스",
            "platform_type": "wordpress",
            "url": "https://digital-marketing.wordpress.com",
            "username": "marketingpro",
            "post_count": 3,
            "total_views": 750,
            "total_likes": 45
        },
        {
            "name": "일상 이야기 네이버",
            "platform_type": "naver",
            "url": "https://blog.naver.com/dailystory",
            "username": "dailystory",
            "post_count": 8,
            "total_views": 2100,
            "total_likes": 156
        }
    ]
    
    added_platforms = []
    
    for platform in sample_platforms:
        try:
            # 중복 확인
            existing = supabase.table("blog_platforms").select("*").eq("url", platform["url"]).execute()
            
            if not existing.data:
                response = supabase.table("blog_platforms").insert(platform).execute()
                if response.data:
                    print(f"✅ 플랫폼 추가: {platform['name']}")
                    added_platforms.append(response.data[0])
            else:
                print(f"ℹ️  이미 존재하는 플랫폼: {platform['name']}")
                added_platforms.append(existing.data[0])
                
        except Exception as e:
            print(f"❌ 플랫폼 추가 실패 ({platform['name']}): {e}")
    
    return added_platforms

def add_sample_posts(platforms):
    """샘플 블로그 포스트 추가"""
    if not platforms:
        print("⚠️  플랫폼이 없어 포스트를 추가할 수 없습니다.")
        return
    
    sample_posts = [
        {
            "platform_name": "AI 기술 블로그",
            "title": "ChatGPT와 Claude: AI 어시스턴트 비교 분석",
            "content": """<h2>서론</h2>
<p>최근 AI 어시스턴트의 발전이 놀랍습니다. 특히 ChatGPT와 Claude는 각각의 장점을 가지고 있어 사용자들에게 다양한 선택지를 제공합니다.</p>

<h2>ChatGPT의 특징</h2>
<ul>
<li>광범위한 지식 베이스</li>
<li>다양한 플러그인 지원</li>
<li>코드 작성 능력</li>
</ul>

<h2>Claude의 특징</h2>
<ul>
<li>긴 문맥 처리 능력</li>
<li>윤리적 고려사항 강조</li>
<li>자연스러운 대화 스타일</li>
</ul>

<h2>결론</h2>
<p>두 AI 모두 각자의 강점이 있으므로, 용도에 맞게 선택하여 사용하는 것이 중요합니다.</p>""",
            "meta_description": "ChatGPT와 Claude AI 어시스턴트의 주요 특징과 차이점을 비교 분석합니다.",
            "status": "published",
            "published_url": "https://ai-tech.tistory.com/123",
            "views": 450,
            "likes": 32,
            "comments": 8,
            "tags": ["AI", "ChatGPT", "Claude", "인공지능", "비교분석"]
        },
        {
            "platform_name": "디지털 마케팅 워드프레스",
            "title": "2025년 디지털 마케팅 트렌드 TOP 5",
            "content": """<h2>들어가며</h2>
<p>2025년 디지털 마케팅은 AI와 개인화가 핵심 키워드입니다. 이번 포스트에서는 주목해야 할 5가지 트렌드를 소개합니다.</p>

<h2>1. AI 기반 콘텐츠 생성</h2>
<p>AI를 활용한 콘텐츠 생성이 보편화되고 있습니다.</p>

<h2>2. 초개인화 마케팅</h2>
<p>고객 데이터를 기반으로 한 맞춤형 경험 제공이 중요해집니다.</p>

<h2>3. 음성 검색 최적화</h2>
<p>스마트 스피커 사용 증가로 음성 검색 최적화가 필수입니다.</p>

<h2>4. 인플루언서 마케팅 진화</h2>
<p>마이크로 인플루언서와의 협업이 늘어나고 있습니다.</p>

<h2>5. 지속가능성 마케팅</h2>
<p>환경과 사회적 가치를 강조하는 브랜드가 선호됩니다.</p>""",
            "meta_description": "2025년 주목해야 할 디지털 마케팅 트렌드 5가지를 소개합니다.",
            "status": "published",
            "published_url": "https://digital-marketing.wordpress.com/2025-trends",
            "views": 280,
            "likes": 19,
            "comments": 5,
            "tags": ["디지털마케팅", "트렌드", "2025", "AI", "개인화"]
        },
        {
            "platform_name": "일상 이야기 네이버",
            "title": "봄맞이 홈카페 인테리어 꿀팁",
            "content": """<p>안녕하세요! 오늘은 집에서도 카페 분위기를 낼 수 있는 인테리어 팁을 공유하려고 해요.</p>

<h3>1. 조명이 분위기의 80%</h3>
<p>따뜻한 색온도의 간접조명을 활용하면 카페 같은 아늑한 분위기를 만들 수 있어요.</p>

<h3>2. 그린 인테리어</h3>
<p>작은 화분들을 곳곳에 배치하면 생기있는 공간이 됩니다.</p>

<h3>3. 커피 코너 만들기</h3>
<p>커피머신과 컵을 보기 좋게 진열하면 진짜 카페 같아요!</p>

<h3>4. 아늑한 좌석 공간</h3>
<p>푹신한 쿠션과 담요로 편안한 공간을 만들어보세요.</p>

<p>여러분도 집에서 나만의 카페를 만들어보는 건 어떨까요? 😊</p>""",
            "meta_description": "집에서도 카페 분위기를 낼 수 있는 홈카페 인테리어 팁을 소개합니다.",
            "status": "published",
            "published_url": "https://blog.naver.com/dailystory/12345",
            "views": 520,
            "likes": 45,
            "comments": 12,
            "tags": ["홈카페", "인테리어", "일상", "꿀팁", "봄"]
        }
    ]
    
    # 플랫폼 이름으로 매핑
    platform_map = {p['name']: p['id'] for p in platforms}
    
    for post in sample_posts:
        try:
            platform_id = platform_map.get(post['platform_name'])
            if not platform_id:
                print(f"⚠️  플랫폼을 찾을 수 없음: {post['platform_name']}")
                continue
            
            # platform_name 제거하고 platform_id 추가
            post_data = {k: v for k, v in post.items() if k != 'platform_name'}
            post_data['platform_id'] = platform_id
            post_data['published_at'] = datetime.now().isoformat()
            
            # 포스트 추가
            response = supabase.table("blog_posts").insert(post_data).execute()
            
            if response.data:
                print(f"✅ 포스트 추가: {post['title']}")
            
        except Exception as e:
            print(f"❌ 포스트 추가 실패 ({post['title']}): {e}")

def check_data():
    """추가된 데이터 확인"""
    print("\n" + "="*60)
    print("📊 데이터 확인")
    print("="*60)
    
    # 플랫폼 확인
    platforms = supabase.table("blog_platforms").select("*").execute()
    print(f"\n✅ 블로그 플랫폼: {len(platforms.data)}개")
    for p in platforms.data:
        print(f"   - {p['name']} ({p['platform_type']}) - {p['post_count']}개 포스트")
    
    # 포스트 확인
    posts = supabase.table("blog_posts").select("*, blog_platforms(name)").execute()
    print(f"\n✅ 블로그 포스트: {len(posts.data)}개")
    for p in posts.data:
        platform_name = p.get('blog_platforms', {}).get('name', 'Unknown')
        print(f"   - [{platform_name}] {p['title']} - {p['views']} views, {p['likes']} likes")

if __name__ == "__main__":
    print("🚀 Supabase 샘플 데이터 추가")
    print("="*60)
    
    # 1. 샘플 플랫폼 추가
    print("\n1️⃣ 샘플 플랫폼 추가 중...")
    platforms = add_sample_platforms()
    
    # 2. 샘플 포스트 추가
    print("\n2️⃣ 샘플 포스트 추가 중...")
    add_sample_posts(platforms)
    
    # 3. 데이터 확인
    check_data()
    
    print("\n✅ 샘플 데이터 추가 완료!")
    print("🎉 이제 http://localhost:3001 에서 확인할 수 있습니다.")