'use client';

import { useState } from 'react';
import { X } from 'lucide-react';

interface AddPlatformModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (platform: any) => void;
  platformType: string;
}

export default function AddPlatformModal({
  isOpen,
  onClose,
  onAdd,
  platformType,
}: AddPlatformModalProps) {
  const [formData, setFormData] = useState({
    name: '',
    url: '',
    username: '',
  });
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const getPlatformInfo = (type: string) => {
    switch (type.toLowerCase()) {
      case 'tistory':
        return {
          icon: '🟠',
          color: 'orange',
          title: 'Tistory 블로그',
          urlPlaceholder: 'https://yourblog.tistory.com',
        };
      case 'wordpress':
        return {
          icon: '🟦',
          color: 'blue',
          title: 'WordPress 블로그',
          urlPlaceholder: 'https://yourblog.wordpress.com',
        };
      case 'naver':
        return {
          icon: '🟢',
          color: 'green',
          title: 'Naver 블로그',
          urlPlaceholder: 'https://blog.naver.com/username',
        };
      default:
        return {
          icon: '📝',
          color: 'gray',
          title: '블로그',
          urlPlaceholder: 'https://yourblog.com',
        };
    }
  };

  const platformInfo = getPlatformInfo(platformType);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/dashboard/platforms`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            name: formData.name,
            type: platformType,
            url: formData.url,
            username: formData.username,
          }),
        }
      );

      if (!response.ok) {
        throw new Error('플랫폼 추가에 실패했습니다');
      }

      const result = await response.json();
      onAdd(result.platform);
      setFormData({ name: '', url: '', username: '' });
      onClose();
    } catch (error) {
      console.error('플랫폼 추가 오류:', error);
      alert('플랫폼 추가에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md mx-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <span className="text-2xl">{platformInfo.icon}</span>
            <h2 className="text-xl font-semibold">{platformInfo.title} 연결</h2>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X size={24} />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">블로그 이름 *</label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="내 블로그"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">블로그 URL *</label>
            <input
              type="url"
              required
              value={formData.url}
              onChange={(e) => setFormData({ ...formData, url: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={platformInfo.urlPlaceholder}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">사용자명 (선택)</label>
            <input
              type="text"
              value={formData.username}
              onChange={(e) => setFormData({ ...formData, username: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="username"
            />
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={loading}
              className={`flex-1 px-4 py-2 text-white rounded-md hover:opacity-90 ${
                loading ? 'bg-gray-400' : `bg-${platformInfo.color}-500`
              }`}
            >
              {loading ? '추가 중...' : '추가하기'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
