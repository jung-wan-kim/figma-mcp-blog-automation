export interface BlogPlatform {
  name: string;
  type?: string; // Frontend expects 'type'
  platform_type?: string; // Backend sends 'platform_type'
  url: string;
  post_count: number;
  total_views?: number;
  total_likes?: number;
}

export interface BlogPost {
  id: number;
  title: string;
  content: string;
  platform: {
    name: string;
    platform_type: string;
    url: string;
    username?: string;
  };
  published_url: string;
  published_at: string;
  status: string;
  views: number;
  likes: number;
  comments: number;
}

export interface DashboardStats {
  total_posts: number;
  platforms: BlogPlatform[];
  recent_posts: BlogPost[];
}

export interface ImageInfo {
  id: string;
  url: string;
  thumb_url: string;
  alt_text: string;
  attribution: {
    photographer: string;
    source: string;
  };
  width: number;
  height: number;
}

export interface ContentResponse {
  title: string;
  content: string;
  meta_description: string;
  word_count: number;
  ai_model_used: string;
  featured_image: ImageInfo;
  suggested_images: {
    title_based: ImageInfo[];
    keyword_based: ImageInfo[];
  };
}

export interface PublishRequest {
  keywords: string[];
  content_type: string;
  target_length: number;
  tone?: string;
  blog_platform: {
    name: string;
    platform_type: string;
    url: string;
    username?: string;
  };
}
