'use client';

import { useState, useEffect } from 'react';
import { PublishRequest, BlogPlatform } from '@/types';

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
  const [platforms, setPlatforms] = useState<BlogPlatform[]>([]);
  const [loadingPlatforms, setLoadingPlatforms] = useState(true);

  // 등록된 플랫폼 목록 가져오기
  useEffect(() => {
    const fetchPlatforms = async () => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/dashboard/platforms`
        );
        if (response.ok) {
          const data = await response.json();
          setPlatforms(data.platforms || []);
        }
      } catch (error) {
        console.error('플랫폼 목록 가져오기 실패:', error);
      } finally {
        setLoadingPlatforms(false);
      }
    };

    fetchPlatforms();
  }, []);

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

  const handlePlatformSelect = (platformId: string) => {
    const selectedPlatform = platforms.find((p) => p.id === platformId);
    if (selectedPlatform) {
      setFormData({
        ...formData,
        blog_platform: {
          name: selectedPlatform.name,
          platform_type: selectedPlatform.platform_type || selectedPlatform.type || 'tistory',
          url: selectedPlatform.url,
        },
      });
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (formData.keywords.length === 0) {
      alert('최소 1개 이상의 키워드를 입력해주세요');
      return;
    }
    if (!formData.blog_platform.url) {
      alert('발행할 블로그 플랫폼을 선택해주세요');
      return;
    }
    onSubmit(formData);
  };

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
      <h2 className="text-xl font-semibold text-black mb-6">콘텐츠 생성 설정</h2>

      <form onSubmit={handleSubmit} className="space-y-6" style={{ color: '#000000' }}>
        {/* 키워드 입력 */}
        <div>
          <label className="block text-sm font-medium text-black mb-2">키워드 *</label>
          <div className="flex space-x-2 mb-3">
            <input
              type="text"
              value={keywordInput}
              onChange={(e) => setKeywordInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleKeywordAdd())}
              placeholder="키워드를 입력하세요"
              className="flex-1 px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
              style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
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

        {/* 블로그 플랫폼 선택 */}
        <div className="space-y-4 p-4 bg-gray-50 rounded-lg">
          <h3 className="font-medium text-black">발행할 블로그 플랫폼</h3>

          {loadingPlatforms ? (
            <div className="animate-pulse">
              <div className="h-10 bg-gray-200 rounded"></div>
            </div>
          ) : platforms.length > 0 ? (
            <div>
              <label className="block text-sm font-medium text-black mb-2">
                등록된 플랫폼 선택 *
              </label>
              <select
                value={platforms.find((p) => p.url === formData.blog_platform.url)?.id || ''}
                onChange={(e) => handlePlatformSelect(e.target.value)}
                className="w-full px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
                style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
              >
                <option value="">플랫폼을 선택하세요</option>
                {platforms.map((platform) => (
                  <option key={platform.id} value={platform.id}>
                    {platform.name} ({platform.platform_type || platform.type}) - {platform.url}
                  </option>
                ))}
              </select>

              {formData.blog_platform.url && (
                <div className="mt-2 p-2 bg-blue-50 rounded border border-blue-200">
                  <p className="text-sm text-blue-800">
                    <strong>선택된 플랫폼:</strong> {formData.blog_platform.name}
                  </p>
                  <p className="text-sm text-blue-600">{formData.blog_platform.url}</p>
                </div>
              )}
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-black mb-3">등록된 플랫폼이 없습니다</p>
              <a
                href="/platforms"
                className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 text-sm"
              >
                플랫폼 등록하기 →
              </a>
            </div>
          )}
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
