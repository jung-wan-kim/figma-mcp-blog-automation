'use client';

import { useState } from 'react';
import { BlogPost } from '@/types';
import PostPreviewModal from './PostPreviewModal';

interface RecentPostsProps {
  posts: BlogPost[];
}

export default function RecentPosts({ posts }: RecentPostsProps) {
  const [selectedPost, setSelectedPost] = useState<BlogPost | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const handlePostClick = (post: BlogPost) => {
    setSelectedPost(post);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setTimeout(() => setSelectedPost(null), 300);
  };
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
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

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">최근 발행된 글</h3>
        <p className="mt-1 text-sm text-gray-500">최근에 생성되고 발행된 블로그 포스트</p>
      </div>

      <div className="px-6 py-4">
        {posts.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">📝</div>
            <p className="text-gray-500">발행된 글이 없습니다</p>
            <p className="text-sm text-gray-400 mt-2">첫 번째 블로그 글을 생성해보세요</p>
          </div>
        ) : (
          <div className="space-y-4">
            {posts.map((post) => (
              <div
                key={post.id}
                className="border border-gray-200 rounded-lg p-4 hover:bg-gray-50 transition-colors cursor-pointer"
                onClick={() => handlePostClick(post)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-medium text-gray-900 truncate hover:text-blue-600 transition-colors">{post.title}</h4>
                    <p className="mt-1 text-sm text-gray-500">
                      {post.blog_platforms?.name || post.platform?.name || '알 수 없는 플랫폼'} •{' '}
                      {formatDate(post.published_at || post.created_at)}
                    </p>
                  </div>

                  <div className="flex flex-col items-end space-y-2">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(post.status)}`}
                    >
                      {getStatusText(post.status)}
                    </span>

                    {post.published_url && (
                      <a
                        href={post.published_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                      >
                        글 보기 →
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      
      {/* 미리보기 모달 */}
      <PostPreviewModal
        post={selectedPost}
        isOpen={isModalOpen}
        onClose={handleCloseModal}
      />
    </div>
  );
}
