#!/usr/bin/env python3
"""
Supabase 테이블 생성 - Management API 사용
"""

import httpx
import asyncio
from typing import Dict, Any
import json

# Supabase 설정
SUPABASE_URL = "https://eupjjwgxrzxmddnumxyd.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1cGpqd2d4cnp4bWRkbnVteHlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg1ODA2ODksImV4cCI6MjA2NDE1NjY4OX0.Z9-K6ktYOCGnAmV6cYWaYSu6HHwIuiWE0rV7ovDvVw8"

# SQL 쿼리들을 개별적으로 정의
CREATE_TABLES_SQL = [
    # 1. blog_platforms 테이블
    """
    CREATE TABLE IF NOT EXISTS blog_platforms (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        platform_type VARCHAR(50) NOT NULL,
        url VARCHAR(500) NOT NULL,
        username VARCHAR(255),
        post_count INTEGER DEFAULT 0,
        total_views INTEGER DEFAULT 0,
        total_likes INTEGER DEFAULT 0,
        api_key VARCHAR(500),
        api_secret VARCHAR(500),
        access_token TEXT,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(url)
    );
    """,
    
    # 2. blog_posts 테이블
    """
    CREATE TABLE IF NOT EXISTS blog_posts (
        id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
        platform_id UUID REFERENCES blog_platforms(id) ON DELETE CASCADE,
        title VARCHAR(500) NOT NULL,
        content TEXT NOT NULL,
        meta_description VARCHAR(500),
        published_url VARCHAR(1000),
        status VARCHAR(50) DEFAULT 'draft',
        views INTEGER DEFAULT 0,
        likes INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        tags TEXT[],
        featured_image_url VARCHAR(1000),
        scheduled_at TIMESTAMP WITH TIME ZONE,
        published_at TIMESTAMP WITH TIME ZONE,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
    );
    """,
    
    # 3. 업데이트 트리거 함수
    """
    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    """,
    
    # 4. 트리거 생성
    """
    CREATE TRIGGER update_blog_platforms_updated_at BEFORE UPDATE
        ON blog_platforms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """,
    
    """
    CREATE TRIGGER update_blog_posts_updated_at BEFORE UPDATE
        ON blog_posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """,
    
    # 5. 인덱스 생성
    """
    CREATE INDEX IF NOT EXISTS idx_blog_posts_platform_id ON blog_posts(platform_id);
    """,
    
    """
    CREATE INDEX IF NOT EXISTS idx_blog_posts_status ON blog_posts(status);
    """,
    
    """
    CREATE INDEX IF NOT EXISTS idx_blog_posts_published_at ON blog_posts(published_at DESC);
    """
]

async def execute_sql_via_rpc(sql: str) -> Dict[str, Any]:
    """Supabase RPC를 통해 SQL 실행"""
    async with httpx.AsyncClient() as client:
        try:
            # Supabase의 REST API 엔드포인트 사용
            response = await client.post(
                f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
                headers={
                    "apikey": SUPABASE_ANON_KEY,
                    "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
                    "Content-Type": "application/json"
                },
                json={"query": sql}
            )
            
            if response.status_code == 404:
                # RPC 함수가 없는 경우 - 직접 생성 안내
                return {"error": "RPC function not found", "manual": True}
            
            return response.json() if response.status_code == 200 else {"error": response.text}
            
        except Exception as e:
            return {"error": str(e)}

async def create_tables():
    """테이블 생성 실행"""
    print("🚀 Supabase 테이블 생성 시작...")
    print("="*60)
    
    # RPC 방식 시도
    test_result = await execute_sql_via_rpc("SELECT 1")
    
    if test_result.get("manual"):
        print("⚠️  Supabase에서 직접 SQL을 실행해야 합니다.")
        print("\n다음 단계를 따라주세요:")
        print("\n1. Supabase 대시보드 열기:")
        print(f"   https://supabase.com/dashboard/project/eupjjwgxrzxmddnumxyd/sql/new")
        
        print("\n2. 아래 SQL을 순서대로 실행:")
        
        for i, sql in enumerate(CREATE_TABLES_SQL, 1):
            print(f"\n--- SQL {i} ---")
            print(sql.strip())
            print("-" * 40)
        
        print("\n3. 각 SQL을 복사하여 SQL Editor에 붙여넣고 'Run' 클릭")
        
        # 대체 방법: 전체 SQL 파일 생성
        combined_sql = "\n\n".join(CREATE_TABLES_SQL)
        with open("create_all_tables.sql", "w", encoding="utf-8") as f:
            f.write(combined_sql)
        
        print("\n💡 또는 생성된 'create_all_tables.sql' 파일의 내용을 한 번에 실행할 수 있습니다.")
        
    else:
        # RPC로 실행 (가능한 경우)
        for i, sql in enumerate(CREATE_TABLES_SQL, 1):
            print(f"\n실행 중... ({i}/{len(CREATE_TABLES_SQL)})")
            result = await execute_sql_via_rpc(sql)
            
            if "error" in result:
                print(f"❌ 오류: {result['error']}")
            else:
                print(f"✅ 성공")

def create_manual_guide():
    """수동 설정 가이드 생성"""
    guide = """# Supabase 테이블 수동 생성 가이드

## 1. Supabase SQL Editor 열기
링크: https://supabase.com/dashboard/project/eupjjwgxrzxmddnumxyd/sql/new

## 2. 다음 SQL을 실행

### 테이블 생성
```sql
"""
    
    for sql in CREATE_TABLES_SQL:
        guide += sql.strip() + "\n\n"
    
    guide += """```

## 3. 샘플 데이터 추가 (선택사항)

```sql
-- 샘플 플랫폼
INSERT INTO blog_platforms (name, platform_type, url, username)
VALUES ('테스트 블로그', 'tistory', 'https://test.tistory.com', 'testuser');

-- 샘플 게시물 (위에서 생성한 플랫폼 ID 사용)
INSERT INTO blog_posts (platform_id, title, content, status, published_url)
SELECT id, 'AI 테스트 포스트', '테스트 내용입니다.', 'published', 'https://test.tistory.com/1'
FROM blog_platforms WHERE platform_type = 'tistory' LIMIT 1;
```
"""
    
    with open("SUPABASE_MANUAL_SETUP.md", "w", encoding="utf-8") as f:
        f.write(guide)
    
    print("\n📄 'SUPABASE_MANUAL_SETUP.md' 파일이 생성되었습니다.")

if __name__ == "__main__":
    # 수동 가이드 생성
    create_manual_guide()
    
    # 테이블 생성 시도
    asyncio.run(create_tables())
    
    print("\n✅ 완료!")
    print("\n다음 단계:")
    print("1. Supabase 대시보드에서 테이블이 생성되었는지 확인")
    print("2. 프론트엔드/백엔드 서버 재시작")
    print("3. http://localhost:3001 접속하여 테스트")