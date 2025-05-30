"""
Claude API를 사용한 콘텐츠 생성 서비스
"""
import anthropic
from typing import List, Dict, Any
from app.core.config import settings
import structlog

logger = structlog.get_logger()


class ClaudeContentGenerator:
    def __init__(self):
        """Claude 클라이언트 초기화"""
        import os
        
        # 여러 소스에서 API 키 찾기
        api_key = None
        
        # 1. .env 파일의 CLAUDE_API_KEY
        if hasattr(settings, 'claude_api_key') and settings.claude_api_key and settings.claude_api_key != "sk-ant-api03-실제클로드API키를여기에입력하세요":
            api_key = settings.claude_api_key
            logger.info("Claude API 키를 .env 파일에서 로드했습니다")
        
        # 2. 환경변수 ANTHROPIC_API_KEY (Claude Code 등에서 사용)
        elif os.getenv('ANTHROPIC_API_KEY'):
            api_key = os.getenv('ANTHROPIC_API_KEY')
            logger.info("Claude API 키를 ANTHROPIC_API_KEY 환경변수에서 로드했습니다")
        
        # 3. 환경변수 CLAUDE_API_KEY
        elif os.getenv('CLAUDE_API_KEY'):
            api_key = os.getenv('CLAUDE_API_KEY')
            logger.info("Claude API 키를 CLAUDE_API_KEY 환경변수에서 로드했습니다")
        
        if not api_key:
            raise ValueError("Claude API 키가 설정되지 않았습니다. .env 파일의 CLAUDE_API_KEY 또는 환경변수 ANTHROPIC_API_KEY를 설정해주세요.")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = settings.claude_model
        self.max_tokens = settings.claude_max_tokens
        logger.info(f"Claude 클라이언트 초기화 완료: {self.model}")

    def generate_content(
        self, 
        keywords: List[str], 
        content_type: str,
        target_length: int,
        tone: str = "친근하고 전문적인"
    ) -> Dict[str, Any]:
        """
        Claude API를 사용하여 콘텐츠 생성
        
        Args:
            keywords: 키워드 리스트
            content_type: 콘텐츠 유형 (blog_post, guide, tutorial 등)
            target_length: 목표 글자 수
            tone: 톤앤매너
            
        Returns:
            생성된 콘텐츠 딕셔너리
        """
        try:
            main_keyword = keywords[0]
            secondary_keywords = ", ".join(keywords[1:]) if len(keywords) > 1 else ""
            
            # 콘텐츠 유형별 프롬프트 조정
            type_instructions = {
                "blog_post": "블로그 포스트 형태로 일반 독자들이 쉽게 이해할 수 있게",
                "guide": "단계별 가이드 형태로 실용적인 정보를 중심으로",
                "tutorial": "튜토리얼 형태로 실습 가능한 내용을 포함하여",
                "review": "리뷰 형태로 객관적인 분석과 평가를 중심으로",
                "news": "뉴스 기사 형태로 최신 정보와 동향을 중심으로"
            }
            
            type_instruction = type_instructions.get(content_type, "블로그 포스트 형태로")
            
            # 글자 수 계산을 위한 가이드라인
            length_guide = {
                1000: "간결하고 핵심적인 내용으로 구성하되",
                1500: "적당한 분량으로 주요 내용을 다루되",
                2000: "상세한 설명과 예시를 포함하되",
                3000: "포괄적이고 심도 있는 내용으로 구성하되",
                4000: "매우 상세하고 전문적인 내용으로 구성하되",
                5000: "완전하고 포괄적인 가이드 형태로 구성하되"
            }
            
            length_instruction = length_guide.get(target_length, "적절한 분량으로")
            
            prompt = f"""
한국어로 블로그 콘텐츠를 작성해주세요.

**주요 키워드**: {main_keyword}
**보조 키워드**: {secondary_keywords}
**콘텐츠 유형**: {content_type}
**목표 글자 수**: {target_length}자 (공백 포함)
**톤앤매너**: {tone}

**작성 지침**:
1. {type_instruction} {length_instruction} 정확히 {target_length}자 내외(±100자)로 작성해주세요
2. {tone} 톤으로 작성해주세요
3. SEO에 최적화된 구조로 작성해주세요
4. 목차와 소제목을 활용하여 가독성을 높여주세요
5. 실용적이고 유익한 정보를 포함해주세요

**출력 형식**:
다음 JSON 형식으로 응답해주세요:
{{
    "title": "매력적이고 SEO 친화적인 제목",
    "meta_description": "120자 이내의 메타 설명",
    "content": "마크다운 형식의 본문 내용",
    "word_count": 실제_글자수
}}

마크다운 형식으로 본문을 작성할 때:
- 헤딩은 ## 부터 시작 (# 는 제목이므로 사용하지 말 것)
- 적절한 굵은 글씨(**텍스트**)와 리스트 활용
- 코드나 예시가 필요한 경우 ```로 감싸기
- 단락 구분을 명확히 하기

정확한 글자 수를 맞춰서 작성해주세요. 목표 글자 수 {target_length}자에 최대한 가깝게 작성하는 것이 중요합니다.
"""

            # Claude API 호출
            response = self.client.messages.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.7,
                messages=[
                    {
                        "role": "user", 
                        "content": prompt
                    }
                ]
            )
            
            # 응답 파싱
            content_text = response.content[0].text.strip()
            
            # JSON 응답 파싱 시도
            import json
            try:
                # JSON 부분만 추출
                json_start = content_text.find('{')
                json_end = content_text.rfind('}') + 1
                if json_start != -1 and json_end != -1:
                    json_str = content_text[json_start:json_end]
                    content_data = json.loads(json_str)
                else:
                    raise ValueError("JSON 형식을 찾을 수 없습니다")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"JSON 파싱 실패, 기본 구조로 처리: {e}")
                # JSON 파싱 실패 시 기본 구조로 처리
                lines = content_text.split('\n')
                title = f"{main_keyword}에 대한 완벽한 가이드"
                content_data = {
                    "title": title,
                    "meta_description": f"{main_keyword}에 대한 포괄적인 정보를 제공합니다. {', '.join(keywords[:3])}을 활용한 실무 팁을 확인하세요.",
                    "content": content_text,
                    "word_count": len(content_text.replace(' ', ''))
                }
            
            # 실제 글자 수 계산 (공백 포함)
            actual_word_count = len(content_data.get("content", ""))
            content_data["word_count"] = actual_word_count
            
            logger.info(f"Claude API 콘텐츠 생성 완료", 
                       keywords=keywords,
                       target_length=target_length,
                       actual_length=actual_word_count,
                       model=self.model)
            
            return content_data
            
        except anthropic.APIError as e:
            logger.error(f"Claude API 오류: {e}")
            raise Exception(f"Claude API 호출 실패: {str(e)}")
        except Exception as e:
            logger.error(f"콘텐츠 생성 오류: {e}")
            raise Exception(f"콘텐츠 생성 중 오류 발생: {str(e)}")

    def generate_meta_description(self, title: str, keywords: List[str]) -> str:
        """메타 설명 생성"""
        try:
            prompt = f"""
다음 블로그 제목과 키워드를 바탕으로 SEO에 최적화된 메타 설명을 120자 이내로 작성해주세요.

제목: {title}
키워드: {', '.join(keywords)}

조건:
- 120자 이내
- 검색 엔진에서 클릭을 유도할 수 있는 매력적인 문구
- 주요 키워드 포함
- 액션을 유도하는 문구 포함

메타 설명만 응답해주세요.
"""
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                temperature=0.5,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            logger.error(f"메타 설명 생성 오류: {e}")
            # 기본 메타 설명 반환
            return f"{keywords[0]}에 대한 포괄적인 가이드입니다. {', '.join(keywords[:3])}을 활용한 실무 팁을 확인하세요."


# 글로벌 인스턴스
claude_generator = None

def get_claude_generator() -> ClaudeContentGenerator:
    """Claude 생성기 인스턴스 반환"""
    global claude_generator
    if claude_generator is None:
        claude_generator = ClaudeContentGenerator()
    return claude_generator