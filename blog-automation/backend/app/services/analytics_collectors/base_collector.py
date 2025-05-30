from abc import ABC, abstractmethod
from typing import Dict, Optional
import structlog

logger = structlog.get_logger()


class BaseAnalyticsCollector(ABC):
    """Analytics Collector의 기본 클래스"""
    
    def __init__(self):
        self.logger = logger.bind(collector=self.__class__.__name__)
    
    @abstractmethod
    async def collect(
        self,
        platform_post_id: str,
        platform_post_url: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """플랫폼에서 분석 데이터를 수집합니다.
        
        Returns:
            Dict: {
                "views": int,
                "unique_visitors": int,
                "clicks": int,
                "shares": int,
                "comments": int,
                "likes": int,
                "avg_time_on_page": float,
                "bounce_rate": float,
                "keyword_rankings": dict (optional)
            }
        """
        pass
    
    def _normalize_metrics(self, raw_data: Dict) -> Dict:
        """플랫폼별 데이터를 표준 형식으로 정규화합니다."""
        return {
            "views": raw_data.get("views", 0),
            "unique_visitors": raw_data.get("unique_visitors", 0),
            "clicks": raw_data.get("clicks", 0),
            "shares": raw_data.get("shares", 0),
            "comments": raw_data.get("comments", 0),
            "likes": raw_data.get("likes", 0),
            "avg_time_on_page": raw_data.get("avg_time_on_page", 0.0),
            "bounce_rate": raw_data.get("bounce_rate", 0.0)
        }