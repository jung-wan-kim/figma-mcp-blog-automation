'use client';

import { useState, useEffect } from 'react';

interface PublishingActivity {
  date: string;
  count: number;
  posts: string[];
}

interface PublishingApiResponse {
  activities: PublishingActivity[];
  total_posts: number;
  active_days: number;
  date_range: {
    start: string;
    end: string;
  };
}

export default function PublishingCalendar() {
  const [yearData, setYearData] = useState<PublishingActivity[]>([]);
  const [stats, setStats] = useState<{ total_posts: number; active_days: number }>({
    total_posts: 0,
    active_days: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchPublishingActivity();
  }, []);

  const fetchPublishingActivity = async () => {
    try {
      setLoading(true);
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/dashboard/publishing-activity`
      );

      if (!response.ok) {
        throw new Error('발행 활동 데이터를 가져올 수 없습니다');
      }

      const data: PublishingApiResponse = await response.json();
      setYearData(data.activities);
      setStats({
        total_posts: data.total_posts,
        active_days: data.active_days,
      });
    } catch (error) {
      console.error('발행 활동 데이터 로딩 실패:', error);
      // 에러 시 빈 데이터로 설정
      setYearData([]);
      setStats({ total_posts: 0, active_days: 0 });
    } finally {
      setLoading(false);
    }
  };

  const getColorIntensity = (count: number): string => {
    if (count === 0) return 'bg-gray-100';
    if (count === 1) return 'bg-green-200';
    if (count === 2) return 'bg-green-400';
    return 'bg-green-600';
  };

  const getWeekDays = (): string[] => ['', 'Mon', '', 'Wed', '', 'Fri', ''];

  const getMonthLabels = (): { label: string; week: number }[] => {
    const months: { label: string; week: number }[] = [];
    let currentMonth = -1;
    let isFirstMonth = true;

    // 53주 동안 주별로 확인
    for (let weekIndex = 0; weekIndex < 53; weekIndex++) {
      const startOfWeekIndex = weekIndex * 7;
      if (startOfWeekIndex >= yearData.length) break;

      const activity = yearData[startOfWeekIndex];
      if (!activity) continue;

      const date = new Date(activity.date);
      const month = date.getMonth();

      // 월이 바뀔 때만 라벨 추가 (첫 번째 월은 제외)
      if (month !== currentMonth) {
        if (!isFirstMonth) {
          months.push({
            label: date.toLocaleDateString('en-US', { month: 'short' }),
            week: weekIndex,
          });
        }
        currentMonth = month;
        isFirstMonth = false;
      }
    }

    return months;
  };

  const formatDate = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-medium text-black">발행 활동</h3>
          <div className="text-sm text-gray-600">로딩 중...</div>
        </div>
        <div className="animate-pulse">
          <div className="h-20 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-black">발행 활동</h3>
        <div className="text-sm text-gray-600">
          총 {stats.total_posts}개 포스트 · {stats.active_days}일 활성
        </div>
      </div>

      <div className="space-y-1 flex flex-col items-center">
        {/* 월 라벨 */}
        <div className="flex text-[10px] text-gray-500 max-w-4xl">
          <div className="w-8"></div>
          <div className="flex gap-[2px]" style={{ width: 'calc(100% - 40px)' }}>
            {Array.from({ length: 53 }, (_, weekIndex) => {
              const monthLabel = getMonthLabels().find((m) => m.week === weekIndex);
              return (
                <div key={weekIndex} className="w-3 text-center">
                  {monthLabel ? monthLabel.label : ''}
                </div>
              );
            })}
          </div>
        </div>

        {/* 캘린더 그리드 */}
        <div className="flex max-w-4xl">
          {/* 요일 라벨 */}
          <div className="flex flex-col text-[10px] text-gray-500 mr-2">
            {getWeekDays().map((day, index) => (
              <div key={index} className="h-3 w-8 flex items-center">
                {day}
              </div>
            ))}
          </div>

          {/* 활동 그리드 */}
          <div style={{ width: 'calc(100% - 40px)' }}>
            <div className="flex gap-[2px]">
              {Array.from({ length: 53 }, (_, weekIndex) => (
                <div key={weekIndex} className="flex flex-col gap-[2px]">
                  {Array.from({ length: 7 }, (_, dayIndex) => {
                    const activityIndex = weekIndex * 7 + dayIndex;
                    const activity = yearData[activityIndex];

                    // 오른쪽 끝 주(52번째 주)는 항상 7개 칸을 모두 표시
                    if (!activity) {
                      return (
                        <div 
                          key={dayIndex} 
                          className={`w-3 h-3 rounded-sm ${weekIndex === 52 ? 'bg-gray-100' : ''}`} 
                        />
                      );
                    }

                    return (
                      <div
                        key={activity.date}
                        className={`w-3 h-3 rounded-sm ${getColorIntensity(activity.count)} hover:ring-2 hover:ring-gray-400 cursor-pointer transition-all`}
                        title={`${formatDate(activity.date)}: ${activity.count}개 포스트 발행${activity.posts.length > 0 ? '\n' + activity.posts.join('\n') : ''}`}
                      />
                    );
                  })}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 범례 */}
        <div className="flex items-center text-xs text-gray-500 mt-3 max-w-4xl w-full">
          <div className="w-8"></div>
          <div
            className="flex items-center justify-end"
            style={{
              width: `${53 * 12 + 52 * 2 + 56}px`, // 53주 × 12px(잔디) + 52개 × 2px(gap) + 56px(4개 잔디만큼 오른쪽)
            }}
          >
            <span className="mr-2">적음</span>
            <div className="flex space-x-1">
              <div className="w-3 h-3 bg-gray-100 rounded-sm"></div>
              <div className="w-3 h-3 bg-green-200 rounded-sm"></div>
              <div className="w-3 h-3 bg-green-400 rounded-sm"></div>
              <div className="w-3 h-3 bg-green-600 rounded-sm"></div>
            </div>
            <span className="ml-2">많음</span>
          </div>
        </div>
      </div>
    </div>
  );
}
