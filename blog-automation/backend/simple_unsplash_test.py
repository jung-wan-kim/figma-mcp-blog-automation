#!/usr/bin/env python3
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def test_unsplash():
    api_key = os.getenv('UNSPLASH_ACCESS_KEY')
    print(f"API Key: {api_key[:10]}..." if api_key else "API Key not found")
    
    if not api_key:
        return False, "API key not configured"
    
    # Simple GET request
    url = "https://api.unsplash.com/photos/random"
    headers = {"Authorization": f"Client-ID {api_key}"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Photo URL: {data['urls']['regular']}")
            return True, data['urls']['regular']
        else:
            print(f"Error: {response.text}")
            return False, response.text
            
    except Exception as e:
        print(f"Exception: {e}")
        return False, str(e)

if __name__ == "__main__":
    print(f"Testing Unsplash API - {datetime.now()}")
    print("-" * 50)
    
    success, result = test_unsplash()
    
    # Update MD file
    md_content = f"""# Unsplash 이미지 생성 테스트 결과

## 최종 업데이트: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 요약
- **Unsplash API 상태**: {'✅ 정상' if success else '❌ 오류'}
- **API 키 설정**: {'✅' if os.getenv('UNSPLASH_ACCESS_KEY') else '❌'}
- **Unsplash 이미지 생성**: {'✅ 성공' if success else '❌ 실패'}

## 테스트 결과
"""
    
    if success:
        md_content += f"""
✅ **테스트 성공!**

- API 응답: 200 OK
- 이미지 URL: {result}
- Unsplash API가 정상적으로 작동합니다.
"""
    else:
        md_content += f"""
❌ **테스트 실패**

- 오류: {result}
- API 키를 확인하거나 네트워크 연결을 점검하세요.
"""
    
    with open("/Users/jung-wankim/Project/figma-mcp-blog-automation/UNSPLASH_TEST_RESULTS.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"\n{'✅ Success!' if success else '❌ Failed'}")
    print("Results saved to UNSPLASH_TEST_RESULTS.md")