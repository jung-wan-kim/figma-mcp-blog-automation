-- 블로그 자동화 시스템 데이터베이스 스키마
-- Supabase에서 실행할 SQL

-- 블로그 플랫폼 테이블
CREATE TABLE IF NOT EXISTS blog_platforms (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    platform_type VARCHAR(50) NOT NULL, -- tistory, wordpress, naver
    url VARCHAR(500) NOT NULL,
    username VARCHAR(255),
    post_count INTEGER DEFAULT 0,
    total_views INTEGER DEFAULT 0,
    total_likes INTEGER DEFAULT 0,
    api_key VARCHAR(500), -- 암호화된 API 키
    api_secret VARCHAR(500), -- 암호화된 API 시크릿
    access_token TEXT, -- 암호화된 액세스 토큰
    is_active BOOLEAN DEFAULT true,
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
    status VARCHAR(50) DEFAULT 'draft', -- draft, published, scheduled, failed
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    tags TEXT[], -- PostgreSQL 배열
    featured_image_url VARCHAR(1000),
    scheduled_at TIMESTAMP WITH TIME ZONE,
    published_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 콘텐츠 생성 요청 테이블
CREATE TABLE IF NOT EXISTS content_requests (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    keywords TEXT[] NOT NULL,
    content_type VARCHAR(50) DEFAULT 'blog_post',
    target_length INTEGER DEFAULT 3000,
    tone VARCHAR(100),
    ai_model_used VARCHAR(100),
    generated_title VARCHAR(500),
    generated_content TEXT,
    word_count INTEGER,
    status VARCHAR(50) DEFAULT 'pending', -- pending, generating, completed, failed
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE
);

-- 분석 데이터 테이블
CREATE TABLE IF NOT EXISTS analytics_data (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    post_id UUID REFERENCES blog_posts(id) ON DELETE CASCADE,
    platform_id UUID REFERENCES blog_platforms(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    avg_time_on_page DECIMAL(10, 2),
    bounce_rate DECIMAL(5, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(post_id, date)
);

-- 이미지 저장소 테이블
CREATE TABLE IF NOT EXISTS images (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    url VARCHAR(1000) NOT NULL,
    thumb_url VARCHAR(1000),
    alt_text VARCHAR(500),
    width INTEGER,
    height INTEGER,
    size_bytes INTEGER,
    mime_type VARCHAR(100),
    source VARCHAR(100), -- unsplash, pexels, etc.
    photographer VARCHAR(255),
    attribution TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 발행 이력 테이블
CREATE TABLE IF NOT EXISTS publication_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    post_id UUID REFERENCES blog_posts(id) ON DELETE CASCADE,
    platform_id UUID REFERENCES blog_platforms(id) ON DELETE CASCADE,
    action VARCHAR(50) NOT NULL, -- publish, update, delete
    status VARCHAR(50) NOT NULL, -- success, failed
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 업데이트 트리거를 위한 함수
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- 업데이트 트리거 생성
CREATE TRIGGER update_blog_platforms_updated_at BEFORE UPDATE
    ON blog_platforms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_blog_posts_updated_at BEFORE UPDATE
    ON blog_posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- 인덱스 생성
CREATE INDEX idx_blog_posts_platform_id ON blog_posts(platform_id);
CREATE INDEX idx_blog_posts_status ON blog_posts(status);
CREATE INDEX idx_blog_posts_published_at ON blog_posts(published_at DESC);
CREATE INDEX idx_analytics_data_post_id ON analytics_data(post_id);
CREATE INDEX idx_analytics_data_date ON analytics_data(date DESC);
CREATE INDEX idx_publication_history_post_id ON publication_history(post_id);

-- RLS (Row Level Security) 정책 (선택사항 - Supabase에서 인증 사용 시)
-- ALTER TABLE blog_platforms ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE blog_posts ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE content_requests ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE analytics_data ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE images ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE publication_history ENABLE ROW LEVEL SECURITY;