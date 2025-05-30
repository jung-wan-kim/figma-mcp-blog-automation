# 블로그 자동화 시스템 데이터베이스 설정 가이드

## 📋 목차

1. [Supabase 프로젝트 설정](#1-supabase-프로젝트-설정)
2. [데이터베이스 테이블 생성](#2-데이터베이스-테이블-생성)
3. [환경 변수 설정](#3-환경-변수-설정)
4. [테스트 및 확인](#4-테스트-및-확인)

## 1. Supabase 프로젝트 설정

### 1.1 Supabase 계정 생성

1. [Supabase](https://supabase.com)에 접속
2. GitHub 계정으로 로그인
3. 새 프로젝트 생성

### 1.2 프로젝트 정보

- **프로젝트 이름**: blog-automation
- **데이터베이스 비밀번호**: 안전한 비밀번호 설정
- **리전**: 가까운 지역 선택 (예: Northeast Asia)

## 2. 데이터베이스 테이블 생성

### 2.1 SQL Editor 접속

1. Supabase 대시보드에서 "SQL Editor" 클릭
2. "New query" 버튼 클릭

### 2.2 테이블 생성 SQL 실행

아래 경로의 SQL 파일 내용을 복사하여 실행:

```
backend/database/schema.sql
```

또는 아래 SQL을 직접 실행:

```sql
-- 블로그 플랫폼 테이블
CREATE TABLE IF NOT EXISTS blog_platforms (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platform_type VARCHAR(50) NOT NULL,
    url VARCHAR(500) NOT NULL,
    username VARCHAR(255),
    post_count INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(url)
);

-- 블로그 게시물 테이블
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
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거 생성
CREATE TRIGGER update_blog_platforms_updated_at BEFORE UPDATE
    ON blog_platforms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blog_posts_updated_at BEFORE UPDATE
    ON blog_posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 인덱스 생성
CREATE INDEX idx_blog_posts_platform_id ON blog_posts(platform_id);
CREATE INDEX idx_blog_posts_status ON blog_posts(status);
CREATE INDEX idx_blog_posts_published_at ON blog_posts(published_at DESC);
```

### 2.3 테이블 권한 설정 (선택사항)

RLS (Row Level Security)를 사용하려면:

```sql
-- RLS 활성화
ALTER TABLE blog_platforms ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;

-- 읽기 권한 (모든 사용자)
CREATE POLICY "Public read access" ON blog_platforms
    FOR SELECT USING (true);

CREATE POLICY "Public read access" ON blog_posts
    FOR SELECT USING (true);

-- 쓰기 권한 (인증된 사용자만)
CREATE POLICY "Authenticated write access" ON blog_platforms
    FOR ALL USING (auth.role() = 'authenticated');

CREATE POLICY "Authenticated write access" ON blog_posts
    FOR ALL USING (auth.role() = 'authenticated');
```

## 3. 환경 변수 설정

### 3.1 Supabase 정보 확인

1. Supabase 대시보드 > Settings > API
2. 다음 정보 확인:
   - **Project URL**: `https://eupjjwgxrzxmddnumxyd.supabase.co`
   - **anon/public key**: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

### 3.2 프론트엔드 환경 변수

`blog-automation/frontend/.env.local` 파일:

```
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://eupjjwgxrzxmddnumxyd.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 3.3 백엔드 환경 변수

`blog-automation/backend/.env` 파일:

```
SUPABASE_URL=https://eupjjwgxrzxmddnumxyd.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
CLAUDE_API_KEY=your_claude_api_key_here
```

## 4. 테스트 및 확인

### 4.1 데이터베이스 연결 테스트

1. 백엔드 서버 실행:

   ```bash
   cd blog-automation/backend
   source venv/bin/activate
   python test_server.py
   ```

2. 프론트엔드 서버 실행:

   ```bash
   cd blog-automation/frontend
   npm run dev
   ```

3. 브라우저에서 확인:
   - 대시보드: http://localhost:3001
   - 플랫폼 관리: http://localhost:3001/platforms
   - 발행 내역: http://localhost:3001/posts

### 4.2 테이블 확인

Supabase 대시보드 > Table Editor에서:

- `blog_platforms` 테이블 확인
- `blog_posts` 테이블 확인

### 4.3 샘플 데이터 추가 (선택사항)

```sql
-- 샘플 플랫폼 추가
INSERT INTO blog_platforms (name, platform_type, url, username)
VALUES
  ('내 티스토리 블로그', 'tistory', 'https://myblog.tistory.com', 'myusername'),
  ('워드프레스 블로그', 'wordpress', 'https://myblog.wordpress.com', 'admin');

-- 샘플 게시물 추가
INSERT INTO blog_posts (
  platform_id,
  title,
  content,
  status,
  published_url,
  published_at
)
SELECT
  id,
  'AI가 작성한 첫 번째 블로그 포스트',
  '이것은 AI가 자동으로 생성한 블로그 포스트입니다.',
  'published',
  'https://myblog.tistory.com/1',
  NOW()
FROM blog_platforms
WHERE platform_type = 'tistory'
LIMIT 1;
```

## 🔧 문제 해결

### CORS 오류

- 백엔드 서버가 실행 중인지 확인
- `test_server.py`의 CORS 설정 확인

### 테이블이 없다는 오류

- SQL Editor에서 테이블 생성 SQL 재실행
- 올바른 프로젝트/데이터베이스에 연결되었는지 확인

### 연결 실패

- Supabase URL과 API 키가 올바른지 확인
- 네트워크 연결 상태 확인

## 📝 다음 단계

1. 실제 블로그 플랫폼 API 키 설정
2. Claude API 키 설정
3. 콘텐츠 자동 생성 및 발행 테스트
