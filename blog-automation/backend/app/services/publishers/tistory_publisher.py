from typing import Dict, List, Optional
import aiohttp
from urllib.parse import urlencode

from app.services.publishers.base_publisher import BasePublisher


class TistoryPublisher(BasePublisher):
    """Tistory 플랫폼 Publisher"""
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.access_token = credentials.get("access_token")
        self.blog_name = credentials.get("blog_name")
        self.api_url = "https://www.tistory.com/apis"
    
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
            
            # API 파라미터 준비
            params = {
                "access_token": self.access_token,
                "output": "json",
                "blogName": self.blog_name,
                "title": title,
                "content": prepared_content,
                "visibility": kwargs.get("visibility", "3"),  # 3: 발행
                "category": kwargs.get("category", "0"),  # 0: 카테고리 없음
                "tag": ",".join(tags) if tags else "",
                "acceptComment": kwargs.get("accept_comment", "1"),  # 1: 댓글 허용
            }
            
            # API 호출
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/post/write",
                    data=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("tistory", {}).get("status") == "200":
                            post_id = result["tistory"]["postId"]
                            post_url = result["tistory"]["url"]
                            
                            self.logger.info(
                                "Tistory post published successfully",
                                post_id=post_id,
                                url=post_url
                            )
                            
                            return {
                                "success": True,
                                "post_id": str(post_id),
                                "url": post_url
                            }
                        else:
                            error_msg = result.get("tistory", {}).get("error_message", "Unknown error")
                            self.logger.error(
                                "Tistory publish failed",
                                error=error_msg
                            )
                            
                            return {
                                "success": False,
                                "error": error_msg
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            self.logger.error("Tistory publish error", error=str(e))
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
            # 기존 포스트 정보 조회
            post_info = await self._get_post_info(post_id)
            if not post_info["success"]:
                return post_info
            
            # 업데이트 파라미터 준비
            params = {
                "access_token": self.access_token,
                "output": "json",
                "blogName": self.blog_name,
                "postId": post_id,
                "title": title or post_info["title"],
                "content": self._prepare_content(content) if content else post_info["content"],
            }
            
            # 선택적 파라미터 추가
            if "visibility" in kwargs:
                params["visibility"] = kwargs["visibility"]
            if "category" in kwargs:
                params["category"] = kwargs["category"]
            if "tag" in kwargs:
                params["tag"] = ",".join(kwargs["tag"]) if isinstance(kwargs["tag"], list) else kwargs["tag"]
            
            # API 호출
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/post/modify",
                    data=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("tistory", {}).get("status") == "200":
                            return {
                                "success": True,
                                "post_id": post_id,
                                "url": result["tistory"]["url"]
                            }
                        else:
                            error_msg = result.get("tistory", {}).get("error_message", "Unknown error")
                            return {
                                "success": False,
                                "error": error_msg
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            self.logger.error("Tistory update error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete(self, post_id: str) -> Dict:
        try:
            params = {
                "access_token": self.access_token,
                "output": "json",
                "blogName": self.blog_name,
                "postId": post_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/post/delete",
                    data=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("tistory", {}).get("status") == "200":
                            return {"success": True}
                        else:
                            error_msg = result.get("tistory", {}).get("error_message", "Unknown error")
                            return {
                                "success": False,
                                "error": error_msg
                            }
                    else:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}"
                        }
                        
        except Exception as e:
            self.logger.error("Tistory delete error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_post_info(self, post_id: str) -> Dict:
        """포스트 정보를 조회합니다."""
        try:
            params = {
                "access_token": self.access_token,
                "output": "json",
                "blogName": self.blog_name,
                "postId": post_id
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/post/read",
                    params=params
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        
                        if result.get("tistory", {}).get("status") == "200":
                            item = result["tistory"]["item"]
                            return {
                                "success": True,
                                "title": item["title"],
                                "content": item["content"],
                                "visibility": item["visibility"],
                                "category": item["categoryId"],
                                "tags": item["tags"]["tag"] if item.get("tags") else []
                            }
                        else:
                            return {
                                "success": False,
                                "error": result.get("tistory", {}).get("error_message", "Unknown error")
                            }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _prepare_tags(self, keywords: List[str]) -> List[str]:
        """티스토리 태그 규칙에 맞게 변환합니다."""
        # 티스토리는 쉼표로 구분된 태그를 사용
        # 특수문자 제거 등의 처리
        if not keywords:
            return []
        
        tags = []
        for keyword in keywords:
            # 간단한 정제 작업
            tag = keyword.strip().replace(",", "")
            if tag:
                tags.append(tag)
        
        return tags[:10]  # 티스토리는 최대 10개 태그 지원