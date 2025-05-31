'use client';

import { useState, useEffect } from 'react';
import { BlogPost } from '@/types';
import Navbar from '@/components/Navbar';

export default function PostsPage() {
  const [posts, setPosts] = useState<BlogPost[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/dashboard/posts`
      );
      if (!response.ok) {
        throw new Error('발행 내역을 가져올 수 없습니다');
      }
      const data = await response.json();
      setPosts(data.posts || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getPlatformIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'tistory':
        return '🟠';
      case 'wordpress':
        return '🟦';
      case 'naver':
        return '🟢';
      default:
        return '📝';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="bg-white p-6 rounded-lg border">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">오류 발생</h2>
            <p className="text-gray-600 mb-4">{error}</p>
            <button
              onClick={fetchPosts}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              다시 시도
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {posts.length === 0 ? (
          <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-12">
            <div className="text-center">
              <div className="text-6xl mb-4">📝</div>
              <a
                href="/create"
                className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
              >
                ✍️ 첫 글 작성하기
              </a>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">총 {posts.length}개</span>
            </div>

            {posts.map((post) => (
              <div
                key={post.id}
                className="bg-white shadow-sm rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg">
                          {getPlatformIcon(post.platform.platform_type)}
                        </span>
                        <span className="text-sm text-gray-500">{post.platform.name}</span>
                      </div>
                      <span className="text-xs text-gray-500">{formatDate(post.published_at)}</span>
                    </div>

                    <h2 className="text-lg font-semibold text-black mb-2">
                      <a 
                        href={`/posts/${post.id}`}
                        className="hover:text-blue-600 transition-colors"
                      >
                        {post.title}
                      </a>
                    </h2>

                    {/* HTML 콘텐츠를 텍스트로 변환해서 미리보기 표시 */}
                    {post.content && (
                      <p className="text-gray-600 text-sm mb-3 line-clamp-2">
                        {post.content.replace(/<[^>]*>/g, '').substring(0, 150)}...
                      </p>
                    )}

                    <div className="flex items-center justify-end text-sm text-gray-600 mt-3">
                      <div className="flex items-center space-x-3">
                        <a
                          href={`/posts/${post.id}`}
                          className="text-blue-600 hover:text-blue-800"
                        >
                          자세히 보기
                        </a>
                        {post.published_url && (
                          <a
                            href={post.published_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-gray-600 hover:text-gray-800"
                          >
                            원본 →
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
