#!/usr/bin/env python3
"""
이미지가 첨부된 콘텐츠 생성 테스트 스크립트
"""
import asyncio
import httpx
import json
from datetime import datetime

async def test_content_generation():
    """콘텐츠 생성 및 이미지 첨부 테스트"""
    
    test_cases = [
        {
            "name": "AI 기술 가이드",
            "data": {
                "keywords": ["인공지능", "머신러닝", "딥러닝"],
                "content_type": "guide",
                "target_length": 2000,
                "tone": "친근하고 전문적인"
            }
        },
        {
            "name": "웹개발 튜토리얼",
            "data": {
                "keywords": ["React", "JavaScript", "프론트엔드"],
                "content_type": "tutorial",
                "target_length": 1500,
                "tone": "전문적이고 상세한"
            }
        },
        {
            "name": "데이터과학 블로그",
            "data": {
                "keywords": ["Python", "데이터분석", "pandas"],
                "content_type": "blog_post",
                "target_length": 2500,
                "tone": "캐주얼하고 재미있는"
            }
        }
    ]
    
    print("🚀 이미지 첨부 콘텐츠 생성 테스트 시작!")
    print("=" * 60)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n📝 테스트 {i}: {test_case['name']}")
            print(f"키워드: {', '.join(test_case['data']['keywords'])}")
            print(f"목표 길이: {test_case['data']['target_length']}자")
            
            try:
                # API 호출
                response = await client.post(
                    "http://localhost:8000/test/publish",
                    headers={"Content-Type": "application/json"},
                    json=test_case['data']
                )
                
                if response.status_code == 200:
                    result = response.json()
                    
                    if result.get('success'):
                        content = result.get('content', {})
                        
                        print(f"✅ 성공!")
                        print(f"   제목: {content.get('title', 'N/A')}")
                        print(f"   실제 글자 수: {content.get('word_count', 0)}자")
                        print(f"   AI 모델: {result.get('generation_info', {}).get('ai_model', 'N/A')}")
                        
                        # 이미지 첨부 확인
                        content_text = content.get('content', '')
                        image_count = content_text.count('![')
                        image_urls = []
                        
                        import re
                        image_matches = re.findall(r'!\[(.*?)\]\((.*?)\)', content_text)
                        
                        print(f"   📸 첨부된 이미지: {len(image_matches)}개")
                        
                        for j, (alt_text, url) in enumerate(image_matches, 1):
                            print(f"      {j}. {alt_text[:50]}...")
                            print(f"         URL: {url}")
                            
                            # 이미지 URL 유효성 검사
                            try:
                                img_response = await client.head(url, timeout=5.0)
                                if img_response.status_code == 200:
                                    print(f"         ✅ 이미지 접근 가능")
                                else:
                                    print(f"         ❌ 이미지 접근 불가 ({img_response.status_code})")
                            except Exception as img_error:
                                print(f"         ❌ 이미지 검증 실패: {img_error}")
                        
                        # 대표 이미지 확인
                        featured_image = content.get('featured_image', {})
                        if featured_image and featured_image.get('url'):
                            print(f"   🖼️ 대표 이미지: {featured_image.get('alt_text', 'N/A')}")
                            print(f"      사진작가: {featured_image.get('attribution', {}).get('photographer', 'N/A')}")
                            
                            # 대표 이미지 URL 검증
                            try:
                                featured_response = await client.head(featured_image['url'], timeout=5.0)
                                if featured_response.status_code == 200:
                                    print(f"      ✅ 대표 이미지 접근 가능")
                                else:
                                    print(f"      ❌ 대표 이미지 접근 불가 ({featured_response.status_code})")
                            except Exception as feat_error:
                                print(f"      ❌ 대표 이미지 검증 실패: {feat_error}")
                        
                        # 샘플 본문 출력 (처음 200자)
                        sample_content = content_text[:200].replace('\n', ' ')
                        print(f"   📄 본문 샘플: {sample_content}...")
                        
                    else:
                        print(f"❌ 실패: {result.get('message', 'Unknown error')}")
                        
                else:
                    print(f"❌ HTTP 오류: {response.status_code}")
                    print(f"   응답: {response.text[:200]}...")
                    
            except Exception as e:
                print(f"❌ 테스트 실패: {e}")
            
            print("-" * 40)
            
            # 테스트 간 잠시 대기
            if i < len(test_cases):
                await asyncio.sleep(2)
    
    print(f"\n🎉 모든 테스트 완료! ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")

def main():
    """메인 함수"""
    print("이미지 첨부 콘텐츠 생성 테스트")
    print("서버가 http://localhost:8000에서 실행 중인지 확인하세요.")
    print()
    
    try:
        asyncio.run(test_content_generation())
    except KeyboardInterrupt:
        print("\n\n⚠️ 테스트가 사용자에 의해 중단되었습니다.")
    except Exception as e:
        print(f"\n\n❌ 테스트 실행 중 오류 발생: {e}")

if __name__ == "__main__":
    main()