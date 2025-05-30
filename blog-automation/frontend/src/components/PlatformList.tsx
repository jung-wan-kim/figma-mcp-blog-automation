'use client';

import { BlogPlatform } from '@/types';

interface PlatformListProps {
  platforms: BlogPlatform[];
}

export default function PlatformList({ platforms }: PlatformListProps) {
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
    <div className="bg-white shadow-sm rounded-lg border border-gray-200">
      <div className="px-6 py-4 border-b border-gray-200">
        <h3 className="text-lg font-medium text-gray-900">연결된 블로그 플랫폼</h3>
        <p className="mt-1 text-sm text-gray-500">현재 연결된 블로그 플랫폼과 발행 현황</p>
      </div>

      <div className="px-6 py-4">
        {platforms.length === 0 ? (
          <div className="text-center py-8">
            <div className="text-4xl mb-4">🌐</div>
            <p className="text-gray-500">연결된 플랫폼이 없습니다</p>
            <p className="text-sm text-gray-400 mt-2">
              플랫폼을 추가하여 블로그 발행을 시작해보세요
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {platforms.map((platform, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center space-x-4">
                  <div className="text-2xl">{getPlatformIcon(platform.type)}</div>
                  <div>
                    <h4 className="font-medium text-gray-900">{platform.name}</h4>
                    <p className="text-sm text-gray-500">
                      {platform.type} • {platform.url}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <div className="text-lg font-bold text-gray-900">{platform.post_count}</div>
                  <div className="text-sm text-gray-500">발행된 글</div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
