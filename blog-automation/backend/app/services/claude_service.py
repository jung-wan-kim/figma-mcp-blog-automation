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

    def _get_tone_guidelines(self, tone: str) -> Dict[str, str]:
        """톤별 가이드라인 반환"""
        tone_map = {
            "친근하고 전문적인": {
                "말투": "~해보세요, ~하시면 좋아요",
                "이모지": "적절히 사용 (문단당 0-1개)",
                "예시": "일상적 비유 + 기술적 설명",
                "호칭": "여러분, 독자님",
                "특징": "전문 지식을 쉽게 설명, 부드러운 어투"
            },
            "전문적이고 상세한": {
                "말투": "~합니다, ~됩니다",
                "이모지": "최소한으로 사용",
                "예시": "실제 코드와 기술 사례",
                "호칭": "개발자, 엔지니어",
                "특징": "정확한 기술 용어, 깊이 있는 분석"
            },
            "캐주얼하고 재미있는": {
                "말투": "~해요, ~죠, ㅋㅋ",
                "이모지": "자유롭게 사용",
                "예시": "재미있는 비유와 밈",
                "호칭": "친구들, 여러분",
                "특징": "유머와 위트, 친구같은 대화"
            }
        }
        return tone_map.get(tone, tone_map["친근하고 전문적인"])

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
            
            # 톤 가이드라인 가져오기
            tone_guide = self._get_tone_guidelines(tone)
            
            # 콘텐츠 유형별 프롬프트 조정
            type_instructions = {
                "blog_post": "블로그 포스트 형태로 일반 독자들이 쉽게 이해할 수 있게",
                "guide": "단계별 가이드 형태로 실용적인 정보를 중심으로",
                "tutorial": "튜토리얼 형태로 실습 가능한 내용을 포함하여",
                "review": "리뷰 형태로 객관적인 분석과 평가를 중심으로",
                "news": "뉴스 기사 형태로 최신 정보와 동향을 중심으로"
            }
            
            type_instruction = type_instructions.get(content_type, "블로그 포스트 형태로")
            
            prompt = f"""당신은 {tone} 스타일로 글을 쓰는 한국의 전문 블로거입니다.
{main_keyword} 분야에서 5년 이상의 실무 경험이 있으며, 복잡한 개념을 쉽게 설명하는 능력이 있습니다.

**주요 키워드**: {main_keyword}
**보조 키워드**: {secondary_keywords}
**콘텐츠 유형**: {content_type}
**최소 글자 수**: {target_length}자 이상 (공백 포함)
**참고**: 이는 최소값입니다. 가치 있는 내용으로 자연스럽게 초과 작성하세요.

**톤 가이드라인**:
- 말투: {tone_guide['말투']}
- 이모지 사용: {tone_guide['이모지']}
- 예시 스타일: {tone_guide['예시']}
- 독자 호칭: {tone_guide['호칭']}
- 특징: {tone_guide['특징']}

**필수 포함 사항**:
1. 개인적 경험이나 에피소드 (최소 1개)
2. 구체적이고 실용적인 예시 (최소 2개)
3. 독자가 바로 적용할 수 있는 실천 팁
4. 문장 길이 다양화 (10-40자 범위)
5. 적절한 감정 표현과 감탄사

**절대 피해야 할 것**:
- AI가 쓴 것 같은 정형화된 패턴
- "결론적으로", "요약하자면", "마무리하며", "이상으로" 같은 틀에 박힌 표현
- 같은 내용의 반복
- 글자 수를 채우기 위한 불필요한 내용
- 억지스러운 끝맺음 (특히 마지막 단락에서 글자 수 채우기)

**작성 지침**:
1. 호기심을 유발하는 질문이나 개인 경험으로 시작
2. {type_instruction} 작성
3. 대화하듯 자연스러운 흐름 유지
4. 중간중간 독자와 소통하는 표현 사용 ("여러분은 어떠신가요?", "제 경험으로는..." 등)
5. 실수나 어려움도 솔직하게 공유
6. 글이 자연스럽게 끝나면 거기서 마무리 (억지로 늘리지 않기)

**출력 형식**:
다음 JSON 형식으로 응답해주세요:
{{
    "title": "매력적이고 클릭하고 싶은 제목",
    "meta_description": "150자 이내의 흥미로운 설명",
    "content": "마크다운 형식의 본문 (사람이 쓴 것처럼 자연스럽게)",
    "word_count": 실제_글자수
}}

마크다운 형식:
- 헤딩은 ## 부터 시작
- 굵은 글씨(**텍스트**)는 강조할 때만
- 리스트는 자연스럽게
- 단락 구분 명확히

**매우 중요**: 
- 사람이 직접 쓴 것처럼 자연스럽고 진정성 있게 작성
- 최소 {target_length}자 이상 작성 (상한선 없음)
- 가치 있는 내용으로 충실하게 작성하여 자연스럽게 길이 달성
- 필수 섹션을 모두 포함하면 자연스럽게 최소 길이 초과

**필수 섹션 체크리스트**:
1. 매력적인 도입부 (개인 경험 포함)
2. 본문 핵심 내용 (최소 3-4개 섹션)
3. 실제 사례나 경험담
4. 실용적인 팁이나 조언
5. 자연스러운 마무리와 독자 소통"""

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