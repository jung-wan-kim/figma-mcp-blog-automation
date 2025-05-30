-- 블로그 자동화 시스템 데이터베이스 스키마
-- Supabase SQL Editor에서 실행할 전체 스키마

-- 기존 테이블 삭제 (주의: 데이터가 모두 삭제됩니다!)
-- DROP TABLE IF EXISTS publication_history CASCADE;
-- DROP TABLE IF EXISTS analytics_data CASCADE;
-- DROP TABLE IF EXISTS images CASCADE;
-- DROP TABLE IF EXISTS content_requests CASCADE;
-- DROP TABLE IF EXISTS blog_posts CASCADE;
-- DROP TABLE IF EXISTS blog_accounts CASCADE;
-- DROP TABLE IF EXISTS users CASCADE;
-- DROP TABLE IF EXISTS blog_platforms CASCADE;
-- DROP TABLE IF EXISTS contents CASCADE;
-- DROP TABLE IF EXISTS publications CASCADE;

-- 1. users 테이블 (인증 사용자)
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

-- 2. blog_platforms 테이블 (플랫폼 정의)
CREATE TABLE IF NOT EXISTS blog_platforms (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    logo_url VARCHAR(500),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. blog_accounts 테이블 (사용자의 블로그 계정)
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

-- 4. contents 테이블 (생성된 콘텐츠)
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

-- 5. publications 테이블 (발행 정보)
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

-- 6. 분석 데이터 테이블
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

-- 7. 이미지 테이블
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

-- 업데이트 트리거 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 업데이트 트리거 생성
CREATE TRIGGER update_users_updated_at BEFORE UPDATE
    ON users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blog_platforms_updated_at BEFORE UPDATE
    ON blog_platforms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blog_accounts_updated_at BEFORE UPDATE
    ON blog_accounts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contents_updated_at BEFORE UPDATE
    ON contents FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_publications_updated_at BEFORE UPDATE
    ON publications FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 인덱스 생성
CREATE INDEX idx_blog_accounts_user_id ON blog_accounts(user_id);
CREATE INDEX idx_contents_user_id ON contents(user_id);
CREATE INDEX idx_contents_status ON contents(status);
CREATE INDEX idx_publications_content_id ON publications(content_id);
CREATE INDEX idx_publications_blog_account_id ON publications(blog_account_id);
CREATE INDEX idx_publications_status ON publications(status);
CREATE INDEX idx_analytics_publication_id ON analytics(publication_id);
CREATE INDEX idx_analytics_date ON analytics(date DESC);

-- 초기 플랫폼 데이터 삽입
INSERT INTO blog_platforms (name, slug, description) VALUES
('WordPress', 'wordpress', 'Popular open-source blogging platform'),
('Tistory', 'tistory', 'Korean blogging platform by Kakao'),
('Naver Blog', 'naver', 'Korean blogging platform by Naver')
ON CONFLICT (slug) DO NOTHING;

-- 테스트 사용자 생성 (비밀번호: testpass123)
-- INSERT INTO users (email, hashed_password, full_name, is_active)
-- VALUES ('test@example.com', '$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36', 'Test User', true);

-- Row Level Security 활성화 (선택사항)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_platforms ENABLE ROW LEVEL SECURITY;
ALTER TABLE blog_accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE contents ENABLE ROW LEVEL SECURITY;
ALTER TABLE publications ENABLE ROW LEVEL SECURITY;
ALTER TABLE analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE images ENABLE ROW LEVEL SECURITY;

-- RLS 정책 예시 (모든 사용자가 읽기 가능, 본인 데이터만 수정 가능)
CREATE POLICY "Enable read access for all users" ON blog_platforms
    FOR SELECT USING (true);

CREATE POLICY "Enable insert for authenticated users only" ON contents
    FOR INSERT WITH CHECK (auth.uid() IS NOT NULL);

CREATE POLICY "Enable update for users based on user_id" ON contents
    FOR UPDATE USING (auth.uid()::text = user_id::text);

-- 뷰 생성 (유용한 조합)
CREATE OR REPLACE VIEW publication_details AS
SELECT 
    p.id,
    p.published_url,
    p.status as publication_status,
    p.published_at,
    c.title,
    c.content,
    c.keywords,
    ba.blog_name,
    ba.blog_url,
    bp.name as platform_name,
    bp.slug as platform_slug
FROM publications p
JOIN contents c ON p.content_id = c.id
JOIN blog_accounts ba ON p.blog_account_id = ba.id
JOIN blog_platforms bp ON ba.platform_id = bp.id;

-- 함수: 최근 게시물 가져오기
CREATE OR REPLACE FUNCTION get_recent_publications(limit_count INT DEFAULT 10)
RETURNS TABLE (
    id UUID,
    title VARCHAR,
    blog_name VARCHAR,
    platform_name VARCHAR,
    published_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        c.title,
        ba.blog_name,
        bp.name as platform_name,
        p.published_at
    FROM publications p
    JOIN contents c ON p.content_id = c.id
    JOIN blog_accounts ba ON p.blog_account_id = ba.id
    JOIN blog_platforms bp ON ba.platform_id = bp.id
    WHERE p.status = 'published'
    ORDER BY p.published_at DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- 완료 메시지
-- SELECT '✅ 모든 테이블과 초기 데이터가 성공적으로 생성되었습니다!' as message;