'use client';

import { ContentResponse } from '@/types';
import { useState } from 'react';

interface ContentPreviewProps {
  content: ContentResponse | null;
  loading: boolean;
}

export default function ContentPreview({ content, loading }: ContentPreviewProps) {
  const [copiedTitle, setCopiedTitle] = useState(false);
  const [copiedContent, setCopiedContent] = useState(false);
  
  // 클립보드에 복사하는 함수
  const copyToClipboard = async (text: string, type: 'title' | 'content') => {
    try {
      await navigator.clipboard.writeText(text);
      if (type === 'title') {
        setCopiedTitle(true);
        setTimeout(() => setCopiedTitle(false), 2000);
      } else {
        setCopiedContent(true);
        setTimeout(() => setCopiedContent(false), 2000);
      }
    } catch (err) {
      console.error('복사 실패:', err);
    }
  };
  if (loading) {
    return (
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-black mb-6">콘텐츠 미리보기</h2>
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-3/4"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
          <div className="space-y-2">
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded"></div>
            <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          </div>
        </div>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-black mb-6">콘텐츠 미리보기</h2>
        <div className="text-center py-12">
          <div className="text-4xl mb-4">✍️</div>
          <p className="text-black">콘텐츠를 생성하면 여기에 미리보기가 표시됩니다</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-xl font-semibold text-black">콘텐츠 미리보기</h2>
        <span className="text-sm text-gray-600">
          {content.ai_model_used} ({content.word_count.toLocaleString()}자)
        </span>
      </div>

      <div className="space-y-6">
        {/* 제목 */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-medium text-black">제목</h3>
            <button
              onClick={() => copyToClipboard(content.title, 'title')}
              className="flex items-center gap-1 px-2 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
              title="제목 복사하기"
            >
              {copiedTitle ? (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  복사됨
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  복사
                </>
              )}
            </button>
          </div>
          <p className="text-xl font-bold text-black">{content.title}</p>
        </div>

        {/* 메타 설명 */}
        <div>
          <h3 className="text-lg font-medium text-black mb-2">메타 설명</h3>
          <p className="text-black bg-gray-50 p-3 rounded">{content.meta_description}</p>
        </div>

        {/* 대표 이미지 - URL이 있을 때만 표시 */}
        {content.featured_image && content.featured_image.url && (
          <div>
            <h3 className="text-lg font-medium text-black mb-2">대표 이미지</h3>
            <div className="border border-gray-200 rounded-lg overflow-hidden">
              <img
                src={content.featured_image.url}
                alt={content.featured_image.alt_text}
                className="w-full h-48 object-cover"
              />
              <div className="p-3 bg-gray-50">
                <p className="text-sm text-black">{content.featured_image.alt_text}</p>
                <p className="text-xs text-black mt-1">
                  출처: {content.featured_image.attribution.source} -{' '}
                  {content.featured_image.attribution.photographer}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* 콘텐츠 본문 (마크다운 렌더링으로 이미지 포함) */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-medium text-black">본문</h3>
            <button
              onClick={() => copyToClipboard(content.content, 'content')}
              className="flex items-center gap-1 px-2 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
              title="본문 복사하기"
            >
              {copiedContent ? (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  복사됨
                </>
              ) : (
                <>
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  복사
                </>
              )}
            </button>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg text-sm text-black">
            <div 
              className="prose prose-sm max-w-none"
              style={{
                lineHeight: '1.6',
                color: '#000000'
              }}
            >
              {content.content.split('\n').map((line, index) => {
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
          </div>
        </div>
      </div>
    </div>
  );
}
