#!/usr/bin/env python3
"""
간단한 테스트 서버 - Claude API 연동 테스트용
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import asyncio
from anthropic import Anthropic
import os
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

app = FastAPI(
    title="Blog Automation Test API",
    description="Claude API 테스트용 간단한 서버",
    version="1.0.0"
)

# Claude 클라이언트 초기화
claude_client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY"))

class ContentRequest(BaseModel):
    keywords: List[str]
    content_type: str = "blog_post"
    target_length: int = 1500
    tone: Optional[str] = "친근하고 전문적인"

class ContentResponse(BaseModel):
    title: str
    content: str
    meta_description: str
    word_count: int
    ai_model_used: str = "claude-3-sonnet"

@app.get("/")
async def root():
    return {
        "message": "🤖 AI 블로그 자동화 시스템 테스트 서버",
        "status": "running",
        "claude_api": "connected" if os.getenv("CLAUDE_API_KEY") else "not configured"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "claude_available": bool(os.getenv("CLAUDE_API_KEY"))}

@app.post("/test/generate", response_model=ContentResponse)
async def test_generate_content(request: ContentRequest):
    """Claude API를 사용해서 간단한 콘텐츠 생성 테스트"""
    
    if not os.getenv("CLAUDE_API_KEY"):
        raise HTTPException(status_code=500, detail="Claude API 키가 설정되지 않았습니다")
    
    try:
        # 간단한 프롬프트로 콘텐츠 생성
        prompt = f"""
        다음 키워드를 바탕으로 {request.target_length}자 분량의 블로그 글을 작성해주세요:
        
        키워드: {', '.join(request.keywords)}
        콘텐츠 유형: {request.content_type}
        톤앤매너: {request.tone}
        
        다음 형식으로 작성해주세요:
        
        제목: [SEO 친화적인 제목]
        
        메타설명: [150자 이내의 메타 설명]
        
        본문:
        [HTML 태그를 사용한 구조화된 본문 내용]
        
        요구사항:
        - 자연스러운 한국어 사용
        - HTML 태그로 구조화 (<h2>, <p>, <ul> 등)
        - 키워드를 자연스럽게 포함
        - 독자에게 유용한 실용적 정보 제공
        """
        
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=3000,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content_text = response.content[0].text
        
        # 응답 파싱 (간단한 방식)
        lines = content_text.split('\n')
        title = ""
        meta_description = ""
        content_body = ""
        
        parsing_content = False
        for line in lines:
            if line.startswith("제목:"):
                title = line.replace("제목:", "").strip()
            elif line.startswith("메타설명:"):
                meta_description = line.replace("메타설명:", "").strip()
            elif line.startswith("본문:"):
                parsing_content = True
            elif parsing_content:
                content_body += line + "\n"
        
        # 기본값 설정
        if not title:
            title = f"{request.keywords[0]}에 대한 완벽 가이드"
        if not meta_description:
            meta_description = f"{request.keywords[0]}에 대해 알아야 할 모든 것을 정리했습니다."
        if not content_body:
            content_body = content_text
        
        # 단어 수 계산 (간단한 방식)
        word_count = len(content_body.split())
        
        return ContentResponse(
            title=title,
            content=content_body.strip(),
            meta_description=meta_description,
            word_count=word_count,
            ai_model_used="claude-3-sonnet"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"콘텐츠 생성 실패: {str(e)}")

@app.get("/test/claude")
async def test_claude_connection():
    """Claude API 연결 테스트"""
    
    if not os.getenv("CLAUDE_API_KEY"):
        return {"status": "error", "message": "Claude API 키가 설정되지 않았습니다"}
    
    try:
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=100,
            messages=[{"role": "user", "content": "안녕하세요! Claude API 연결 테스트입니다. 간단히 인사해주세요."}],
            temperature=0.3
        )
        
        return {
            "status": "success",
            "message": "Claude API 연결 성공!",
            "response": response.content[0].text
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": f"Claude API 연결 실패: {str(e)}"
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 블로그 자동화 테스트 서버 시작!")
    print("📖 API 문서: http://localhost:8000/docs")
    print("🤖 Claude API 테스트: http://localhost:8000/test/claude")
    uvicorn.run(app, host="0.0.0.0", port=8000)