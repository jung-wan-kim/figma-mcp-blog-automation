#!/usr/bin/env python3
"""
Unsplash 이미지 생성 자동 테스트 스크립트
이미지가 성공적으로 생성될 때까지 반복 테스트하고 결과를 MD 파일에 업데이트
"""

import asyncio
import sys
import os
import time
from datetime import datetime
import json
import aiohttp
from typing import List, Dict, Optional
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# 프로젝트 루트 경로 설정
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class UnsplashImageTester:
    def __init__(self):
        self.unsplash_access_key = os.getenv('UNSPLASH_ACCESS_KEY')
        self.test_results = []
        self.max_retries = 10  # 최대 10번 재시도
        self.retry_interval = 3  # 3초 간격
        self.test_keywords = [
            "technology",
            "programming",
            "coffee",
            "nature",
            "blog writing"
        ]
        
    async def test_image_search(self, keyword: str) -> Dict:
        """단일 키워드로 이미지 검색 테스트"""
        if not self.unsplash_access_key:
            return {
                "keyword": keyword,
                "success": False,
                "error": "UNSPLASH_ACCESS_KEY not set",
                "time": 0
            }
            
        try:
            start_time = time.time()
            async with aiohttp.ClientSession() as session:
                url = f"https://api.unsplash.com/search/photos"
                params = {
                    "query": keyword,
                    "per_page": 3
                }
                headers = {
                    "Authorization": f"Client-ID {self.unsplash_access_key}"
                }
                
                async with session.get(url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        results = data.get("results", [])
                        formatted_results = [{
                            "urls": {
                                "thumb": img["urls"]["thumb"],
                                "regular": img["urls"]["regular"],
                                "full": img["urls"]["full"]
                            },
                            "photographer": img["user"]["name"],
                            "source_url": img["links"]["html"],
                            "description": img.get("description", "")
                        } for img in results]
                        
                        end_time = time.time()
                        return {
                            "keyword": keyword,
                            "success": True,
                            "count": len(formatted_results),
                            "time": round(end_time - start_time, 2),
                            "has_unsplash": True,
                            "results": formatted_results[:1] if formatted_results else []
                        }
                    else:
                        error_text = await response.text()
                        return {
                            "keyword": keyword,
                            "success": False,
                            "error": f"Status {response.status}: {error_text}",
                            "time": round(time.time() - start_time, 2)
                        }
        except Exception as e:
            return {
                "keyword": keyword,
                "success": False,
                "error": str(e),
                "time": 0
            }
    
    async def test_content_suggestion(self) -> Dict:
        """콘텐츠 기반 이미지 제안 테스트"""
        keywords = ["python", "web scraping", "programming"]
        results = []
        
        start_time = time.time()
        for keyword in keywords:
            result = await self.test_image_search(keyword)
            if result.get("success") and result.get("results"):
                results.extend(result["results"])
        
        end_time = time.time()
        
        return {
            "test": "content_suggestion",
            "success": bool(results),
            "count": len(results),
            "time": round(end_time - start_time, 2),
            "has_unsplash": bool(results),
            "results": results[:1] if results else []
        }
    
    async def check_unsplash_api_status(self) -> Dict:
        """Unsplash API 상태 직접 확인"""
        if not self.unsplash_access_key:
            return {
                "api_key_set": False,
                "message": "UNSPLASH_ACCESS_KEY not configured"
            }
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {"Authorization": f"Client-ID {self.unsplash_access_key}"}
                async with session.get(
                    "https://api.unsplash.com/photos/random",
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    return {
                        "api_key_set": True,
                        "status_code": response.status,
                        "success": response.status == 200,
                        "headers": dict(response.headers) if response.status == 200 else None
                    }
        except Exception as e:
            return {
                "api_key_set": True,
                "success": False,
                "error": str(e)
            }
    
    async def run_full_test(self) -> Dict:
        """전체 테스트 실행"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 테스트 시작...")
        
        # API 상태 확인
        api_status = await self.check_unsplash_api_status()
        print(f"API 상태: {api_status}")
        
        # 키워드 검색 테스트
        search_results = []
        for keyword in self.test_keywords:
            result = await self.test_image_search(keyword)
            search_results.append(result)
            print(f"- '{keyword}' 검색: {'✅' if result['success'] else '❌'} "
                  f"({result.get('count', 0)}개 결과, {result['time']}초)")
        
        # 콘텐츠 제안 테스트
        content_result = await self.test_content_suggestion()
        print(f"- 콘텐츠 제안: {'✅' if content_result['success'] else '❌'} "
              f"({content_result.get('count', 0)}개 결과, {content_result['time']}초)")
        
        # Unsplash 이미지 확인
        has_unsplash = any(r.get("has_unsplash", False) for r in search_results) or \
                       content_result.get("has_unsplash", False)
        
        return {
            "timestamp": datetime.now().isoformat(),
            "api_status": api_status,
            "search_results": search_results,
            "content_result": content_result,
            "has_unsplash_images": has_unsplash,
            "summary": {
                "total_tests": len(search_results) + 1,
                "successful_tests": sum(1 for r in search_results if r["success"]) + \
                                   (1 if content_result["success"] else 0),
                "unsplash_working": has_unsplash
            }
        }
    
    def update_markdown_report(self, test_data: Dict):
        """테스트 결과를 마크다운 파일로 업데이트"""
        md_path = "/Users/jung-wankim/Project/figma-mcp-blog-automation/UNSPLASH_TEST_RESULTS.md"
        
        content = f"""# Unsplash 이미지 생성 테스트 결과

## 최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 요약
- **Unsplash API 상태**: {'✅ 정상' if test_data['api_status'].get('success', False) else '❌ 오류'}
- **API 키 설정**: {'✅' if test_data['api_status'].get('api_key_set', False) else '❌'}
- **Unsplash 이미지 생성**: {'✅ 성공' if test_data['has_unsplash_images'] else '❌ 실패 (기본 이미지 사용 중)'}
- **성공한 테스트**: {test_data['summary']['successful_tests']}/{test_data['summary']['total_tests']}

## API 상태 상세
```json
{json.dumps(test_data['api_status'], indent=2, ensure_ascii=False)}
```

## 키워드 검색 테스트 결과
"""
        
        for result in test_data['search_results']:
            status = '✅' if result['success'] else '❌'
            content += f"\n### {status} {result['keyword']}\n"
            content += f"- 결과 수: {result.get('count', 0)}\n"
            content += f"- 소요 시간: {result.get('time', 0)}초\n"
            content += f"- Unsplash 이미지: {'예' if result.get('has_unsplash', False) else '아니오'}\n"
            
            if result.get('results'):
                img = result['results'][0]
                content += f"- 샘플 이미지:\n"
                content += f"  - URL: {img.get('urls', {}).get('regular', 'N/A')}\n"
                content += f"  - 출처: {img.get('source_url', 'N/A')}\n"
                content += f"  - 작가: {img.get('photographer', 'N/A')}\n"
        
        content += f"\n## 콘텐츠 제안 테스트\n"
        content_result = test_data['content_result']
        status = '✅' if content_result['success'] else '❌'
        content += f"- 상태: {status}\n"
        content += f"- 결과 수: {content_result.get('count', 0)}\n"
        content += f"- 소요 시간: {content_result.get('time', 0)}초\n"
        content += f"- Unsplash 이미지: {'예' if content_result.get('has_unsplash', False) else '아니오'}\n"
        
        content += f"\n## 테스트 로그\n"
        content += f"- 테스트 실행 시간: {test_data['timestamp']}\n"
        content += f"- 총 재시도 횟수: {self.current_retry}/{self.max_retries}\n"
        
        if not test_data['has_unsplash_images']:
            content += f"\n## 🔧 문제 해결 방법\n"
            content += f"1. `.env` 파일에 `UNSPLASH_ACCESS_KEY` 환경 변수가 설정되어 있는지 확인\n"
            content += f"2. Unsplash 개발자 계정에서 유효한 Access Key를 발급받았는지 확인\n"
            content += f"3. API 사용량 제한에 도달하지 않았는지 확인\n"
            content += f"4. 네트워크 연결 상태 확인\n"
        
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n📄 테스트 결과가 {md_path}에 저장되었습니다.")
    
    async def run_with_retry(self):
        """성공할 때까지 재시도하며 테스트 실행"""
        self.current_retry = 0
        
        while self.current_retry < self.max_retries:
            self.current_retry += 1
            print(f"\n========== 시도 {self.current_retry}/{self.max_retries} ==========")
            
            test_result = await self.run_full_test()
            self.update_markdown_report(test_result)
            
            if test_result['has_unsplash_images']:
                print(f"\n✅ Unsplash 이미지 생성 성공!")
                print(f"총 {self.current_retry}번의 시도 후 성공했습니다.")
                return True
            
            if self.current_retry < self.max_retries:
                print(f"\n⏳ {self.retry_interval}초 후 재시도합니다...")
                await asyncio.sleep(self.retry_interval)
        
        print(f"\n❌ {self.max_retries}번의 시도 후에도 Unsplash 이미지를 생성하지 못했습니다.")
        return False

async def main():
    tester = UnsplashImageTester()
    success = await tester.run_with_retry()
    
    if success:
        print("\n🎉 테스트 완료! Unsplash 이미지가 정상적으로 생성됩니다.")
    else:
        print("\n⚠️  테스트 실패. UNSPLASH_TEST_RESULTS.md 파일을 확인하세요.")

if __name__ == "__main__":
    asyncio.run(main())