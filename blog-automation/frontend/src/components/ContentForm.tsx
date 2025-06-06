'use client';

import { useState, useEffect } from 'react';
import { PublishRequest } from '@/types';

interface ContentFormProps {
  onSubmit: (data: PublishRequest) => void;
  loading: boolean;
  error: string | null;
}

interface Platform {
  id: string;
  name: string;
  platform_type: string;
  url: string;
}

export default function ContentForm({ onSubmit, loading, error }: ContentFormProps) {
  const [platforms, setPlatforms] = useState<Platform[]>([]);
  const [selectedPlatformId, setSelectedPlatformId] = useState<string>('');
  const [topic, setTopic] = useState<string>('');
  const [formData, setFormData] = useState<PublishRequest>({
    keywords: [],
    content_type: 'blog_post',
    target_length: 3000,
    tone: '친근하고 전문적인',
    blog_platform: {
      name: '',
      platform_type: '',
      url: '',
    },
  });

  // 플랫폼 목록 가져오기
  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/dashboard/platforms`
      );
      if (response.ok) {
        const data = await response.json();
        setPlatforms(data.platforms || []);
        
        // 첫 번째 플랫폼을 기본값으로 설정
        if (data.platforms && data.platforms.length > 0) {
          const firstPlatform = data.platforms[0];
          setSelectedPlatformId(firstPlatform.id);
          setFormData(prev => ({
            ...prev,
            blog_platform: {
              name: firstPlatform.name,
              platform_type: firstPlatform.platform_type,
              url: firstPlatform.url,
            }
          }));
        }
      }
    } catch (err) {
      console.error('플랫폼 목록 가져오기 실패:', err);
    }
  };

  // 플랫폼 선택 시 formData 업데이트
  const handlePlatformChange = (platformId: string) => {
    const platform = platforms.find(p => p.id === platformId);
    if (platform) {
      setSelectedPlatformId(platformId);
      setFormData(prev => ({
        ...prev,
        blog_platform: {
          name: platform.name,
          platform_type: platform.platform_type,
          url: platform.url,
        }
      }));
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!topic.trim()) {
      alert('주제를 입력해주세요');
      return;
    }
    
    // 주제 전체를 키워드로 전달
    onSubmit({
      ...formData,
      keywords: [topic.trim()]  // 주제를 그대로 전달
    });
  };

  return (
    <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-6">
      <form onSubmit={handleSubmit} className="space-y-6" style={{ color: '#000000' }}>
        {/* 주제 입력 */}
        <div>
          <label className="block text-sm font-medium text-black mb-2">작성하고 싶은 주제 *</label>
          <div className="mb-3">
            <input
              type="text"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="예: 인공지능이 바꿀 미래의 교육 방식"
              className="w-full px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
              style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
              required
            />
            <p className="text-xs text-gray-500 mt-1">
              작성하고 싶은 주제를 자유롭게 입력해주세요. AI가 주제에 맞는 콘텐츠를 생성합니다.
            </p>
          </div>
        </div>

        {/* 플랫폼 선택 */}
        <div>
          <label className="block text-sm font-medium text-black mb-2">발행할 플랫폼</label>
          <select
            value={selectedPlatformId}
            onChange={(e) => handlePlatformChange(e.target.value)}
            className="w-full px-3 py-2 border-2 border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white text-black"
            style={{ color: '#000000 !important', backgroundColor: '#ffffff !important' }}
          >
            {platforms.map((platform) => (
              <option key={platform.id} value={platform.id}>
                {platform.name} ({platform.platform_type})
              </option>
            ))}
          </select>
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
          disabled={loading || !topic.trim()}
          className={`w-full py-3 px-4 rounded-md font-medium ${
            loading || !topic.trim() ? 'bg-gray-400 cursor-not-allowed' : 'bg-blue-500 hover:bg-blue-600'
          } text-white transition-colors`}
        >
          {loading ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              콘텐츠 생성 중...
            </div>
          ) : (
            '🚀 콘텐츠 생성'
          )}
        </button>
      </form>
    </div>
  );
}
