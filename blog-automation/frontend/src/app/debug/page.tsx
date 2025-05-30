'use client';

import { useState } from 'react';

export default function DebugPage() {
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const testAPI = async () => {
    setLoading(true);
    setError(null);
    setApiResponse(null);

    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    console.log('API URL:', apiUrl);

    try {
      const response = await fetch(`${apiUrl}/dashboard/stats`);
      console.log('Response status:', response.status);
      console.log('Response headers:', response.headers);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      console.log('Response data:', data);
      setApiResponse(data);
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">API 디버그 페이지</h1>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">환경 변수</h2>
          <p className="font-mono bg-gray-100 p-2 rounded">
            NEXT_PUBLIC_API_URL: {process.env.NEXT_PUBLIC_API_URL || 'Not set'}
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4">API 테스트</h2>
          <button
            onClick={testAPI}
            disabled={loading}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
          >
            {loading ? '테스트 중...' : 'API 테스트'}
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-300 rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-red-800 mb-2">에러:</h3>
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {apiResponse && (
          <div className="bg-green-50 border border-green-300 rounded-lg p-4">
            <h3 className="font-semibold text-green-800 mb-2">성공!</h3>
            <pre className="text-sm overflow-auto">{JSON.stringify(apiResponse, null, 2)}</pre>
          </div>
        )}

        <div className="mt-8 bg-gray-100 rounded-lg p-4">
          <h3 className="font-semibold mb-2">브라우저 콘솔 확인하기:</h3>
          <p className="text-sm text-gray-600">
            F12를 눌러 개발자 도구를 열고 Console 탭을 확인하세요.
          </p>
        </div>
      </div>
    </div>
  );
}
