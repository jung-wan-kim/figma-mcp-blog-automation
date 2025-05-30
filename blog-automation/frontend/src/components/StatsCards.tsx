'use client';

import { DashboardStats } from '@/types';

interface StatsCardsProps {
  stats: DashboardStats;
}

export default function StatsCards({ stats }: StatsCardsProps) {
  const totalViews = stats.platforms.reduce(
    (sum, platform) => sum + (platform.total_views || 0),
    0
  );
  const totalLikes = stats.platforms.reduce(
    (sum, platform) => sum + (platform.total_likes || 0),
    0
  );

  const cards = [
    {
      title: '총 발행된 글',
      value: stats.total_posts,
      icon: '📝',
      color: 'bg-blue-500',
      description: '전체 플랫폼에 발행된 글 수',
    },
    {
      title: '연결된 플랫폼',
      value: stats.platforms.length,
      icon: '🌐',
      color: 'bg-green-500',
      description: '현재 연결된 블로그 플랫폼 수',
    },
    {
      title: '총 조회수',
      value: totalViews.toLocaleString(),
      icon: '👀',
      color: 'bg-purple-500',
      description: '모든 글의 누적 조회수',
    },
    {
      title: '총 좋아요',
      value: totalLikes.toLocaleString(),
      icon: '❤️',
      color: 'bg-pink-500',
      description: '모든 글의 누적 좋아요 수',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {cards.map((card, index) => (
        <div
          key={index}
          className="bg-white overflow-hidden shadow-sm rounded-lg border border-gray-200 hover:shadow-md transition-shadow"
        >
          <div className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 truncate">{card.title}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{card.value}</p>
                <p className="mt-1 text-xs text-gray-500">{card.description}</p>
              </div>
              <div className={`p-3 rounded-full ${card.color} text-white text-2xl`}>
                {card.icon}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
