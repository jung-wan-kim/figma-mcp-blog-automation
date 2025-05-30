from typing import List, Dict
import re
from bs4 import BeautifulSoup
import structlog

logger = structlog.get_logger()


class SEOOptimizer:
    def __init__(self):
        self.keyword_density_target = 0.02  # 2%
        self.min_heading_count = 3
        self.optimal_paragraph_length = 150  # words
        self.optimal_sentence_length = 20  # words
    
    async def optimize_content(self, content: str, keywords: List[str]) -> Dict:
        """콘텐츠를 SEO 최적화하고 점수를 계산합니다."""
        
        # HTML 파싱
        soup = BeautifulSoup(content, 'html.parser')
        
        # 분석 수행
        keyword_density = self._calculate_keyword_density(soup.get_text(), keywords)
        readability_score = self._calculate_readability_score(soup.get_text())
        heading_analysis = self._analyze_heading_structure(soup)
        
        # 최적화 수행
        optimized_soup = await self._optimize_content_structure(soup, keywords)
        optimized_content = str(optimized_soup)
        
        # SEO 점수 계산
        seo_score = self._calculate_seo_score(
            keyword_density, readability_score, heading_analysis
        )
        
        # 최적화 제안 생성
        suggestions = self._generate_optimization_suggestions(
            keyword_density, readability_score, heading_analysis
        )
        
        return {
            "optimized_content": optimized_content,
            "seo_score": seo_score,
            "readability_score": readability_score,
            "keyword_density": keyword_density,
            "heading_analysis": heading_analysis,
            "suggestions": suggestions
        }
    
    def _calculate_keyword_density(self, text: str, keywords: List[str]) -> Dict:
        """키워드 밀도를 계산합니다."""
        text_lower = text.lower()
        words = text_lower.split()
        total_words = len(words)
        
        keyword_counts = {}
        for keyword in keywords:
            count = text_lower.count(keyword.lower())
            density = (count / total_words) * 100 if total_words > 0 else 0
            keyword_counts[keyword] = {
                "count": count,
                "density": round(density, 2)
            }
        
        return keyword_counts
    
    def _calculate_readability_score(self, text: str) -> int:
        """가독성 점수를 계산합니다 (Flesch Reading Ease 변형)."""
        sentences = re.split(r'[.!?]+', text)
        words = text.split()
        
        if not sentences or not words:
            return 0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # 한국어에 맞게 조정된 간단한 가독성 점수
        # 문장 길이가 짧을수록 높은 점수
        if avg_sentence_length <= 15:
            score = 90
        elif avg_sentence_length <= 20:
            score = 80
        elif avg_sentence_length <= 25:
            score = 70
        elif avg_sentence_length <= 30:
            score = 60
        else:
            score = 50
        
        return score
    
    def _analyze_heading_structure(self, soup: BeautifulSoup) -> Dict:
        """헤딩 구조를 분석합니다."""
        h1_tags = soup.find_all('h1')
        h2_tags = soup.find_all('h2')
        h3_tags = soup.find_all('h3')
        
        # 헤딩에 키워드가 포함되어 있는지 확인
        heading_texts = []
        for tag in h1_tags + h2_tags + h3_tags:
            heading_texts.append(tag.get_text().strip())
        
        return {
            "h1_count": len(h1_tags),
            "h2_count": len(h2_tags),
            "h3_count": len(h3_tags),
            "total_headings": len(h1_tags) + len(h2_tags) + len(h3_tags),
            "heading_texts": heading_texts
        }
    
    async def _optimize_content_structure(
        self, 
        soup: BeautifulSoup, 
        keywords: List[str]
    ) -> BeautifulSoup:
        """콘텐츠 구조를 최적화합니다."""
        
        # 첫 번째 단락에 주요 키워드 포함 확인
        first_paragraph = soup.find('p')
        if first_paragraph and keywords:
            text = first_paragraph.get_text().lower()
            if keywords[0].lower() not in text:
                # 키워드를 자연스럽게 포함하도록 수정
                logger.info(
                    "Adding primary keyword to first paragraph",
                    keyword=keywords[0]
                )
        
        # 긴 단락 분할
        for p in soup.find_all('p'):
            text = p.get_text()
            words = text.split()
            if len(words) > self.optimal_paragraph_length * 1.5:
                # 단락이 너무 길면 분할 제안
                logger.info(
                    "Long paragraph detected",
                    word_count=len(words)
                )
        
        # alt 태그가 없는 이미지에 키워드 기반 alt 텍스트 추가
        for img in soup.find_all('img'):
            if not img.get('alt'):
                img['alt'] = f"{keywords[0]} 관련 이미지"
        
        return soup
    
    def _calculate_seo_score(
        self,
        keyword_density: Dict,
        readability_score: int,
        heading_analysis: Dict
    ) -> int:
        """종합 SEO 점수를 계산합니다."""
        score = 0
        
        # 키워드 밀도 점수 (30점)
        if keyword_density:
            primary_keyword_density = list(keyword_density.values())[0]['density']
            if 1.5 <= primary_keyword_density <= 2.5:
                score += 30
            elif 1.0 <= primary_keyword_density <= 3.0:
                score += 20
            else:
                score += 10
        
        # 가독성 점수 (30점)
        if readability_score >= 80:
            score += 30
        elif readability_score >= 70:
            score += 20
        else:
            score += 10
        
        # 헤딩 구조 점수 (20점)
        if heading_analysis['total_headings'] >= self.min_heading_count:
            score += 10
        if heading_analysis['h2_count'] >= 2:
            score += 10
        
        # 기본 점수 (20점)
        score += 20
        
        return min(score, 100)
    
    def _generate_optimization_suggestions(
        self,
        keyword_density: Dict,
        readability_score: int,
        heading_analysis: Dict
    ) -> List[str]:
        """SEO 최적화 제안사항을 생성합니다."""
        suggestions = []
        
        # 키워드 밀도 관련 제안
        if keyword_density:
            primary_keyword_density = list(keyword_density.values())[0]['density']
            if primary_keyword_density < 1.0:
                suggestions.append("주요 키워드 사용을 늘려주세요 (현재 밀도가 너무 낮습니다)")
            elif primary_keyword_density > 3.0:
                suggestions.append("키워드 과다 사용을 피해주세요 (키워드 스터핑 위험)")
        
        # 가독성 관련 제안
        if readability_score < 70:
            suggestions.append("문장을 더 짧고 명확하게 작성해주세요")
        
        # 헤딩 구조 관련 제안
        if heading_analysis['total_headings'] < self.min_heading_count:
            suggestions.append("더 많은 소제목을 사용하여 콘텐츠를 구조화해주세요")
        
        if heading_analysis['h1_count'] == 0:
            suggestions.append("H1 태그를 추가해주세요 (페이지당 하나)")
        elif heading_analysis['h1_count'] > 1:
            suggestions.append("H1 태그는 페이지당 하나만 사용해주세요")
        
        if not suggestions:
            suggestions.append("훌륭합니다! SEO 최적화가 잘 되어 있습니다.")
        
        return suggestions