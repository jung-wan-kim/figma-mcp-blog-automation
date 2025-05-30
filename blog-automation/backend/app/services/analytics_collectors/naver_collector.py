from typing import Dict, Optional
from playwright.async_api import async_playwright

from app.services.analytics_collectors.base_collector import BaseAnalyticsCollector


class NaverAnalyticsCollector(BaseAnalyticsCollector):
    """네이버 블로그 플랫폼 Analytics Collector"""
    
    async def collect(
        self,
        platform_post_id: str,
        platform_post_url: Optional[str] = None,
        **kwargs
    ) -> Dict:
        try:
            username = kwargs.get("username")
            password = kwargs.get("password")
            blog_id = kwargs.get("blog_id", username)
            
            if not all([username, password]):
                return self._normalize_metrics({})
            
            # Playwright를 사용하여 네이버 블로그 통계 수집
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    # 로그인
                    await self._login(page, username, password)
                    
                    # 통계 페이지로 이동
                    stats_url = f"https://blog.naver.com/BlogStatsView.naver?blogId={blog_id}&logNo={platform_post_id}"
                    await page.goto(stats_url)
                    await page.wait_for_load_state("networkidle")
                    
                    # 통계 데이터 추출
                    stats = await self._extract_stats(page)
                    
                    return self._normalize_metrics(stats)
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            self.logger.error(
                "Naver analytics collection failed",
                post_id=platform_post_id,
                error=str(e)
            )
            return self._normalize_metrics({})
    
    async def _login(self, page, username: str, password: str):
        """네이버 로그인을 수행합니다."""
        try:
            await page.goto("https://nid.naver.com/nidlogin.login")
            
            await page.fill('input[name="id"]', username)
            await page.fill('input[name="pw"]', password)
            await page.click('button[type="submit"]')
            
            await page.wait_for_timeout(3000)
            
        except Exception as e:
            self.logger.error("Naver login failed", error=str(e))
            raise
    
    async def _extract_stats(self, page) -> Dict:
        """통계 페이지에서 데이터를 추출합니다."""
        stats = {}
        
        try:
            # 조회수 추출
            views_element = await page.query_selector('.stats_view_count')
            if views_element:
                views_text = await views_element.inner_text()
                stats["views"] = self._parse_number(views_text)
            
            # 댓글수 추출
            comments_element = await page.query_selector('.stats_comment_count')
            if comments_element:
                comments_text = await comments_element.inner_text()
                stats["comments"] = self._parse_number(comments_text)
            
            # 공감수 추출
            likes_element = await page.query_selector('.stats_sympathy_count')
            if likes_element:
                likes_text = await likes_element.inner_text()
                stats["likes"] = self._parse_number(likes_text)
            
        except Exception as e:
            self.logger.error("Stats extraction failed", error=str(e))
        
        return stats
    
    def _parse_number(self, text: str) -> int:
        """텍스트에서 숫자를 추출합니다."""
        try:
            # 쉼표 제거 및 숫자만 추출
            number_str = ''.join(filter(str.isdigit, text.replace(',', '')))
            return int(number_str) if number_str else 0
        except:
            return 0