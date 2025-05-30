from typing import List, Dict, Optional
import aiohttp
import structlog
from app.core.config import settings

logger = structlog.get_logger()


class ImageService:
    def __init__(self):
        self.unsplash_access_key = settings.unsplash_access_key
        self.unsplash_base_url = "https://api.unsplash.com"
    
    async def search_images(
        self,
        query: str,
        count: int = 3,
        orientation: str = "landscape"
    ) -> List[Dict]:
        """
        Unsplash API를 사용해서 키워드에 맞는 이미지 검색
        """
        if not self.unsplash_access_key:
            logger.warning("Unsplash API 키가 설정되지 않음 - 기본 이미지 반환")
            return self._get_default_images(count)
        
        try:
            async with aiohttp.ClientSession() as session:
                url = f"{self.unsplash_base_url}/search/photos"
                headers = {
                    "Authorization": f"Client-ID {self.unsplash_access_key}"
                }
                params = {
                    "query": query,
                    "per_page": count,
                    "orientation": orientation,
                    "content_filter": "high",
                    "order_by": "relevant"
                }
                
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._format_unsplash_results(data["results"])
                    else:
                        logger.error(f"Unsplash API 오류: {response.status}")
                        return self._get_default_images(count)
        
        except Exception as e:
            logger.error(f"이미지 검색 실패: {str(e)}")
            return self._get_default_images(count)
    
    def _format_unsplash_results(self, results: List[Dict]) -> List[Dict]:
        """Unsplash 결과를 표준 포맷으로 변환"""
        formatted = []
        
        for image in results:
            formatted.append({
                "id": image["id"],
                "url": image["urls"]["regular"],
                "thumb_url": image["urls"]["thumb"],
                "download_url": image["urls"]["full"],
                "alt_text": image.get("alt_description", "블로그 이미지"),
                "attribution": {
                    "photographer": image["user"]["name"],
                    "photographer_url": image["user"]["links"]["html"],
                    "source": "Unsplash",
                    "source_url": image["links"]["html"]
                },
                "width": image["width"],
                "height": image["height"]
            })
        
        return formatted
    
    def _get_default_images(self, count: int) -> List[Dict]:
        """기본 이미지 반환 (API 키가 없거나 오류 시)"""
        default_images = [
            {
                "id": "default_1",
                "url": "https://via.placeholder.com/800x600/4A90E2/FFFFFF?text=Blog+Image+1",
                "thumb_url": "https://via.placeholder.com/300x200/4A90E2/FFFFFF?text=Blog+Image+1",
                "download_url": "https://via.placeholder.com/1200x800/4A90E2/FFFFFF?text=Blog+Image+1",
                "alt_text": "블로그 이미지 1",
                "attribution": {
                    "photographer": "Placeholder",
                    "photographer_url": "#",
                    "source": "Placeholder",
                    "source_url": "#"
                },
                "width": 800,
                "height": 600
            },
            {
                "id": "default_2",
                "url": "https://via.placeholder.com/800x600/50C878/FFFFFF?text=Blog+Image+2",
                "thumb_url": "https://via.placeholder.com/300x200/50C878/FFFFFF?text=Blog+Image+2",
                "download_url": "https://via.placeholder.com/1200x800/50C878/FFFFFF?text=Blog+Image+2",
                "alt_text": "블로그 이미지 2",
                "attribution": {
                    "photographer": "Placeholder",
                    "photographer_url": "#",
                    "source": "Placeholder",
                    "source_url": "#"
                },
                "width": 800,
                "height": 600
            },
            {
                "id": "default_3",
                "url": "https://via.placeholder.com/800x600/FF6B6B/FFFFFF?text=Blog+Image+3",
                "thumb_url": "https://via.placeholder.com/300x200/FF6B6B/FFFFFF?text=Blog+Image+3",
                "download_url": "https://via.placeholder.com/1200x800/FF6B6B/FFFFFF?text=Blog+Image+3",
                "alt_text": "블로그 이미지 3",
                "attribution": {
                    "photographer": "Placeholder",
                    "photographer_url": "#",
                    "source": "Placeholder",
                    "source_url": "#"
                },
                "width": 800,
                "height": 600
            }
        ]
        
        return default_images[:count]
    
    async def suggest_images_for_content(
        self,
        title: str,
        keywords: List[str],
        content: str
    ) -> Dict:
        """
        콘텐츠 내용을 분석해서 적절한 이미지 제안
        """
        # 제목에서 핵심 키워드 추출
        title_query = title.replace(":", "").replace("|", "").strip()
        
        # 키워드 조합
        keyword_query = " ".join(keywords[:2])  # 처음 2개 키워드만 사용
        
        try:
            # 1. 제목 기반 이미지 검색
            title_images = await self.search_images(title_query, count=2)
            
            # 2. 키워드 기반 이미지 검색  
            keyword_images = await self.search_images(keyword_query, count=2)
            
            # 3. 대표 이미지 선택 (첫 번째 이미지)
            featured_image = title_images[0] if title_images else keyword_images[0]
            
            return {
                "featured_image": featured_image,
                "suggested_images": {
                    "title_based": title_images,
                    "keyword_based": keyword_images
                },
                "all_images": title_images + keyword_images
            }
        
        except Exception as e:
            logger.error(f"이미지 제안 실패: {str(e)}")
            default_images = self._get_default_images(3)
            return {
                "featured_image": default_images[0],
                "suggested_images": {
                    "title_based": default_images[:2],
                    "keyword_based": default_images[1:]
                },
                "all_images": default_images
            }