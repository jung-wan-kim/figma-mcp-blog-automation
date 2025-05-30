#!/usr/bin/env python3
"""Supabase 데이터베이스 URL 생성 도우미"""

print("""
Supabase PostgreSQL 연결 정보:

1. Supabase 대시보드에서 Database Settings 확인:
   https://supabase.com/dashboard/project/eupjjwgxrzxmddnumxyd/settings/database

2. Connection string 형식:
   postgresql://postgres:[YOUR-PASSWORD]@db.eupjjwgxrzxmddnumxyd.supabase.co:5432/postgres

3. .env 파일에 추가할 내용:
   DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.eupjjwgxrzxmddnumxyd.supabase.co:5432/postgres

또는 Supabase Python 클라이언트를 직접 사용하는 방법도 있습니다.
현재 SUPABASE_URL과 SUPABASE_KEY가 이미 설정되어 있으므로,
SQLAlchemy 대신 Supabase 클라이언트를 사용하는 것도 좋은 방법입니다.
""")