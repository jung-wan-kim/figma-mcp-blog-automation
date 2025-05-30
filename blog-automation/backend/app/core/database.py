"""
Supabase 데이터베이스 연결 설정
SQLAlchemy 대신 Supabase Python 클라이언트 사용
"""

from supabase import create_client, Client
from app.core.config import settings
from app.core.supabase import get_supabase_client

# Supabase 클라이언트 가져오기
supabase_client = get_supabase_client()

# 기존 코드 호환성을 위한 함수
async def get_db() -> Client:
    """Supabase 클라이언트를 반환합니다."""
    return supabase_client

# SQLAlchemy Base 대체 (필요한 경우)
class Base:
    """SQLAlchemy Base 대체 클래스"""
    pass