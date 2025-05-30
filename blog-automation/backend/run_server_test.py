#!/usr/bin/env python3
"""테스트용 서버 실행 스크립트 - 최소 설정"""

import os
import sys
from pathlib import Path

# 프로젝트 루트 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

# 필요한 환경변수 설정
os.environ.setdefault('DATABASE_URL', 'sqlite+aiosqlite:///./test.db')  # 임시로 SQLite 사용

if __name__ == "__main__":
    import uvicorn
    
    print("🚀 테스트 서버 시작 (SQLite 사용)...")
    print("주의: 이것은 테스트용입니다. 실제 운영에는 PostgreSQL/Supabase를 사용하세요.")
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )