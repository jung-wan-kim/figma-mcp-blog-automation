#!/usr/bin/env python3
"""
Supabase 테이블 생성 스크립트
"""

import os
from supabase import create_client, Client
import sys

# Supabase 설정
SUPABASE_URL = "https://eupjjwgxrzxmddnumxyd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1cGpqd2d4cnp4bWRkbnVteHlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg1ODA2ODksImV4cCI6MjA2NDE1NjY4OX0.Z9-K6ktYOCGnAmV6cYWaYSu6HHwIuiWE0rV7ovDvVw8"

# Supabase 클라이언트 생성
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def check_table_exists(table_name: str) -> bool:
    """테이블 존재 여부 확인"""
    try:
        # 테이블에서 1개 행만 조회 시도
        response = supabase.table(table_name).select("*").limit(1).execute()
        print(f"✅ 테이블 '{table_name}' 존재함")
        return True
    except Exception as e:
        if "relation" in str(e) and "does not exist" in str(e):
            print(f"❌ 테이블 '{table_name}' 없음")
            return False
        else:
            print(f"⚠️  테이블 '{table_name}' 확인 중 오류: {e}")
            return False

def create_tables():
    """SQL 파일을 읽어서 테이블 생성"""
    sql_file_path = os.path.join(os.path.dirname(__file__), "database/schema.sql")
    
    # SQL 파일 읽기
    try:
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        print(f"✅ SQL 파일 읽기 완료: {sql_file_path}")
    except Exception as e:
        print(f"❌ SQL 파일 읽기 실패: {e}")
        return False
    
    # Supabase는 SQL을 직접 실행할 수 없으므로, 
    # 테이블이 없는 경우에만 안내 메시지 출력
    print("\n" + "="*60)
    print("📋 Supabase SQL Editor에서 실행해야 할 SQL:")
    print("="*60)
    print("\n1. Supabase 대시보드로 이동: https://app.supabase.com")
    print("2. 프로젝트 선택")
    print("3. 왼쪽 메뉴에서 'SQL Editor' 클릭")
    print("4. 'New query' 버튼 클릭")
    print("5. 아래 SQL을 복사하여 붙여넣고 'Run' 클릭")
    print("\n" + "-"*60)
    print(sql_content)
    print("-"*60 + "\n")
    
    return True

def test_connection():
    """Supabase 연결 테스트"""
    print("🔍 Supabase 연결 테스트 중...")
    
    tables_to_check = [
        "blog_platforms",
        "blog_posts",
        "content_requests",
        "analytics_data",
        "images",
        "publication_history"
    ]
    
    existing_tables = []
    missing_tables = []
    
    for table in tables_to_check:
        if check_table_exists(table):
            existing_tables.append(table)
        else:
            missing_tables.append(table)
    
    print("\n" + "="*60)
    print("📊 테이블 상태 요약:")
    print("="*60)
    
    if existing_tables:
        print(f"\n✅ 존재하는 테이블 ({len(existing_tables)}개):")
        for table in existing_tables:
            print(f"   - {table}")
    
    if missing_tables:
        print(f"\n❌ 없는 테이블 ({len(missing_tables)}개):")
        for table in missing_tables:
            print(f"   - {table}")
        
        print("\n⚠️  위 테이블들을 생성해야 합니다!")
        create_tables()
    else:
        print("\n🎉 모든 테이블이 이미 생성되어 있습니다!")
    
    # 샘플 데이터 추가 옵션
    if existing_tables and "blog_platforms" in existing_tables:
        print("\n💡 샘플 데이터를 추가하시겠습니까? (y/n): ", end="")
        if input().lower() == 'y':
            add_sample_data()

def add_sample_data():
    """샘플 데이터 추가"""
    try:
        # 샘플 플랫폼 추가
        sample_platform = {
            "name": "테스트 티스토리 블로그",
            "platform_type": "tistory",
            "url": "https://test.tistory.com",
            "username": "testuser",
            "post_count": 0,
            "total_views": 0,
            "total_likes": 0
        }
        
        # 중복 확인
        existing = supabase.table("blog_platforms").select("*").eq("url", sample_platform["url"]).execute()
        
        if not existing.data:
            response = supabase.table("blog_platforms").insert(sample_platform).execute()
            if response.data:
                print("✅ 샘플 플랫폼 추가 완료")
                platform_id = response.data[0]['id']
                
                # 샘플 게시물 추가
                sample_post = {
                    "platform_id": platform_id,
                    "title": "AI가 작성한 첫 번째 테스트 포스트",
                    "content": "이것은 블로그 자동화 시스템의 테스트 포스트입니다. Supabase와 연동되어 자동으로 저장되었습니다.",
                    "meta_description": "AI 블로그 자동화 테스트",
                    "status": "published",
                    "published_url": "https://test.tistory.com/1",
                    "views": 100,
                    "likes": 10,
                    "comments": 5,
                    "tags": ["AI", "자동화", "테스트"]
                }
                
                post_response = supabase.table("blog_posts").insert(sample_post).execute()
                if post_response.data:
                    print("✅ 샘플 게시물 추가 완료")
                else:
                    print("❌ 샘플 게시물 추가 실패")
        else:
            print("ℹ️  샘플 플랫폼이 이미 존재합니다")
            
    except Exception as e:
        print(f"❌ 샘플 데이터 추가 중 오류: {e}")

if __name__ == "__main__":
    print("🚀 Supabase 테이블 생성 도구")
    print("="*60)
    print(f"URL: {SUPABASE_URL}")
    print(f"Key: {SUPABASE_KEY[:20]}...")
    print("="*60 + "\n")
    
    test_connection()