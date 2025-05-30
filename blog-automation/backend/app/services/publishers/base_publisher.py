from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger()


class BasePublisher(ABC):
    """블로그 플랫폼 Publisher의 기본 클래스"""
    
    def __init__(self, credentials: Dict):
        self.credentials = credentials
        self.logger = logger.bind(publisher=self.__class__.__name__)
    
    @abstractmethod
    async def publish(
        self,
        title: str,
        content: str,
        meta_description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        **kwargs
    ) -> Dict:
        """콘텐츠를 발행합니다.
        
        Returns:
            Dict: {
                "success": bool,
                "post_id": str (optional),
                "url": str (optional),
                "error": str (optional)
            }
        """
        pass
    
    @abstractmethod
    async def update(
        self,
        post_id: str,
        title: Optional[str] = None,
        content: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """기존 포스트를 업데이트합니다."""
        pass
    
    @abstractmethod
    async def delete(self, post_id: str) -> Dict:
        """포스트를 삭제합니다."""
        pass
    
    def _prepare_content(self, content: str) -> str:
        """플랫폼에 맞게 콘텐츠를 준비합니다."""
        # 기본적으로는 그대로 반환
        return content
    
    def _prepare_tags(self, keywords: List[str]) -> List[str]:
        """키워드를 플랫폼에 맞는 태그로 변환합니다."""
        # 기본적으로는 그대로 반환
        return keywords if keywords else []