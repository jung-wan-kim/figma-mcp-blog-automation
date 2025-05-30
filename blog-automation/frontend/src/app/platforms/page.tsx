'use client';

import { useState, useEffect } from 'react';
import { BlogPlatform } from '@/types';
import Navbar from '@/components/Navbar';

export default function PlatformsPage() {
  const [platforms, setPlatforms] = useState<BlogPlatform[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchPlatforms();
  }, []);

  const fetchPlatforms = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/dashboard/platforms');
      if (!response.ok) {
        throw new Error('플랫폼 정보를 가져올 수 없습니다');
      }
      const data = await response.json();
      setPlatforms(data.platforms || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    } finally {
      setLoading(false);
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

  const getPlatformColor = (type: string) => {
    switch (type.toLowerCase()) {
      case 'tistory':
        return 'bg-orange-50 border-orange-200';
      case 'wordpress':
        return 'bg-blue-50 border-blue-200';
      case 'naver':
        return 'bg-green-50 border-green-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="animate-pulse space-y-4">
            {[...Array(3)].map((_, i) => (
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
              onClick={fetchPlatforms}
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
          <h1 className="text-3xl font-bold text-gray-900">🌐 플랫폼 관리</h1>
          <p className="mt-2 text-gray-600">
            연결된 블로그 플랫폼을 관리하고 발행 현황을 확인하세요
          </p>
        </div>

        {platforms.length === 0 ? (
          <div className="bg-white shadow-sm rounded-lg border border-gray-200 p-12">
            <div className="text-center">
              <div className="text-6xl mb-4">🌐</div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">연결된 플랫폼이 없습니다</h3>
              <p className="text-gray-500 mb-6">
                블로그 플랫폼을 연결하여 자동 발행을 시작해보세요
              </p>
              <div className="flex justify-center space-x-4">
                <button className="inline-flex items-center px-4 py-2 bg-orange-500 text-white rounded-md hover:bg-orange-600">
                  🟠 Tistory 연결
                </button>
                <button className="inline-flex items-center px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600">
                  🟦 WordPress 연결
                </button>
                <button className="inline-flex items-center px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600">
                  🟢 Naver Blog 연결
                </button>
              </div>
            </div>
          </div>
        ) : (
          <div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {platforms.map((platform, index) => (
                <div
                  key={index}
                  className={`bg-white shadow-sm rounded-lg border-2 p-6 hover:shadow-md transition-shadow ${getPlatformColor(platform.type)}`}
                >
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="text-3xl">{getPlatformIcon(platform.type)}</div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{platform.name}</h3>
                        <p className="text-sm text-gray-500 capitalize">{platform.type}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-gray-900">{platform.post_count}</div>
                      <div className="text-xs text-gray-500">발행된 글</div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <div>
                      <label className="text-sm font-medium text-gray-700">URL</label>
                      <a
                        href={platform.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="block text-sm text-blue-600 hover:text-blue-800 truncate"
                      >
                        {platform.url}
                      </a>
                    </div>

                    <div className="flex justify-between items-center text-sm">
                      <span className="text-gray-500">총 조회수:</span>
                      <span className="font-medium">
                        {(platform.total_views || 0).toLocaleString()}
                      </span>
                    </div>

                    <div className="flex justify-between items-center text-sm">
                      <span className="text-gray-500">총 좋아요:</span>
                      <span className="font-medium">
                        {(platform.total_likes || 0).toLocaleString()}
                      </span>
                    </div>

                    <div className="pt-3 border-t border-gray-200">
                      <div className="flex space-x-2">
                        <button className="flex-1 px-3 py-2 bg-blue-50 text-blue-700 rounded text-sm hover:bg-blue-100">
                          설정
                        </button>
                        <button className="flex-1 px-3 py-2 bg-gray-50 text-gray-700 rounded text-sm hover:bg-gray-100">
                          통계
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-8 bg-white shadow-sm rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">새 플랫폼 추가</h3>
              <div className="flex flex-wrap gap-3">
                <button className="inline-flex items-center px-4 py-2 bg-orange-50 text-orange-700 border border-orange-200 rounded-md hover:bg-orange-100">
                  🟠 Tistory 연결
                </button>
                <button className="inline-flex items-center px-4 py-2 bg-blue-50 text-blue-700 border border-blue-200 rounded-md hover:bg-blue-100">
                  🟦 WordPress 연결
                </button>
                <button className="inline-flex items-center px-4 py-2 bg-green-50 text-green-700 border border-green-200 rounded-md hover:bg-green-100">
                  🟢 Naver Blog 연결
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
