'use client';

import { useState, useEffect } from 'react';
import { DashboardStats } from '@/types';
import StatsCards from '@/components/StatsCards';
import PlatformList from '@/components/PlatformList';
import RecentPosts from '@/components/RecentPosts';
import Navbar from '@/components/Navbar';

export default function Dashboard() {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      setLoading(true);
      console.log(
        'Fetching stats from:',
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/dashboard/stats`
      );

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/dashboard/stats`
      );
      console.log('Response status:', response.status);

      if (!response.ok) {
        throw new Error('대시보드 데이터를 가져올 수 없습니다');
      }
      const data = await response.json();
      console.log('Received data:', data);

      setStats(data);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">오류 발생</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={fetchStats}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">🤖 AI 블로그 자동화 대시보드</h1>
          <p className="mt-2 text-gray-600">
            콘텐츠 생성부터 발행까지 모든 과정을 한눈에 관리하세요
          </p>
        </div>

        {stats && (
          <div className="space-y-8">
            {/* 통계 카드 */}
            <StatsCards stats={stats} />

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* 플랫폼 목록 */}
              <PlatformList platforms={stats.platforms} />

              {/* 최근 발행된 글 */}
              <RecentPosts posts={stats.recent_posts} />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
