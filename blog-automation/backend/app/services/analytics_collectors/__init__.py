from app.models.blog_account import BlogPlatform
from app.services.analytics_collectors.wordpress_collector import WordPressAnalyticsCollector
from app.services.analytics_collectors.tistory_collector import TistoryAnalyticsCollector
from app.services.analytics_collectors.naver_collector import NaverAnalyticsCollector


def get_analytics_collector(platform: BlogPlatform):
    """플랫폼에 맞는 Analytics Collector 인스턴스를 반환합니다."""
    
    if platform == BlogPlatform.WORDPRESS:
        return WordPressAnalyticsCollector()
    elif platform == BlogPlatform.TISTORY:
        return TistoryAnalyticsCollector()
    elif platform == BlogPlatform.NAVER:
        return NaverAnalyticsCollector()
    else:
        raise ValueError(f"Unsupported platform: {platform}")