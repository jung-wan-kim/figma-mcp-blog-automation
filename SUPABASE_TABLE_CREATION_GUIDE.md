# Supabase 테이블 생성 가이드

## 생성되지 않은 테이블 목록
- ❌ users
- ❌ blog_accounts
- ❌ contents
- ❌ publications
- ❌ analytics
- ❌ images

## 빠른 실행 가이드

### 1단계: Supabase SQL Editor 열기
[SQL Editor 링크](https://supabase.com/dashboard/project/eupjjwgxrzxmddnumxyd/sql/new)

### 2단계: 테이블 생성 순서
**중요**: 외래 키 제약 조건 때문에 순서대로 실행해야 합니다!

1. **users 테이블 먼저 생성**
```sql
CREATE TABLE IF NOT EXISTS users (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

2. **blog_accounts 테이블 생성**
```sql
CREATE TABLE IF NOT EXISTS blog_accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform_id UUID REFERENCES blog_platforms(id) ON DELETE CASCADE,
    blog_name VARCHAR(255) NOT NULL,
    blog_url VARCHAR(500) NOT NULL,
    username VARCHAR(255),
    encrypted_credentials TEXT,
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, blog_url)
);
```

3. **contents 테이블 생성**
```sql
CREATE TABLE IF NOT EXISTS contents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    meta_description VARCHAR(500),
    keywords TEXT[],
    status VARCHAR(50) DEFAULT 'draft',
    ai_model VARCHAR(100),
    generation_params JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

4. **publications 테이블 생성**
```sql
CREATE TABLE IF NOT EXISTS publications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content_id UUID REFERENCES contents(id) ON DELETE CASCADE,
    blog_account_id UUID REFERENCES blog_accounts(id) ON DELETE CASCADE,
    published_url VARCHAR(1000),
    platform_post_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(content_id, blog_account_id)
);
```

5. **analytics 테이블 생성**
```sql
CREATE TABLE IF NOT EXISTS analytics (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    publication_id UUID REFERENCES publications(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(publication_id, date)
);
```

6. **images 테이블 생성**
```sql
CREATE TABLE IF NOT EXISTS images (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content_id UUID REFERENCES contents(id) ON DELETE CASCADE,
    url VARCHAR(1000) NOT NULL,
    thumbnail_url VARCHAR(1000),
    alt_text VARCHAR(500),
    source VARCHAR(100),
    photographer VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3단계: 트리거 함수 및 트리거 생성
```sql
-- 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 트리거들
CREATE TRIGGER update_users_updated_at BEFORE UPDATE
    ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blog_accounts_updated_at BEFORE UPDATE
    ON blog_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contents_updated_at BEFORE UPDATE
    ON contents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_publications_updated_at BEFORE UPDATE
    ON publications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 4단계: 인덱스 생성 (성능 최적화)
```sql
CREATE INDEX idx_blog_accounts_user_id ON blog_accounts(user_id);
CREATE INDEX idx_contents_user_id ON contents(user_id);
CREATE INDEX idx_contents_status ON contents(status);
CREATE INDEX idx_publications_content_id ON publications(content_id);
CREATE INDEX idx_publications_blog_account_id ON publications(blog_account_id);
CREATE INDEX idx_publications_status ON publications(status);
CREATE INDEX idx_analytics_publication_id ON analytics(publication_id);
CREATE INDEX idx_analytics_date ON analytics(date DESC);
CREATE INDEX idx_images_content_id ON images(content_id);
```

### 5단계: 테이블 생성 확인
```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'blog_accounts', 'contents', 'publications', 'analytics', 'images')
ORDER BY table_name;
```

예상 결과:
```
blog_accounts
contents
images
publications
users
analytics
```

## 대체 방법: 한 번에 모두 실행
`SUPABASE_MISSING_TABLES.sql` 파일의 전체 내용을 복사하여 SQL Editor에 붙여넣고 실행

## 문제 해결
- **외래 키 오류**: 테이블 생성 순서를 확인하세요
- **이미 존재하는 테이블**: `IF NOT EXISTS`가 있어서 안전합니다
- **권한 오류**: Supabase 대시보드에 로그인했는지 확인하세요