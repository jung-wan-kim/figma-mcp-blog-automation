#!/usr/bin/env python3
"""Supabase 연결 테스트 스크립트"""

import asyncio
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()

def test_supabase_connection():
    """Supabase 연결 테스트"""
    print(f"\n{'='*50}")
    print(f"Supabase 연결 테스트 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}\n")
    
    # 환경변수에서 읽기
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    # 하드코딩된 값 (대체용)
    if not supabase_url:
        supabase_url = "https://eupjjwgxrzxmddnumxyd.supabase.co"
    if not supabase_key:
        supabase_key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1cGpqd2d4cnp4bWRkbnVteHlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg1ODA2ODksImV4cCI6MjA2NDE1NjY4OX0.Z9-K6ktYOCGnAmV6cYWaYSu6HHwIuiWE0rV7ovDvVw8"
    
    print(f"1. 설정 확인:")
    print(f"   - Supabase URL: {supabase_url}")
    print(f"   - Supabase Key: {supabase_key[:20]}...")
    
    try:
        # Supabase 클라이언트 생성
        print(f"\n2. Supabase 클라이언트 생성 중...")
        supabase: Client = create_client(supabase_url, supabase_key)
        print(f"   ✅ 클라이언트 생성 성공!")
        
        # 테이블 목록 확인
        print(f"\n3. 테이블 확인:")
        tables_to_check = ['users', 'contents', 'blog_accounts', 'publications', 'blog_platforms']
        
        for table in tables_to_check:
            try:
                # 각 테이블에서 count 실행
                result = supabase.table(table).select("*", count='exact').limit(0).execute()
                count = result.count
                print(f"   - {table}: ✅ 존재 (레코드 수: {count})")
            except Exception as e:
                error_msg = str(e)
                if "relation" in error_msg and "does not exist" in error_msg:
                    print(f"   - {table}: ❌ 테이블이 존재하지 않음")
                else:
                    print(f"   - {table}: ❌ 오류: {error_msg}")
        
        # Auth 테스트
        print(f"\n4. Authentication 테스트:")
        try:
            # 현재 세션 확인
            session = supabase.auth.get_session()
            if session:
                print(f"   ✅ Auth 연결 성공")
            else:
                print(f"   ℹ️  Auth 연결 성공 (세션 없음)")
        except Exception as e:
            print(f"   ❌ Auth 오류: {e}")
        
        # Storage 버킷 확인
        print(f"\n5. Storage 버킷 확인:")
        try:
            buckets = supabase.storage.list_buckets()
            if buckets:
                print(f"   ✅ Storage 연결 성공")
                for bucket in buckets:
                    print(f"      - {bucket['name']}")
            else:
                print(f"   ℹ️  Storage 연결 성공 (버킷 없음)")
        except Exception as e:
            print(f"   ❌ Storage 오류: {e}")
        
        print(f"\n{'='*50}")
        print(f"✅ Supabase 연결 테스트 완료!")
        print(f"{'='*50}\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Supabase 연결 실패!")
        print(f"오류: {e}")
        print(f"{'='*50}\n")
        return False

def test_create_sample_data():
    """샘플 데이터 생성 테스트"""
    print(f"\n샘플 데이터 생성 테스트...")
    
    supabase_url = os.getenv('SUPABASE_URL', "https://eupjjwgxrzxmddnumxyd.supabase.co")
    supabase_key = os.getenv('SUPABASE_KEY', "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1cGpqd2d4cnp4bWRkbnVteHlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg1ODA2ODksImV4cCI6MjA2NDE1NjY4OX0.Z9-K6ktYOCGnAmV6cYWaYSu6HHwIuiWE0rV7ovDvVw8")
    
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # blog_platforms 테이블에 샘플 데이터 추가 시도
        sample_platform = {
            "name": "WordPress",
            "slug": "wordpress",
            "description": "Popular blogging platform",
            "is_active": True
        }
        
        result = supabase.table('blog_platforms').insert(sample_platform).execute()
        print(f"✅ 샘플 데이터 생성 성공: {result.data}")
        
    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg:
            print(f"ℹ️  샘플 데이터가 이미 존재합니다")
        else:
            print(f"❌ 샘플 데이터 생성 실패: {error_msg}")

if __name__ == "__main__":
    # Supabase 연결 테스트
    success = test_supabase_connection()
    
    # 연결 성공 시 샘플 데이터 테스트
    if success:
        test_create_sample_data()