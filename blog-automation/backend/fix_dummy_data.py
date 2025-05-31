#!/usr/bin/env python3
"""
더미 데이터를 실제 데이터로 변환하는 스크립트
blog_posts 테이블의 platform_id를 업데이트하고 더미 통계를 제거
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import supabase_client
import random

def fix_dummy_data():
    print("🔧 더미 데이터 수정 시작...")
    
    try:
        # 1. 플랫폼 정보 가져오기
        platforms_result = supabase_client.table('blog_platforms').select("*").execute()
        platforms = platforms_result.data or []
        
        if not platforms:
            print("❌ 플랫폼 데이터가 없습니다.")
            return
        
        print(f"✅ {len(platforms)}개 플랫폼 발견:")
        for platform in platforms:
            print(f"  - {platform['name']} ({platform['id']})")
        
        # 2. blog_posts에서 platform_id가 None인 포스트들 가져오기
        posts_result = supabase_client.table('blog_posts').select("*").is_("platform_id", None).execute()
        posts_without_platform = posts_result.data or []
        
        print(f"📝 platform_id가 없는 포스트: {len(posts_without_platform)}개")
        
        # 3. 각 포스트에 platform_id 할당
        for i, post in enumerate(posts_without_platform):
            # 플랫폼을 순환하며 할당
            platform = platforms[i % len(platforms)]
            platform_id = platform['id']
            
            # 포스트 업데이트
            update_result = supabase_client.table('blog_posts').update({
                'platform_id': platform_id
            }).eq('id', post['id']).execute()
            
            if update_result.data:
                print(f"  ✅ 포스트 '{post['title'][:30]}...' → {platform['name']}")
            else:
                print(f"  ❌ 포스트 '{post['title'][:30]}...' 업데이트 실패")
        
        # 4. 각 플랫폼별 실제 통계 계산 및 업데이트
        print("\n📊 플랫폼별 통계 계산 중...")
        
        for platform in platforms:
            platform_id = platform['id']
            
            # 해당 플랫폼의 실제 포스트들
            platform_posts_result = supabase_client.table('blog_posts').select(
                "views, likes, comments"
            ).eq('platform_id', platform_id).execute()
            
            if platform_posts_result.data:
                total_views = sum(post.get('views', 0) for post in platform_posts_result.data)
                total_likes = sum(post.get('likes', 0) for post in platform_posts_result.data)
                post_count = len(platform_posts_result.data)
                
                # 플랫폼 통계 업데이트
                platform_update_result = supabase_client.table('blog_platforms').update({
                    'post_count': post_count,
                    'total_views': total_views,
                    'total_likes': total_likes
                }).eq('id', platform_id).execute()
                
                if platform_update_result.data:
                    print(f"  ✅ {platform['name']}: {post_count}개 포스트, {total_views} 조회수, {total_likes} 좋아요")
                else:
                    print(f"  ❌ {platform['name']} 통계 업데이트 실패")
            else:
                print(f"  📭 {platform['name']}: 포스트 없음")
        
        print("\n🎉 더미 데이터 수정 완료!")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    fix_dummy_data()