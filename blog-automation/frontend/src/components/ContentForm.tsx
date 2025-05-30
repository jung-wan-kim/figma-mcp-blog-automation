'use client';

import { useState } from 'react';
import { PublishRequest } from '@/types';

interface ContentFormProps {
  onSubmit: (data: PublishRequest) => void;
  loading: boolean;
  error: string | null;
}

export default function ContentForm({ onSubmit, loading, error }: ContentFormProps) {
  const [formData, setFormData] = useState<PublishRequest>({
    keywords: [],
    content_type: 'blog_post',
    target_length: 3000,
    tone: '친근하고 전문적인',
    blog_platform: {
      name: '',
      platform_type: 'tistory',
      url: '',
    },
  });

  const [keywordInput, setKeywordInput] = useState('');

  const handleKeywordAdd = () => {
    if (keywordInput.trim() && !formData.keywords.includes(keywordInput.trim())) {
      setFormData({
        ...formData,
        keywords: [...formData.keywords, keywordInput.trim()],
      });
      setKeywordInput('');
    }
  };

  const handleKeywordRemove = (keyword: string) => {
    setFormData({
      ...formData,
      keywords: formData.keywords.filter((k) => k !== keyword),
    });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.keywords.length === 0) {
      alert('최소 1개 이상의 키워드를 입력해주세요');
      return;
    }
    if (!formData.blog_platform.name || !formData.blog_platform.url) {
      alert('블로그 플랫폼 정보를 모두 입력해주세요');
      return;
    }
    onSubmit(formData);
  };

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">콘텐츠 생성 설정</h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 키워드 입력 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">키워드 *</label>
          <div className="flex space-x-2 mb-3">
            <input
              type="text"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleKeywordAdd())}
              placeholder="키워드를 입력하세요"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="button"
              onClick={handleKeywordAdd}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              추가
            </button>
          </div>

          {/* 키워드 태그 */}
          <div className="flex flex-wrap gap-2">
            {formData.keywords.map((keyword, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
              >
                {keyword}
                <button
                  type="button"
                  onClick={() => handleKeywordRemove(keyword)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* 콘텐츠 유형 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">콘텐츠 유형</label>
          <select
            value={formData.content_type}
            onChange={(e) => setFormData({ ...formData, content_type: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="blog_post">블로그 포스트</option>
            <option value="guide">가이드</option>
            <option value="tutorial">튜토리얼</option>
            <option value="review">리뷰</option>
            <option value="news">뉴스</option>
          </select>
        </div>

        {/* 글 길이 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">목표 글 길이 (자)</label>
          <input
            type="number"
            value={formData.target_length}
            onChange={(e) => setFormData({ ...formData, target_length: parseInt(e.target.value) })}
            min="1000"
            max="5000"
            step="500"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>

        {/* 톤앤매너 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">톤앤매너</label>
          <select
            value={formData.tone}
            onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="친근하고 전문적인">친근하고 전문적인</option>
            <option value="정중하고 격식있는">정중하고 격식있는</option>
            <option value="캐주얼하고 재미있는">캐주얼하고 재미있는</option>
            <option value="전문적이고 상세한">전문적이고 상세한</option>
          </select>
        </div>

        {/* 블로그 플랫폼 정보 */}
        <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-gray-900">블로그 플랫폼 정보</h3>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">플랫폼 이름 *</label>
            <input
              type="text"
              value={formData.blog_platform.name}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  blog_platform: { ...formData.blog_platform, name: e.target.value },
                })
              }
              placeholder="예: 개발자 블로그"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">플랫폼 유형</label>
            <select
              value={formData.blog_platform.platform_type}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  blog_platform: { ...formData.blog_platform, platform_type: e.target.value },
                })
              }
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="tistory">Tistory</option>
              <option value="wordpress">WordPress</option>
              <option value="naver">Naver Blog</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">블로그 URL *</label>
            <input
              type="url"
              value={formData.blog_platform.url}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  blog_platform: { ...formData.blog_platform, url: e.target.value },
                })
              }
              placeholder="https://myblog.tistory.com"
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>

        {/* 에러 메시지 */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-md">
            <p className="text-red-800">{error}</p>
          </div>
        )}

        {/* 제출 버튼 */}
        <button
          type="submit"
          disabled={loading}
          className={`w-full py-3 px-4 rounded-md font-medium ${
            loading ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'
          } text-white transition-colors`}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              콘텐츠 생성 중...
            </div>
          ) : (
            '🚀 콘텐츠 생성 및 발행'
          )}
        </button>
      </form>
    </div>
  );
}
