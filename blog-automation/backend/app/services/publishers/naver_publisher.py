from typing import Dict, List, Optional
from playwright.async_api import async_playwright
import asyncio
from bs4 import BeautifulSoup

from app.services.publishers.base_publisher import BasePublisher


class NaverPublisher(BasePublisher):
    """네이버 블로그 플랫폼 Publisher"""
    
    def __init__(self, credentials: Dict):
        super().__init__(credentials)
        self.username = credentials.get("username")
        self.password = credentials.get("password")
        self.blog_id = credentials.get("blog_id", self.username)  # 기본값은 username
    
    async def publish(
        self,
        title: str,
        content: str,
        meta_description: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        **kwargs
    ) -> Dict:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    # 로그인
                    login_success = await self._login(page)
                    if not login_success:
                        return {
                            "success": False,
                            "error": "Login failed"
                        }
                    
                    # 블로그 글쓰기 페이지로 이동
                    await page.goto(f"https://blog.naver.com/{self.blog_id}/postwrite")
                    await page.wait_for_load_state("networkidle")
                    
                    # 제목 입력
                    title_input = await page.wait_for_selector('input[name="post.title"]', timeout=10000)
                    await title_input.fill(title)
                    
                    # 에디터가 로드될 때까지 대기
                    await page.wait_for_selector('.se-content', timeout=10000)
                    
                    # 콘텐츠 입력 (Smart Editor One)
                    await self._input_content_to_editor(page, content)
                    
                    # 태그 입력
                    if keywords:
                        await self._add_tags(page, keywords)
                    
                    # 공개 설정
                    visibility = kwargs.get("visibility", "public")
                    await self._set_visibility(page, visibility)
                    
                    # 발행 버튼 클릭
                    publish_button = await page.wait_for_selector('button:has-text("발행")', timeout=5000)
                    await publish_button.click()
                    
                    # 발행 완료 대기
                    await page.wait_for_navigation(timeout=10000)
                    
                    # 발행된 URL 가져오기
                    current_url = page.url
                    
                    # 포스트 ID 추출
                    post_id = self._extract_post_id(current_url)
                    
                    self.logger.info(
                        "Naver blog post published successfully",
                        post_id=post_id,
                        url=current_url
                    )
                    
                    return {
                        "success": True,
                        "post_id": post_id,
                        "url": current_url
                    }
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            self.logger.error("Naver publish error", error=str(e))
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
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    # 로그인
                    login_success = await self._login(page)
                    if not login_success:
                        return {
                            "success": False,
                            "error": "Login failed"
                        }
                    
                    # 수정 페이지로 이동
                    edit_url = f"https://blog.naver.com/{self.blog_id}/postwrite/{post_id}"
                    await page.goto(edit_url)
                    await page.wait_for_load_state("networkidle")
                    
                    # 제목 수정
                    if title:
                        title_input = await page.wait_for_selector('input[name="post.title"]', timeout=10000)
                        await title_input.fill("")
                        await title_input.fill(title)
                    
                    # 콘텐츠 수정
                    if content:
                        # 기존 콘텐츠 삭제
                        await page.evaluate("""
                            const editor = document.querySelector('.se-content');
                            if (editor) {
                                editor.innerHTML = '';
                            }
                        """)
                        
                        # 새 콘텐츠 입력
                        await self._input_content_to_editor(page, content)
                    
                    # 수정 버튼 클릭
                    update_button = await page.wait_for_selector('button:has-text("수정")', timeout=5000)
                    await update_button.click()
                    
                    # 수정 완료 대기
                    await page.wait_for_navigation(timeout=10000)
                    
                    return {
                        "success": True,
                        "post_id": post_id,
                        "url": page.url
                    }
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            self.logger.error("Naver update error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete(self, post_id: str) -> Dict:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context()
                page = await context.new_page()
                
                try:
                    # 로그인
                    login_success = await self._login(page)
                    if not login_success:
                        return {
                            "success": False,
                            "error": "Login failed"
                        }
                    
                    # 블로그 관리 페이지로 이동
                    await page.goto(f"https://blog.naver.com/{self.blog_id}/admin/post")
                    await page.wait_for_load_state("networkidle")
                    
                    # 포스트 찾기 및 삭제
                    # 포스트 체크박스 선택
                    checkbox = await page.wait_for_selector(f'input[value="{post_id}"]', timeout=10000)
                    await checkbox.check()
                    
                    # 삭제 버튼 클릭
                    delete_button = await page.wait_for_selector('button:has-text("삭제")', timeout=5000)
                    await delete_button.click()
                    
                    # 확인 대화상자 처리
                    page.on("dialog", lambda dialog: dialog.accept())
                    
                    # 삭제 완료 대기
                    await page.wait_for_timeout(2000)
                    
                    return {"success": True}
                    
                finally:
                    await browser.close()
                    
        except Exception as e:
            self.logger.error("Naver delete error", error=str(e))
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _login(self, page) -> bool:
        """네이버 로그인을 수행합니다."""
        try:
            await page.goto("https://nid.naver.com/nidlogin.login")
            
            # 아이디 입력
            await page.fill('input[name="id"]', self.username)
            
            # 비밀번호 입력
            await page.fill('input[name="pw"]', self.password)
            
            # 로그인 버튼 클릭
            await page.click('button[type="submit"]')
            
            # 로그인 완료 대기
            await page.wait_for_timeout(3000)
            
            # 로그인 성공 확인
            current_url = page.url
            if "nid.naver.com" not in current_url:
                return True
            
            # 추가 인증이 필요한 경우 처리
            # (예: 2단계 인증, 캡차 등)
            
            return False
            
        except Exception as e:
            self.logger.error("Login error", error=str(e))
            return False
    
    async def _input_content_to_editor(self, page, content: str):
        """Smart Editor One에 콘텐츠를 입력합니다."""
        # HTML 콘텐츠를 에디터에 맞게 변환
        soup = BeautifulSoup(content, 'html.parser')
        
        # 에디터 클릭하여 포커스
        editor = await page.wait_for_selector('.se-content', timeout=10000)
        await editor.click()
        
        # 텍스트와 HTML 요소를 순차적으로 입력
        for element in soup.children:
            if element.name == 'p':
                await page.keyboard.type(element.get_text())
                await page.keyboard.press('Enter')
            elif element.name in ['h1', 'h2', 'h3']:
                # 제목 스타일 적용
                await self._apply_heading_style(page, element.name)
                await page.keyboard.type(element.get_text())
                await page.keyboard.press('Enter')
            elif element.name == 'ul':
                for li in element.find_all('li'):
                    await page.keyboard.type(f"• {li.get_text()}")
                    await page.keyboard.press('Enter')
            elif element.name == 'ol':
                for i, li in enumerate(element.find_all('li'), 1):
                    await page.keyboard.type(f"{i}. {li.get_text()}")
                    await page.keyboard.press('Enter')
            else:
                # 기타 텍스트
                await page.keyboard.type(str(element))
                await page.keyboard.press('Enter')
    
    async def _apply_heading_style(self, page, heading_type: str):
        """제목 스타일을 적용합니다."""
        # Smart Editor One의 제목 스타일 버튼 클릭
        style_map = {
            'h1': '제목1',
            'h2': '제목2',
            'h3': '제목3'
        }
        
        style_name = style_map.get(heading_type, '제목2')
        
        try:
            # 스타일 드롭다운 열기
            style_button = await page.wait_for_selector('.se-toolbar-button-heading', timeout=5000)
            await style_button.click()
            
            # 스타일 선택
            style_option = await page.wait_for_selector(f'button:has-text("{style_name}")', timeout=3000)
            await style_option.click()
        except:
            # 스타일 적용 실패 시 그냥 진행
            pass
    
    async def _add_tags(self, page, keywords: List[str]):
        """태그를 추가합니다."""
        try:
            # 태그 입력 필드 찾기
            tag_input = await page.wait_for_selector('input[placeholder*="태그"]', timeout=5000)
            
            for keyword in keywords[:10]:  # 네이버는 최대 10개 태그
                await tag_input.fill(keyword)
                await page.keyboard.press('Enter')
                await page.wait_for_timeout(500)
        except:
            # 태그 추가 실패 시 그냥 진행
            pass
    
    async def _set_visibility(self, page, visibility: str):
        """공개 설정을 변경합니다."""
        try:
            if visibility == "private":
                # 비공개 설정
                private_radio = await page.wait_for_selector('input[value="private"]', timeout=5000)
                await private_radio.click()
            elif visibility == "neighbor":
                # 이웃공개 설정
                neighbor_radio = await page.wait_for_selector('input[value="neighbor"]', timeout=5000)
                await neighbor_radio.click()
            # 기본값은 전체공개
        except:
            # 공개 설정 실패 시 그냥 진행
            pass
    
    def _extract_post_id(self, url: str) -> str:
        """URL에서 포스트 ID를 추출합니다."""
        # URL 형식: https://blog.naver.com/{blog_id}/{post_id}
        parts = url.split('/')
        if len(parts) >= 5:
            return parts[-1]
        return ""