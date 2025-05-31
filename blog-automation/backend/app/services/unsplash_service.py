"""
Unsplash API를 사용한 이미지 검색 서비스
"""
import httpx
from typing import List, Dict, Any, Optional
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class UnsplashImageService:
    def __init__(self):
        """Unsplash 클라이언트 초기화"""
        if not settings.unsplash_access_key:
            raise ValueError("Unsplash API 키가 설정되지 않았습니다. .env 파일에 UNSPLASH_ACCESS_KEY를 설정해주세요.")
        
        self.access_key = settings.unsplash_access_key
        self.base_url = "https://api.unsplash.com"
        self.headers = {
            "Authorization": f"Client-ID {self.access_key}",
            "Accept-Version": "v1"
        }

    async def search_images(
        self, 
        query: str, 
        count: int = 5,
        orientation: str = "landscape"
    ) -> List[Dict[str, Any]]:
        """
        키워드로 이미지 검색
        
        Args:
            query: 검색 키워드
            count: 가져올 이미지 수
            orientation: 이미지 방향 (landscape, portrait, squarish)
            
        Returns:
            이미지 정보 리스트
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search/photos",
                    headers=self.headers,
                    params={
                        "query": query,
                        "per_page": count,
                        "orientation": orientation,
                        "content_filter": "high",
                        "order_by": "relevant"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    images = []
                    
                    for photo in data.get("results", []):
                        image_info = {
                            "id": photo.get("id"),
                            "url": photo.get("urls", {}).get("regular"),
                            "thumb_url": photo.get("urls", {}).get("thumb"),
                            "small_url": photo.get("urls", {}).get("small"),
                            "alt_text": photo.get("alt_description", f"{query} 관련 이미지"),
                            "attribution": {
                                "photographer": photo.get("user", {}).get("name", "Unknown"),
                                "source": "Unsplash",
                                "profile_url": photo.get("user", {}).get("links", {}).get("html")
                            },
                            "width": photo.get("width", 800),
                            "height": photo.get("height", 600),
                            "download_url": photo.get("links", {}).get("download")
                        }
                        images.append(image_info)
                    
                    logger.info(f"Unsplash 이미지 검색 성공", query=query, count=len(images))
                    return images
                    
                else:
                    logger.error(f"Unsplash API 오류: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            logger.error(f"Unsplash 이미지 검색 실패: {e}")
            return []

    async def get_featured_image(self, keywords: List[str]) -> Optional[Dict[str, Any]]:
        """
        키워드 기반으로 대표 이미지 하나 가져오기
        
        Args:
            keywords: 키워드 리스트
            
        Returns:
            대표 이미지 정보
        """
        # 첫 번째 키워드로 검색
        main_keyword = keywords[0] if keywords else "technology"
        images = await self.search_images(main_keyword, count=1)
        
        if images:
            return images[0]
        
        # 첫 번째 키워드로 실패하면 일반적인 키워드로 재시도
        fallback_keywords = ["abstract", "nature", "technology", "business"]
        for keyword in fallback_keywords:
            images = await self.search_images(keyword, count=1)
            if images:
                logger.info(f"대체 키워드로 이미지 찾음: {keyword}")
                return images[0]
        
        return None

    async def get_content_images(self, keywords: List[str], title: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        콘텐츠용 다양한 이미지들 가져오기
        
        Args:
            keywords: 키워드 리스트
            title: 콘텐츠 제목
            
        Returns:
            제목 기반 이미지와 키워드 기반 이미지
        """
        result = {
            "title_based": [],
            "keyword_based": []
        }
        
        # 제목에서 주요 단어 추출해서 검색
        title_words = title.split()[:3]  # 제목의 첫 3단어
        if title_words:
            title_query = " ".join(title_words)
            title_images = await self.search_images(title_query, count=2)
            result["title_based"] = title_images
        
        # 각 키워드로 이미지 검색
        for keyword in keywords[:3]:  # 최대 3개 키워드
            keyword_images = await self.search_images(keyword, count=2)
            result["keyword_based"].extend(keyword_images)
        
        # 중복 제거
        seen_ids = set()
        unique_keyword_images = []
        for img in result["keyword_based"]:
            if img["id"] not in seen_ids:
                seen_ids.add(img["id"])
                unique_keyword_images.append(img)
        
        result["keyword_based"] = unique_keyword_images[:4]  # 최대 4개
        
        logger.info(f"콘텐츠 이미지 수집 완료", 
                   title_count=len(result["title_based"]),
                   keyword_count=len(result["keyword_based"]))
        
        return result


# 글로벌 인스턴스
unsplash_service = None

def get_unsplash_service() -> UnsplashImageService:
    """Unsplash 서비스 인스턴스 반환"""
    global unsplash_service
    if unsplash_service is None:
        unsplash_service = UnsplashImageService()
    return unsplash_service