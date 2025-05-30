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
      const response = await fetch('/api/dashboard/posts');
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

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'published':
        return 'bg-green-100 text-green-800';
      case 'draft':
        return 'bg-gray-100 text-gray-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-blue-100 text-blue-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status.toLowerCase()) {
      case 'published':
        return '발행 완료';
      case 'draft':
        return '임시저장';
      case 'failed':
        return '발행 실패';
      default:
        return status;
    }
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
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">📝 발행 내역</h1>
          <p className="mt-2 text-gray-600">
            지금까지 생성되고 발행된 모든 블로그 포스트를 확인하세요
          </p>
        </div>

        {posts.length === 0 ? (
          <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-12">
            <div className="text-center">
              <div className="text-6xl mb-4">📝</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">발행된 글이 없습니다</h3>
              <p className="text-gray-500 mb-6">
                첫 번째 블로그 글을 생성해서 자동화된 콘텐츠 발행을 경험해보세요
              </p>
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
            <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-4">
              <div className="text-sm text-gray-600">
                총 <span className="font-semibold text-gray-900">{posts.length}개</span>의 글이
                발행되었습니다
              </div>
            </div>

            {posts.map((post) => (
              <div
                key={post.id}
                className="bg-white shadow-sm rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-lg">
                        {getPlatformIcon(post.platform.platform_type)}
                      </span>
                      <span className="text-sm text-gray-500">{post.platform.name}</span>
                      <span
                        className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(post.status)}`}
                      >
                        {getStatusText(post.status)}
                      </span>
                    </div>

                    <h2 className="text-xl font-semibold text-gray-900 mb-2">{post.title}</h2>

                    <p className="text-sm text-gray-500 mb-4">
                      발행일: {formatDate(post.published_at)}
                    </p>

                    <div className="flex items-center space-x-6 text-sm text-gray-500">
                      <div className="flex items-center space-x-1">
                        <span>👀</span>
                        <span>{post.views.toLocaleString()} 조회</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span>❤️</span>
                        <span>{post.likes.toLocaleString()} 좋아요</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <span>💬</span>
                        <span>{post.comments.toLocaleString()} 댓글</span>
                      </div>
                    </div>
                  </div>

                  <div className="flex flex-col items-end space-y-2 ml-4">
                    {post.published_url && (
                      <a
                        href={post.published_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center px-3 py-2 bg-blue-50 text-blue-700 rounded-md hover:bg-blue-100 text-sm font-medium"
                      >
                        글 보기 →
                      </a>
                    )}

                    <div className="text-xs text-gray-400">ID: {post.id}</div>
                  </div>
                </div>

                {/* 콘텐츠 미리보기 (접기/펼치기 가능하도록 추후 개선 가능) */}
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <details className="group">
                    <summary className="cursor-pointer text-sm text-gray-600 hover:text-gray-800">
                      콘텐츠 미리보기 보기
                    </summary>
                    <div className="mt-3 text-sm text-gray-700 bg-gray-50 p-4 rounded max-h-40 overflow-y-auto">
                      <div
                        dangerouslySetInnerHTML={{ __html: post.content.substring(0, 500) + '...' }}
                      />
                    </div>
                  </details>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
