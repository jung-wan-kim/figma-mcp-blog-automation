'use client';

import { ContentResponse } from '@/types';

interface ContentPreviewProps {
  content: ContentResponse | null;
  loading: boolean;
}

export default function ContentPreview({ content, loading }: ContentPreviewProps) {
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
          <h3 className="text-lg font-medium text-black mb-2">제목</h3>
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

        {/* 콘텐츠 본문 (마크다운 스타일링) */}
        <div>
          <h3 className="text-lg font-medium text-black mb-2">본문</h3>
          <div className="bg-gray-50 p-4 rounded-lg text-sm text-black whitespace-pre-wrap">
            {content.content}
          </div>
        </div>

        {/* 추천 이미지 - 이미지가 있을 때만 표시 */}
        {content.suggested_images &&
          ((content.suggested_images.title_based &&
            content.suggested_images.title_based.length > 0) ||
            (content.suggested_images.keyword_based &&
              content.suggested_images.keyword_based.length > 0)) && (
            <div>
              <h3 className="text-lg font-medium text-black mb-2">추천 이미지</h3>
              <div className="space-y-4">
                {/* 제목 기반 이미지 */}
                {content.suggested_images.title_based &&
                  content.suggested_images.title_based.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-black mb-2">제목 기반</h4>
                      <div className="grid grid-cols-2 gap-2">
                        {content.suggested_images.title_based.map((image) => (
                          <img
                            key={image.id}
                            src={image.thumb_url}
                            alt={image.alt_text}
                            className="w-full h-24 object-cover rounded border border-gray-200"
                          />
                        ))}
                      </div>
                    </div>
                  )}

                {/* 키워드 기반 이미지 */}
                {content.suggested_images.keyword_based &&
                  content.suggested_images.keyword_based.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-black mb-2">키워드 기반</h4>
                      <div className="grid grid-cols-2 gap-2">
                        {content.suggested_images.keyword_based.map((image) => (
                          <img
                            key={image.id}
                            src={image.thumb_url}
                            alt={image.alt_text}
                            className="w-full h-24 object-cover rounded border border-gray-200"
                          />
                        ))}
                      </div>
                    </div>
                  )}
              </div>
            </div>
          )}
      </div>
    </div>
  );
}
