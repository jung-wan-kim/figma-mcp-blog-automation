from typing import List, Dict, Optional
try:
    import openai
except ImportError:
    openai = None
from anthropic import Anthropic
import structlog

from app.core.config import settings
from app.services.seo_optimizer import SEOOptimizer

logger = structlog.get_logger()


class ContentGeneratorService:
    def __init__(self):
        # OpenAI는 선택사항
        self.openai_client = None
        if openai and settings.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=settings.openai_api_key)
        
        self.claude_client = Anthropic(api_key=settings.claude_api_key)
        self.seo_optimizer = SEOOptimizer()
    
    async def generate_content(
        self,
        keywords: List[str],
        content_type: str,
        style_preset: Optional[str] = None,
        target_length: int = 1500,
        tone: Optional[str] = None,
        ai_model: str = "claude"
    ) -> Dict:
        logger.info(
            "Starting content generation",
            keywords=keywords,
            content_type=content_type,
            ai_model=ai_model
        )
        
        try:
            # 1. 키워드 분석
            keyword_analysis = await self.analyze_keywords(keywords)
            
            # 2. 콘텐츠 아웃라인 생성
            outline = await self.generate_outline(
                keywords, keyword_analysis, content_type
            )
            
            # 3. 제목 생성
            title = await self.generate_title(keywords, content_type, outline)
            
            # 4. 본문 생성
            content = await self.generate_full_content(
                outline, style_preset, target_length, tone, ai_model
            )
            
            # 5. 메타 설명 생성
            meta_description = await self.generate_meta_description(title, content)
            
            # 6. SEO 최적화
            optimized_content = await self.seo_optimizer.optimize_content(
                content, keywords
            )
            
            return {
                "title": title,
                "content": optimized_content["optimized_content"],
                "meta_description": meta_description,
                "seo_score": optimized_content["seo_score"],
                "readability_score": optimized_content["readability_score"],
                "word_count": len(optimized_content["optimized_content"].split()),
                "ai_model_used": ai_model
            }
            
        except Exception as e:
            logger.error("Content generation failed", error=str(e))
            raise
    
    async def analyze_keywords(self, keywords: List[str]) -> Dict:
        prompt = f"""
        다음 키워드들을 분석하여 블로그 콘텐츠 작성에 필요한 정보를 제공해주세요:
        키워드: {', '.join(keywords)}
        
        다음 정보를 포함해주세요:
        1. 주요 타겟 독자층
        2. 검색 의도 (정보성, 거래성, 탐색성 등)
        3. 관련 키워드 및 LSI 키워드
        4. 콘텐츠에 포함해야 할 핵심 주제들
        """
        
        response = self.claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        
        return {"analysis": response.content[0].text}
    
    async def generate_outline(
        self, 
        keywords: List[str], 
        keyword_analysis: Dict,
        content_type: str
    ) -> str:
        prompt = f"""
        다음 정보를 바탕으로 {content_type} 형식의 블로그 글 아웃라인을 작성해주세요:
        
        키워드: {', '.join(keywords)}
        키워드 분석: {keyword_analysis['analysis']}
        
        아웃라인은 다음 구조를 따라주세요:
        1. 서론 (독자의 관심을 끄는 도입부)
        2. 본론 (3-5개의 주요 섹션)
        3. 결론 (핵심 내용 요약 및 행동 유도)
        
        각 섹션에는 구체적인 소제목을 포함해주세요.
        """
        
        response = self.claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        
        return response.content[0].text
    
    async def generate_title(
        self,
        keywords: List[str],
        content_type: str,
        outline: str
    ) -> str:
        prompt = f"""
        다음 정보를 바탕으로 SEO에 최적화되고 클릭을 유도하는 블로그 제목을 생성해주세요:
        
        주요 키워드: {keywords[0]}
        콘텐츠 유형: {content_type}
        아웃라인: {outline[:500]}...
        
        요구사항:
        - 50-60자 이내
        - 주요 키워드 포함
        - 숫자나 리스트 형식 활용 (해당되는 경우)
        - 감정적 호소 또는 이점 강조
        
        3개의 제목 후보를 제시하고, 가장 추천하는 것을 선택해주세요.
        """
        
        response = self.claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        # 응답에서 첫 번째 제목 추출
        titles = response.content[0].text.split('\n')
        return titles[0].strip() if titles else f"{keywords[0]}에 대한 완벽 가이드"
    
    async def generate_full_content(
        self,
        outline: str,
        style_preset: Optional[str],
        target_length: int,
        tone: Optional[str],
        ai_model: str
    ) -> str:
        style_instruction = f"글쓰기 스타일: {style_preset}" if style_preset else ""
        tone_instruction = f"톤앤매너: {tone}" if tone else "친근하고 전문적인"
        
        prompt = f"""
        다음 아웃라인을 바탕으로 {target_length}자 분량의 블로그 글을 작성해주세요:
        
        아웃라인:
        {outline}
        
        작성 지침:
        - {tone_instruction} 톤으로 작성
        - 독자가 쉽게 이해할 수 있는 명확한 문장 사용
        - 각 섹션마다 구체적인 예시나 데이터 포함
        - 자연스러운 문단 전환
        - SEO를 고려한 키워드 자연스럽게 포함
        {style_instruction}
        
        HTML 태그를 사용하여 구조화해주세요:
        - <h2>, <h3>로 제목 구분
        - <p>로 문단 구분
        - <ul>, <ol>로 리스트 작성
        - <strong>, <em>으로 강조
        """
        
        if ai_model == "gpt-4" and self.openai_client:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000,
                temperature=0.7
            )
            return response.choices[0].message.content
        else:
            # 기본적으로 Claude 사용
            response = self.claude_client.messages.create(
                model="claude-3-sonnet-20240229",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4000,
                temperature=0.7
            )
            return response.content[0].text
    
    async def generate_meta_description(self, title: str, content: str) -> str:
        prompt = f"""
        다음 블로그 글의 메타 설명(meta description)을 작성해주세요:
        
        제목: {title}
        내용 요약: {content[:1000]}...
        
        요구사항:
        - 150-160자 이내
        - 핵심 키워드 포함
        - 클릭을 유도하는 설득력 있는 문구
        - 글의 핵심 가치나 이점 강조
        """
        
        response = self.claude_client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )
        
        return response.content[0].text.strip()