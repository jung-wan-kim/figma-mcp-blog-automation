'use client';

import { useState } from 'react';
import { PublishRequest, ContentResponse } from '@/types';
import Navbar from '@/components/Navbar';
import ContentForm from '@/components/ContentForm';
import ContentPreview from '@/components/ContentPreview';

export default function CreatePage() {
  const [content, setContent] = useState<ContentResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (formData: PublishRequest) => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/test/publish`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(formData),
        }
      );

      if (!response.ok) {
        throw new Error('콘텐츠 생성에 실패했습니다');
      }

      const result = await response.json();
      setContent(result.content);
    } catch (err) {
      setError(err instanceof Error ? err.message : '알 수 없는 오류가 발생했습니다');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">✍️ 콘텐츠 생성 및 발행</h1>
          <p className="mt-2 text-gray-600">
            AI를 활용해 고품질 블로그 콘텐츠를 생성하고 원하는 플랫폼에 발행하세요
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* 콘텐츠 생성 폼 */}
          <div>
            <ContentForm onSubmit={handleSubmit} loading={loading} error={error} />
          </div>

          {/* 콘텐츠 미리보기 */}
          <div>
            <ContentPreview content={content} loading={loading} />
          </div>
        </div>
      </div>
    </div>
  );
}
