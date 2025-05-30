from typing import Dict, Any
import aiohttp
from playwright.async_api import async_playwright
import structlog

from app.models.blog_account import BlogPlatform

logger = structlog.get_logger()


async def verify_blog_credentials(platform: BlogPlatform, credentials: Dict[str, Any]) -> bool:
    """블로그 플랫폼 인증 정보를 검증합니다."""
    
    if platform == BlogPlatform.WORDPRESS:
        return await verify_wordpress_credentials(credentials)
    elif platform == BlogPlatform.TISTORY:
        return await verify_tistory_credentials(credentials)
    elif platform == BlogPlatform.NAVER:
        return await verify_naver_credentials(credentials)
    else:
        logger.warning("Unsupported platform", platform=platform)
        return False


async def verify_wordpress_credentials(credentials: Dict[str, Any]) -> bool:
    """WordPress 인증 정보를 검증합니다."""
    try:
        site_url = credentials.get("site_url")
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not all([site_url, username, password]):
            return False
        
        # WordPress REST API 테스트
        api_url = f"{site_url}/wp-json/wp/v2/users/me"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                api_url,
                auth=aiohttp.BasicAuth(username, password)
            ) as response:
                return response.status == 200
                
    except Exception as e:
        logger.error("WordPress verification failed", error=str(e))
        return False


async def verify_tistory_credentials(credentials: Dict[str, Any]) -> bool:
    """Tistory 인증 정보를 검증합니다."""
    try:
        access_token = credentials.get("access_token")
        blog_name = credentials.get("blog_name")
        
        if not all([access_token, blog_name]):
            return False
        
        # Tistory API 테스트
        api_url = "https://www.tistory.com/apis/blog/info"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(
                api_url,
                params={
                    "access_token": access_token,
                    "blogName": blog_name,
                    "output": "json"
                }
            ) as response:
                return response.status == 200
                
    except Exception as e:
        logger.error("Tistory verification failed", error=str(e))
        return False


async def verify_naver_credentials(credentials: Dict[str, Any]) -> bool:
    """네이버 블로그 인증 정보를 검증합니다."""
    try:
        username = credentials.get("username")
        password = credentials.get("password")
        
        if not all([username, password]):
            return False
        
        # 네이버는 공식 API가 제한적이므로 브라우저 자동화로 확인
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            try:
                # 네이버 로그인 페이지로 이동
                await page.goto("https://nid.naver.com/nidlogin.login")
                
                # 로그인 시도
                await page.fill('input[name="id"]', username)
                await page.fill('input[name="pw"]', password)
                await page.click('button[type="submit"]')
                
                # 로그인 성공 확인
                await page.wait_for_timeout(3000)
                
                # 블로그 페이지 접근 가능한지 확인
                await page.goto("https://blog.naver.com/PostList.naver")
                
                # 블로그 관리 페이지가 로드되면 성공
                is_logged_in = await page.locator('.blog_title').count() > 0
                
                return is_logged_in
                
            finally:
                await browser.close()
                
    except Exception as e:
        logger.error("Naver verification failed", error=str(e))
        return False