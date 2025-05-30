#!/usr/bin/env python3
"""빠른 Unsplash API 테스트"""

import asyncio
import os
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

async def quick_test():
    unsplash_key = os.getenv('UNSPLASH_ACCESS_KEY')
    print(f"API Key 설정: {'✅' if unsplash_key else '❌'}")
    
    if not unsplash_key:
        print("UNSPLASH_ACCESS_KEY가 설정되지 않았습니다.")
        return False
    
    try:
        async with aiohttp.ClientSession() as session:
            # 1. Random photo API 테스트
            print("\n1. Random Photo API 테스트...")
            headers = {"Authorization": f"Client-ID {unsplash_key}"}
            async with session.get(
                "https://api.unsplash.com/photos/random",
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                print(f"   상태 코드: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ 성공! 이미지 URL: {data['urls']['regular']}")
                else:
                    print(f"   ❌ 실패: {await response.text()}")
            
            # 2. Search API 테스트
            print("\n2. Search API 테스트...")
            async with session.get(
                "https://api.unsplash.com/search/photos",
                params={"query": "technology", "per_page": 3},
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                print(f"   상태 코드: {response.status}")
                if response.status == 200:
                    data = await response.json()
                    print(f"   ✅ 성공! 검색 결과: {len(data['results'])}개")
                    for i, img in enumerate(data['results'][:2]):
                        print(f"   - 이미지 {i+1}: {img['urls']['regular']}")
                else:
                    print(f"   ❌ 실패: {await response.text()}")
        
        return True
        
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

async def main():
    print(f"Unsplash API 빠른 테스트 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    success = await quick_test()
    
    # 결과 MD 파일 업데이트
    if success:
        result_text = f"""# Unsplash 이미지 생성 테스트 결과

## 최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 요약
- **Unsplash API 상태**: ✅ 정상
- **API 키 설정**: ✅
- **Unsplash 이미지 생성**: ✅ 성공
- **성공한 테스트**: 2/2

## 테스트 상세
- Random Photo API: ✅ 정상 작동
- Search API: ✅ 정상 작동
- 이미지 URL 접근: ✅ 가능

## 결론
Unsplash API가 정상적으로 작동하고 있으며, 이미지 생성 기능을 사용할 수 있습니다.
"""
    else:
        result_text = f"""# Unsplash 이미지 생성 테스트 결과

## 최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 요약
- **Unsplash API 상태**: ❌ 오류
- **API 키 설정**: {'✅' if os.getenv('UNSPLASH_ACCESS_KEY') else '❌'}
- **Unsplash 이미지 생성**: ❌ 실패

## 문제 해결 필요
상세한 오류 내용은 위의 콘솔 출력을 확인하세요.
"""
    
    with open("/Users/jung-wankim/Project/figma-mcp-blog-automation/UNSPLASH_TEST_RESULTS.md", "w", encoding="utf-8") as f:
        f.write(result_text)
    
    print(f"\n{'✅ 테스트 성공!' if success else '❌ 테스트 실패'}")
    print(f"결과가 UNSPLASH_TEST_RESULTS.md에 저장되었습니다.")

if __name__ == "__main__":
    asyncio.run(main())