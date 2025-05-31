'use client';

import { BlogPost } from '@/types';
import { useEffect } from 'react';

interface PostPreviewModalProps {
  post: BlogPost | null;
  isOpen: boolean;
  onClose: () => void;
}

export default function PostPreviewModal({ post, isOpen, onClose }: PostPreviewModalProps) {
  // ESC 키로 닫기
  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    
    if (isOpen) {
      document.addEventListener('keydown', handleEsc);
      // 배경 스크롤 방지
      document.body.style.overflow = 'hidden';
    }
    
    return () => {
      document.removeEventListener('keydown', handleEsc);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose]);

  if (!isOpen || !post) return null;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('ko-KR', {
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

  return (
    <>
      {/* 백드롭 */}
      <div
        className="fixed inset-0 bg-black bg-opacity-50 z-40 transition-opacity"
        onClick={onClose}
      />
      
      {/* 모달 */}
      <div 
        className="fixed inset-0 z-50 overflow-y-auto"
        onClick={onClose}
      >
        <div 
          className="flex min-h-full items-center justify-center p-4"
          onClick={onClose}
        >
          <div
            className="relative w-full max-w-4xl bg-white rounded-lg shadow-xl"
            onClick={(e) => e.stopPropagation()}
          >
            {/* 헤더 */}
            <div className="flex items-center justify-between p-6 border-b">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">
                  {getPlatformIcon(post.platform?.platform_type || post.blog_platforms?.platform_type || 'blog')}
                </span>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{post.title}</h2>
                  <p className="text-sm text-gray-500 mt-1">
                    {post.platform?.name || post.blog_platforms?.name || '알 수 없는 플랫폼'} · {formatDate(post.published_at || post.created_at)}
                  </p>
                </div>
              </div>
              
              <button
                onClick={onClose}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {/* 통계 */}
            <div className="flex items-center space-x-6 px-6 py-4 bg-gray-50 border-b">
              <div className="flex items-center space-x-2">
                <span className="text-gray-600">👀</span>
                <span className="font-medium">{post.views.toLocaleString()}</span>
                <span className="text-sm text-gray-500">조회</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-gray-600">❤️</span>
                <span className="font-medium">{post.likes.toLocaleString()}</span>
                <span className="text-sm text-gray-500">좋아요</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-gray-600">💬</span>
                <span className="font-medium">{post.comments.toLocaleString()}</span>
                <span className="text-sm text-gray-500">댓글</span>
              </div>
            </div>
            
            {/* 본문 */}
            <div className="p-6 max-h-[60vh] overflow-y-auto">
              {post.content ? (
                <div 
                  className="prose prose-sm max-w-none"
                  style={{
                    lineHeight: '1.6',
                    color: '#000000'
                  }}
                >
                  {post.content.split('\n').map((line, index) => {
                    // 마크다운 이미지 패턴 감지: ![alt](url)
                    const imageMatch = line.match(/^!\[(.*?)\]\((.*?)\)$/);
                    if (imageMatch) {
                      const [, altText, imageUrl] = imageMatch;
                      return (
                        <div key={index} className="my-4">
                          <img
                            src={imageUrl}
                            alt={altText}
                            className="w-full h-64 object-cover rounded-lg border border-gray-300"
                            onError={(e) => {
                              // 이미지 로딩 실패시 placeholder 표시
                              e.currentTarget.src = 'https://via.placeholder.com/800x400/f0f0f0/666666?text=Image+Not+Available';
                            }}
                          />
                        </div>
                      );
                    }
                    
                    // 이미지 캡션 감지: *텍스트*
                    if (line.match(/^\*.*\*$/)) {
                      return (
                        <div key={index} className="text-xs text-gray-600 text-center italic mb-4">
                          {line.replace(/^\*|\*$/g, '')}
                        </div>
                      );
                    }
                    
                    // 헤딩 감지
                    if (line.startsWith('## ')) {
                      return (
                        <h4 key={index} className="text-lg font-semibold text-black mt-6 mb-3">
                          {line.replace('## ', '')}
                        </h4>
                      );
                    }
                    
                    if (line.startsWith('### ')) {
                      return (
                        <h5 key={index} className="text-base font-medium text-black mt-4 mb-2">
                          {line.replace('### ', '')}
                        </h5>
                      );
                    }
                    
                    // 리스트 아이템 감지
                    if (line.match(/^\d+\. /)) {
                      return (
                        <div key={index} className="ml-4 mb-1">
                          {line}
                        </div>
                      );
                    }
                    
                    // 불릿 리스트 감지
                    if (line.match(/^- /)) {
                      return (
                        <div key={index} className="ml-4 mb-1">
                          • {line.substring(2)}
                        </div>
                      );
                    }
                    
                    // 볼드 텍스트 처리
                    if (line.includes('**')) {
                      const parts = line.split(/(\*\*.*?\*\*)/);
                      return (
                        <p key={index} className="mb-2">
                          {parts.map((part, i) => 
                            part.startsWith('**') && part.endsWith('**') ? (
                              <strong key={i}>{part.slice(2, -2)}</strong>
                            ) : (
                              part
                            )
                          )}
                        </p>
                      );
                    }
                    
                    // 일반 텍스트 (빈 줄 제외)
                    if (line.trim()) {
                      return (
                        <p key={index} className="mb-2">
                          {line}
                        </p>
                      );
                    }
                    
                    // 빈 줄
                    return <br key={index} />;
                  })}
                </div>
              ) : (
                <div className="text-gray-500 italic">
                  본문 내용을 불러올 수 없습니다.
                </div>
              )}
            </div>
            
            {/* 태그 */}
            {post.tags && post.tags.length > 0 && (
              <div className="px-6 py-4 border-t bg-gray-50">
                <div className="flex flex-wrap gap-2">
                  {post.tags.map((tag, index) => (
                    <span
                      key={index}
                      className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {/* 액션 버튼 */}
            <div className="flex items-center justify-between p-6 border-t bg-gray-50">
              <div className="flex items-center space-x-3">
                {post.published_url && (
                  <a
                    href={post.published_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:text-blue-800 font-medium flex items-center"
                  >
                    원본 글 보기
                    <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                  </a>
                )}
              </div>
              
              <button
                onClick={onClose}
                className="px-4 py-2 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 transition-colors"
              >
                닫기
              </button>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}