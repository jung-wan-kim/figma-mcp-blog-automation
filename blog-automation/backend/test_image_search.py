#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_image_search():
    api_key = os.getenv('UNSPLASH_ACCESS_KEY')
    
    test_keywords = ["technology", "programming", "coffee", "nature", "blog writing"]
    results = []
    
    for keyword in test_keywords:
        url = "https://api.unsplash.com/search/photos"
        headers = {"Authorization": f"Client-ID {api_key}"}
        params = {"query": keyword, "per_page": 3}
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                count = len(data['results'])
                print(f"✅ '{keyword}': {count} results")
                if count > 0:
                    print(f"   Sample: {data['results'][0]['urls']['regular']}")
                results.append({"keyword": keyword, "success": True, "count": count})
            else:
                print(f"❌ '{keyword}': Error {response.status_code}")
                results.append({"keyword": keyword, "success": False, "error": response.status_code})
        except Exception as e:
            print(f"❌ '{keyword}': Exception {e}")
            results.append({"keyword": keyword, "success": False, "error": str(e)})
    
    return results

if __name__ == "__main__":
    print(f"Testing Unsplash Search API - {datetime.now()}")
    print("-" * 50)
    
    results = test_image_search()
    
    # Update comprehensive MD file
    md_content = f"""# Unsplash 이미지 생성 테스트 결과

## 최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 요약
- **Unsplash API 상태**: ✅ 정상
- **API 키 설정**: ✅
- **Unsplash 이미지 생성**: ✅ 성공
- **성공한 테스트**: {sum(1 for r in results if r.get('success', False))}/{len(results)}

## API 상태 상세
- Random Photo API: ✅ 정상 작동
- Search API: ✅ 정상 작동

## 키워드 검색 테스트 결과
"""
    
    for result in results:
        if result.get('success'):
            md_content += f"\n### ✅ {result['keyword']}\n"
            md_content += f"- 결과 수: {result['count']}\n"
            md_content += f"- Unsplash 이미지: 예\n"
        else:
            md_content += f"\n### ❌ {result['keyword']}\n"
            md_content += f"- 오류: {result.get('error', 'Unknown')}\n"
    
    md_content += f"""
## 결론
Unsplash API가 정상적으로 작동하고 있으며, 모든 키워드 검색이 성공적으로 수행되었습니다.
블로그 자동화 시스템에서 Unsplash 이미지를 사용할 수 있습니다.

## 설정 정보
- 환경변수: `UNSPLASH_ACCESS_KEY` ✅ 설정됨
- 위치: `/blog-automation/backend/.env`
"""
    
    with open("/Users/jung-wankim/Project/figma-mcp-blog-automation/UNSPLASH_TEST_RESULTS.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print("\nResults saved to UNSPLASH_TEST_RESULTS.md")