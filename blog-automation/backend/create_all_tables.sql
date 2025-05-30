
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
    


    CREATE OR REPLACE FUNCTION update_updated_at_column()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.updated_at = CURRENT_TIMESTAMP;
        RETURN NEW;
    END;
    $$ language 'plpgsql';
    


    CREATE TRIGGER update_blog_platforms_updated_at BEFORE UPDATE
        ON blog_platforms FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    


    CREATE TRIGGER update_blog_posts_updated_at BEFORE UPDATE
        ON blog_posts FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    


    CREATE INDEX IF NOT EXISTS idx_blog_posts_platform_id ON blog_posts(platform_id);
    


    CREATE INDEX IF NOT EXISTS idx_blog_posts_status ON blog_posts(status);
    


    CREATE INDEX IF NOT EXISTS idx_blog_posts_published_at ON blog_posts(published_at DESC);
    