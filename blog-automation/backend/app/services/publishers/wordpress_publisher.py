from typing import Dict, List, Optional
import aiohttp
from bs4 import BeautifulSoup

from app.services.publishers.base_publisher import BasePublisher


class WordPressPublisher(BasePublisher):
    """WordPress 플랫폼 Publisher"""
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.site_url = credentials.get("site_url")
        self.username = credentials.get("username")
        self.password = credentials.get("password")
        self.api_url = f"{self.site_url}/wp-json/wp/v2"
    
    async def publish(
        self,
        title: str,
        content: str,
        meta_description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        **kwargs
    ) -> Dict:
        try:
            # 콘텐츠 준비
            prepared_content = self._prepare_content(content)
            tags = self._prepare_tags(keywords)
            
            # 카테고리 ID 가져오기 (선택사항)
            category_ids = await self._get_or_create_categories(kwargs.get("categories", []))
            
            # 태그 ID 가져오기
            tag_ids = await self._get_or_create_tags(tags)
            
            # 포스트 데이터 준비
            post_data = {
                "title": title,
                "content": prepared_content,
                "status": "publish",
                "categories": category_ids,
                "tags": tag_ids,
            }
            
            # 메타 데이터 추가 (Yoast SEO 플러그인 지원)
            if meta_description:
                post_data["meta"] = {
                    "_yoast_wpseo_metadesc": meta_description
                }
            
            # API 호출
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/posts",
                    json=post_data,
                    auth=aiohttp.BasicAuth(self.username, self.password)
                ) as response:
                    if response.status == 201:
                        result = await response.json()
                        
                        self.logger.info(
                            "WordPress post published successfully",
                            post_id=result["id"],
                            url=result["link"]
                        )
                        
                        return {
                            "success": True,
                            "post_id": str(result["id"]),
                            "url": result["link"]
                        }
                    else:
                        error_text = await response.text()
                        self.logger.error(
                            "WordPress publish failed",
                            status=response.status,
                            error=error_text
                        )
                        
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            self.logger.error("WordPress publish error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update(
        self,
        post_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs
    ) -> Dict:
        try:
            update_data = {}
            
            if title:
                update_data["title"] = title
            
            if content:
                update_data["content"] = self._prepare_content(content)
            
            async with aiohttp.ClientSession() as session:
                async with session.patch(
                    f"{self.api_url}/posts/{post_id}",
                    json=update_data,
                    auth=aiohttp.BasicAuth(self.username, self.password)
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        return {
                            "success": True,
                            "post_id": str(result["id"]),
                            "url": result["link"]
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            self.logger.error("WordPress update error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete(self, post_id: str) -> Dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f"{self.api_url}/posts/{post_id}",
                    auth=aiohttp.BasicAuth(self.username, self.password)
                ) as response:
                    if response.status == 200:
                        return {"success": True}
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            self.logger.error("WordPress delete error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_or_create_categories(self, category_names: List[str]) -> List[int]:
        """카테고리 ID를 가져오거나 생성합니다."""
        category_ids = []
        
        for name in category_names:
            # 기존 카테고리 검색
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/categories",
                    params={"search": name},
                    auth=aiohttp.BasicAuth(self.username, self.password)
                ) as response:
                    if response.status == 200:
                        categories = await response.json()
                        
                        if categories:
                            category_ids.append(categories[0]["id"])
                        else:
                            # 새 카테고리 생성
                            async with session.post(
                                f"{self.api_url}/categories",
                                json={"name": name},
                                auth=aiohttp.BasicAuth(self.username, self.password)
                            ) as create_response:
                                if create_response.status == 201:
                                    new_category = await create_response.json()
                                    category_ids.append(new_category["id"])
        
        return category_ids
    
    async def _get_or_create_tags(self, tag_names: List[str]) -> List[int]:
        """태그 ID를 가져오거나 생성합니다."""
        tag_ids = []
        
        for name in tag_names:
            # 기존 태그 검색
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/tags",
                    params={"search": name},
                    auth=aiohttp.BasicAuth(self.username, self.password)
                ) as response:
                    if response.status == 200:
                        tags = await response.json()
                        
                        if tags:
                            tag_ids.append(tags[0]["id"])
                        else:
                            # 새 태그 생성
                            async with session.post(
                                f"{self.api_url}/tags",
                                json={"name": name},
                                auth=aiohttp.BasicAuth(self.username, self.password)
                            ) as create_response:
                                if create_response.status == 201:
                                    new_tag = await create_response.json()
                                    tag_ids.append(new_tag["id"])
        
        return tag_ids