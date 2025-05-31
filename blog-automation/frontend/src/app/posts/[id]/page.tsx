'use client';

import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';

interface BlogPost {
  id: string;
  title: string;
  content: string;
  meta_description: string;
  platform: {
    name: string;
    platform_type: string;
    url: string;
  };
  published_url: string;
  status: string;
  views: number;
  likes: number;
  comments: number;
  tags: string[];
  featured_image_url?: string;
  published_at: string;
  created_at: string;
}

export default function PostDetailPage() {
  const params = useParams();
  const router = useRouter();
  const [post, setPost] = useState<BlogPost | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (params.id) {
      fetchPost(params.id as string);
    }
  }, [params.id]);

  const fetchPost = async (postId: string) => {
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/dashboard/posts`
      );
      
      if (!response.ok) {
        throw new Error('포스트를 가져올 수 없습니다');
      }
      
      const data = await response.json();
      const foundPost = data.posts.find((p: BlogPost) => p.id === postId);
      
      if (!foundPost) {
        throw new Error('포스트를 찾을 수 없습니다');
      }
      
      setPost(foundPost);
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
      month: 'long',
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
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse">
            <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-8"></div>
            <div className="space-y-3">
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded"></div>
              <div className="h-4 bg-gray-200 rounded w-5/6"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (error || !post) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">오류 발생</h2>
            <p className="text-gray-600 mb-4">{error || '포스트를 찾을 수 없습니다'}</p>
            <button
              onClick={() => router.push('/posts')}
              className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              목록으로 돌아가기
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <article className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 헤더 정보 */}
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <span className="text-xl">{getPlatformIcon(post.platform.platform_type)}</span>
              <span className="text-gray-600">{post.platform.name}</span>
            </div>
            <span className="text-sm text-gray-500">{formatDate(post.published_at)}</span>
          </div>

          <h1 className="text-3xl font-bold text-gray-900 mb-4">{post.title}</h1>

          {post.published_url && (
            <div className="mt-3">
              <a
                href={post.published_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                원본 글 보기 →
              </a>
            </div>
          )}

          {/* 태그 */}
          {post.tags && post.tags.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {post.tags.map((tag, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                >
                  #{tag}
                </span>
              ))}
            </div>
          )}
        </div>

        {/* 대표 이미지 */}
        {post.featured_image_url && (
          <div className="mb-6">
            <img
              src={post.featured_image_url}
              alt={post.title}
              className="w-full h-auto rounded-lg shadow-sm"
            />
          </div>
        )}

        {/* 본문 내용 */}
        <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-8">
          <div 
            className="prose prose-lg max-w-none"
            dangerouslySetInnerHTML={{ __html: post.content }}
          />
        </div>

        {/* 하단 액션 버튼 */}
        <div className="mt-6 flex justify-between items-center">
          <button
            onClick={() => router.push('/posts')}
            className="text-gray-600 hover:text-gray-800 flex items-center"
          >
            ← 목록으로
          </button>
          
          <div className="flex space-x-3">
            <button
              onClick={() => navigator.clipboard.writeText(window.location.href)}
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
            >
              링크 복사
            </button>
            {post.published_url && (
              <a
                href={post.published_url}
                target="_blank"
                rel="noopener noreferrer"
                className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
              >
                원본 보기
              </a>
            )}
          </div>
        </div>
      </article>
    </div>
  );
}