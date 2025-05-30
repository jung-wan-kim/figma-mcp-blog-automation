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
      name: '티스토리 블로그',
      platform_type: 'tistory',
      url: 'https://example.tistory.com',
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
    onSubmit(formData);
  };

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
      <form onSubmit={handleSubmit} className="space-y-6" style={{ color: '#000000' }}>
        {/* 키워드 입력 */}
        <div>
          <label className="block text-sm font-medium text-black mb-2">키워드 *</label>
          <div className="mb-3">
            <input
              type="text"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  handleKeywordAdd();
                }
              }}
              placeholder="키워드를 입력하고 엔터를 누르세요"
              className="w-full px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
              style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
            />
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

        {/* 콘텐츠 설정 - 한 줄 정렬 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* 콘텐츠 유형 */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">콘텐츠 유형</label>
            <select
              value={formData.content_type}
              onChange={(e) => setFormData({ ...formData, content_type: e.target.value })}
              className="w-full px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
              style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
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
            <label className="block text-sm font-medium text-black mb-2">목표 글 길이</label>
            <select
              value={formData.target_length}
              onChange={(e) =>
                setFormData({ ...formData, target_length: parseInt(e.target.value) })
              }
              className="w-full px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
              style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
            >
              <option value={1000}>짧은 글 (1,000자)</option>
              <option value={1500}>보통 글 (1,500자)</option>
              <option value={2000}>긴 글 (2,000자)</option>
              <option value={3000}>상세한 글 (3,000자)</option>
              <option value={4000}>심층 분석 (4,000자)</option>
              <option value={5000}>완전한 가이드 (5,000자)</option>
            </select>
          </div>

          {/* 톤앤매너 */}
          <div>
            <label className="block text-sm font-medium text-black mb-2">톤앤매너</label>
            <select
              value={formData.tone}
              onChange={(e) => setFormData({ ...formData, tone: e.target.value })}
              className="w-full px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
              style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
            >
              <option value="친근하고 전문적인">친근하고 전문적인</option>
              <option value="정중하고 격식있는">정중하고 격식있는</option>
              <option value="캐주얼하고 재미있는">캐주얼하고 재미있는</option>
              <option value="전문적이고 상세한">전문적이고 상세한</option>
            </select>
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
