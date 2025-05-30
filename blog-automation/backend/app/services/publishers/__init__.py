from app.models.blog_account import BlogPlatform
from app.services.publishers.wordpress_publisher import WordPressPublisher
from app.services.publishers.tistory_publisher import TistoryPublisher
from app.services.publishers.naver_publisher import NaverPublisher


def get_publisher(platform: BlogPlatform, credentials: dict):
    """플랫폼에 맞는 Publisher 인스턴스를 반환합니다."""
    
    if platform == BlogPlatform.WORDPRESS:
        return WordPressPublisher(credentials)
    elif platform == BlogPlatform.TISTORY:
        return TistoryPublisher(credentials)
    elif platform == BlogPlatform.NAVER:
        return NaverPublisher(credentials)
    else:
        raise ValueError(f"Unsupported platform: {platform}")