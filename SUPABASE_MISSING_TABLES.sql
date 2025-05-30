-- Supabase에 생성되지 않은 테이블들
-- 2025-05-30 확인 결과: blog_platforms 테이블만 존재
-- 아래 SQL을 Supabase SQL Editor에서 실행하세요

-- ================================================================
-- 1. users 테이블 (인증 사용자)
-- ================================================================
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

-- ================================================================
-- 2. blog_accounts 테이블 (사용자의 블로그 계정)
-- ================================================================
CREATE TABLE IF NOT EXISTS blog_accounts (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    platform_id UUID REFERENCES blog_platforms(id) ON DELETE CASCADE,
    blog_name VARCHAR(255) NOT NULL,
    blog_url VARCHAR(500) NOT NULL,
    username VARCHAR(255),
    encrypted_credentials TEXT, -- 암호화된 API 키, 비밀번호 등
    is_active BOOLEAN DEFAULT true,
    last_sync_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, blog_url)
);

-- ================================================================
-- 3. contents 테이블 (생성된 콘텐츠)
-- ================================================================
CREATE TABLE IF NOT EXISTS contents (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) NOT NULL,
    content TEXT NOT NULL,
    meta_description VARCHAR(500),
    keywords TEXT[],
    status VARCHAR(50) DEFAULT 'draft', -- draft, published, archived
    ai_model VARCHAR(100),
    generation_params JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ================================================================
-- 4. publications 테이블 (발행 정보)
-- ================================================================
CREATE TABLE IF NOT EXISTS publications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content_id UUID REFERENCES contents(id) ON DELETE CASCADE,
    blog_account_id UUID REFERENCES blog_accounts(id) ON DELETE CASCADE,
    published_url VARCHAR(1000),
    platform_post_id VARCHAR(255),
    status VARCHAR(50) DEFAULT 'pending', -- pending, published, failed
    error_message TEXT,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(content_id, blog_account_id)
);

-- ================================================================
-- 5. analytics 테이블 (분석 데이터)
-- ================================================================
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

-- ================================================================
-- 6. images 테이블 (이미지 정보)
-- ================================================================
CREATE TABLE IF NOT EXISTS images (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    content_id UUID REFERENCES contents(id) ON DELETE CASCADE,
    url VARCHAR(1000) NOT NULL,
    thumbnail_url VARCHAR(1000),
    alt_text VARCHAR(500),
    source VARCHAR(100), -- unsplash, pexels, etc.
    photographer VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ================================================================
-- 업데이트 트리거 함수 (이미 존재할 수 있음)
-- ================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- ================================================================
-- 업데이트 트리거 생성
-- ================================================================
CREATE TRIGGER update_users_updated_at BEFORE UPDATE
    ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blog_accounts_updated_at BEFORE UPDATE
    ON blog_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contents_updated_at BEFORE UPDATE
    ON contents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_publications_updated_at BEFORE UPDATE
    ON publications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- 인덱스 생성 (성능 최적화)
-- ================================================================
CREATE INDEX idx_blog_accounts_user_id ON blog_accounts(user_id);
CREATE INDEX idx_contents_user_id ON contents(user_id);
CREATE INDEX idx_contents_status ON contents(status);
CREATE INDEX idx_publications_content_id ON publications(content_id);
CREATE INDEX idx_publications_blog_account_id ON publications(blog_account_id);
CREATE INDEX idx_publications_status ON publications(status);
CREATE INDEX idx_analytics_publication_id ON analytics(publication_id);
CREATE INDEX idx_analytics_date ON analytics(date DESC);
CREATE INDEX idx_images_content_id ON images(content_id);

-- ================================================================
-- Row Level Security 활성화 (선택사항)
-- ================================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE contents ENABLE ROW LEVEL SECURITY;
ALTER TABLE publications ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;

-- ================================================================
-- 테스트: 테이블 생성 확인
-- ================================================================
-- 실행 후 다음 쿼리로 테이블 생성을 확인할 수 있습니다:
/*
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name IN ('users', 'blog_accounts', 'contents', 'publications', 'analytics', 'images')
ORDER BY table_name;
*/

-- ================================================================
-- 샘플 데이터 (선택사항)
-- ================================================================
-- 테스트 사용자 생성 (비밀번호: testpass123)
/*
INSERT INTO users (email, hashed_password, full_name, is_active)
VALUES ('test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiLXCfNJ', 'Test User', true)
ON CONFLICT (email) DO NOTHING;
*/