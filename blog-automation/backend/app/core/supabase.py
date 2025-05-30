from supabase import create_client, Client
import os
from typing import Optional

# Supabase 설정
SUPABASE_URL = "https://eupjjwgxrzxmddnumxyd.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImV1cGpqd2d4cnp4bWRkbnVteHlkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg1ODA2ODksImV4cCI6MjA2NDE1NjY4OX0.Z9-K6ktYOCGnAmV6cYWaYSu6HHwIuiWE0rV7ovDvVw8"

# Supabase 클라이언트 생성
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase_client() -> Client:
    """Supabase 클라이언트를 반환합니다."""
    return supabase