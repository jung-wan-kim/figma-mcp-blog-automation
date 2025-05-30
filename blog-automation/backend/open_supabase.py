#!/usr/bin/env python3
"""
Supabase SQL Editor 열기
"""

import webbrowser
import os
import time

# Supabase SQL Editor URL
SQL_EDITOR_URL = "https://supabase.com/dashboard/project/eupjjwgxrzxmddnumxyd/sql/new"

# SQL 파일 경로
SQL_FILE = os.path.join(os.path.dirname(__file__), "create_all_tables.sql")

def open_supabase_and_guide():
    """Supabase SQL Editor를 열고 가이드 제공"""
    
    print("🚀 Supabase SQL Editor를 여는 중...")
    print("="*60)
    
    # 브라우저에서 Supabase 열기
    webbrowser.open(SQL_EDITOR_URL)
    
    print("\n✅ 브라우저에서 Supabase SQL Editor가 열렸습니다.")
    print("\n📋 다음 단계를 따라주세요:\n")
    
    print("1. GitHub 계정으로 로그인 (필요한 경우)")
    print("2. SQL Editor가 열리면 기존 내용을 모두 지우기")
    print("3. 아래 파일의 내용을 복사하여 붙여넣기:")
    print(f"   {SQL_FILE}")
    print("4. 'Run' 버튼 클릭하여 실행")
    print("5. 성공 메시지 확인")
    
    print("\n" + "="*60)
    print("📄 SQL 내용:")
    print("="*60)
    
    # SQL 파일 내용 출력
    try:
        with open(SQL_FILE, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print(sql_content)
    except Exception as e:
        print(f"❌ SQL 파일 읽기 실패: {e}")
    
    print("="*60)
    
    # 테이블 생성 후 확인
    print("\n⏳ 테이블 생성을 기다리는 중...")
    print("테이블 생성이 완료되면 Enter를 눌러주세요...")
    input()
    
    # 테이블 확인 스크립트 실행
    print("\n🔍 테이블 생성 확인 중...")
    os.system(f"cd {os.path.dirname(__file__)} && source venv/bin/activate && python create_tables.py")

if __name__ == "__main__":
    open_supabase_and_guide()