#!/usr/bin/env python3
"""
기존 포스트들의 분리된 태그를 주제 형태로 마이그레이션
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import supabase_client
import structlog

logger = structlog.get_logger()

def migrate_tags():
    print("🔧 태그 마이그레이션 시작...")
    
    try:
        # 모든 포스트 가져오기
        posts_result = supabase_client.table('blog_posts').select("id, title, tags").execute()
        posts = posts_result.data or []
        
        if not posts:
            print("❌ 포스트가 없습니다.")
            return
        
        print(f"✅ {len(posts)}개 포스트 발견")
        
        migrated_count = 0
        
        for post in posts:
            post_id = post['id']
            title = post['title']
            tags = post.get('tags', [])
            
            # 태그가 없거나 이미 주제 형태인 경우 스킵
            if not tags:
                print(f"  ⏭️  '{title[:30]}...' - 태그 없음")
                continue
                
            # 태그가 1개이고 공백을 포함하는 경우 이미 마이그레이션된 것
            if len(tags) == 1 and ' ' in tags[0]:
                print(f"  ✓ '{title[:30]}...' - 이미 마이그레이션됨")
                continue
            
            # 분리된 태그들을 하나의 주제로 합치기
            # 짧은 조사나 단어는 제외하고 의미있는 단어들만 합치기
            meaningful_words = []
            for tag in tags:
                # 1글자 태그는 제외 (조사 등)
                if len(tag) > 1:
                    meaningful_words.append(tag)
            
            if meaningful_words:
                # 제목에서 주제 추출 시도
                # 또는 의미있는 단어들을 조합
                new_tag = ' '.join(meaningful_words)
                
                # 태그 업데이트
                update_result = supabase_client.table('blog_posts').update({
                    'tags': [new_tag]
                }).eq('id', post_id).execute()
                
                if update_result.data:
                    print(f"  ✅ '{title[:30]}...' - 태그 마이그레이션: {tags} → [{new_tag}]")
                    migrated_count += 1
                else:
                    print(f"  ❌ '{title[:30]}...' - 업데이트 실패")
            else:
                print(f"  ⏭️  '{title[:30]}...' - 의미있는 태그 없음")
        
        print(f"\n🎉 마이그레이션 완료! {migrated_count}개 포스트 업데이트됨")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")

if __name__ == "__main__":
    migrate_tags()