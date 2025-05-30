'use client';

import { useState, useEffect } from 'react';

interface PublishingActivity {
  date: string;
  count: number;
  posts: string[];
}

interface PublishingCalendarProps {
  data?: PublishingActivity[];
}

export default function PublishingCalendar({ data = [] }: PublishingCalendarProps) {
  const [yearData, setYearData] = useState<PublishingActivity[]>([]);

  useEffect(() => {
    // 지난 1년간의 데이터 생성 (실제로는 props에서 받아옴)
    const today = new Date();
    const oneYearAgo = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());
    const activities: PublishingActivity[] = [];

    // 실제 데이터가 있으면 사용, 없으면 샘플 데이터 생성
    if (data.length > 0) {
      setYearData(data);
    } else {
      // 샘플 데이터 생성
      for (let d = new Date(oneYearAgo); d <= today; d.setDate(d.getDate() + 1)) {
        const dateStr = d.toISOString().split('T')[0];
        const randomActivity = Math.random();
        let count = 0;

        if (randomActivity > 0.7) count = Math.floor(Math.random() * 3) + 1;

        activities.push({
          date: dateStr,
          count,
          posts: count > 0 ? [`포스트 ${count}`] : [],
        });
      }
      setYearData(activities);
    }
  }, [data]);

  const getColorIntensity = (count: number): string => {
    if (count === 0) return 'bg-gray-100';
    if (count === 1) return 'bg-green-200';
    if (count === 2) return 'bg-green-400';
    return 'bg-green-600';
  };

  const getWeekDays = (): string[] => ['일', '월', '화', '수', '목', '금', '토'];

  const getMonthLabels = (): { label: string; week: number }[] => {
    const months: { label: string; week: number }[] = [];
    let currentMonth = -1;
    let weekIndex = 0;

    yearData.forEach((activity, index) => {
      const date = new Date(activity.date);
      const month = date.getMonth();

      if (index % 7 === 0) weekIndex = Math.floor(index / 7);

      if (month !== currentMonth && date.getDate() <= 7) {
        currentMonth = month;
        months.push({
          label: date.toLocaleDateString('ko-KR', { month: 'short' }),
          week: weekIndex,
        });
      }
    });

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

  const totalPosts = yearData.reduce((sum, activity) => sum + activity.count, 0);
  const activeDays = yearData.filter((activity) => activity.count > 0).length;

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-black">발행 활동</h3>
        <div className="text-sm text-gray-600">
          총 {totalPosts}개 포스트 · {activeDays}일 활성
        </div>
      </div>

      <div className="space-y-3">
        {/* 월 라벨 */}
        <div className="flex text-xs text-gray-500 mb-2">
          <div className="w-8"></div>
          {getMonthLabels().map((month, index) => (
            <div
              key={index}
              className="flex-1 text-left"
              style={{ marginLeft: `${month.week * 12}px` }}
            >
              {month.label}
            </div>
          ))}
        </div>

        {/* 캘린더 그리드 */}
        <div className="flex">
          {/* 요일 라벨 */}
          <div className="flex flex-col text-xs text-gray-500 mr-2">
            {getWeekDays().map((day, index) => (
              <div key={index} className="h-3 w-6 flex items-center">
                {index % 2 === 1 ? day : ''}
              </div>
            ))}
          </div>

          {/* 활동 그리드 */}
          <div className="flex flex-wrap" style={{ width: 'calc(100% - 32px)' }}>
            {yearData.map((activity) => (
              <div
                key={activity.date}
                className={`w-3 h-3 rounded-sm mr-1 mb-1 ${getColorIntensity(activity.count)} hover:ring-2 hover:ring-gray-400 cursor-pointer transition-all`}
                title={`${formatDate(activity.date)}: ${activity.count}개 포스트 발행`}
              />
            ))}
          </div>
        </div>

        {/* 범례 */}
        <div className="flex items-center justify-end text-xs text-gray-500 mt-3">
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
  );
}
