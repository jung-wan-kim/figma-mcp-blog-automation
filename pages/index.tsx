import React, { useState } from 'react'
import Link from 'next/link'
import { Button, Card, Input } from '../src/components/generated'

export default function Home() {
  const [inputValue, setInputValue] = useState('')
  
  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Navigation */}
        <nav className="mb-8 flex justify-center space-x-6">
          <Link href="/" className="text-blue-600 hover:text-blue-800 font-medium">
            홈
          </Link>
          <Link href="/dashboard" className="text-blue-600 hover:text-blue-800 font-medium">
            대시보드
          </Link>
        </nav>
        
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-8">
            🎨 Vibe 프로젝트 초기화 완료
          </h1>
          <p className="text-xl text-gray-600 mb-12">
            템플릿 기반으로 생성된 컴포넌트 데모
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <Card variant="elevated">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">🔘 버튼 컴포넌트</h2>
            <p className="text-gray-600 mb-6">다양한 크기와 스타일의 버튼</p>
            <div className="space-y-4">
              <div className="space-x-2">
                <Button size="sm" variant="primary">Primary</Button>
                <Button size="sm" variant="secondary">Secondary</Button>
                <Button size="sm" variant="outline">Outline</Button>
              </div>
              <div className="space-x-2">
                <Button size="md" variant="primary">Medium</Button>
                <Button size="lg" variant="primary">Large</Button>
              </div>
            </div>
          </Card>
          
          <Card variant="outlined">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">📝 입력 필드</h2>
            <p className="text-gray-600 mb-6">다양한 타입의 입력 필드</p>
            <div className="space-y-4">
              <Input 
                placeholder="이름을 입력하세요"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
              />
              <Input type="email" placeholder="이메일을 입력하세요" />
              <Input type="password" placeholder="비밀번호를 입력하세요" />
              <Input type="number" placeholder="숫자를 입력하세요" />
            </div>
          </Card>
          
          <Card variant="default">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">📊 시스템 정보</h2>
            <p className="text-gray-600 mb-6">초기화 시스템 상태</p>
            <div className="text-sm text-gray-600 mb-6">
              <p className="mb-2">✅ 템플릿 초기화 완료</p>
              <p className="mb-2">✅ 3개 컴포넌트 생성</p>
              <p className="mb-2">✅ TypeScript 타입 정의</p>
              <p className="mb-2">✅ Tailwind CSS 스타일링</p>
            </div>
            <Link href="/dashboard">
              <Button variant="primary" size="sm">대시보드 보기</Button>
            </Link>
          </Card>
        </div>
        
        <div className="mt-12 text-center">
          <Card variant="elevated" className="max-w-4xl mx-auto">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">🎯 초기화 옵션</h2>
            <p className="text-gray-600 mb-6">
              Vibe 프로젝트는 3가지 방법으로 초기화할 수 있습니다
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-left">
              <div className="p-4 border rounded-lg">
                <h3 className="font-semibold text-gray-900 mb-2">🎨 Figma 연동</h3>
                <p className="text-sm text-gray-600">디자인 시스템에서 자동 추출</p>
              </div>
              <div className="p-4 border rounded-lg bg-blue-50">
                <h3 className="font-semibold text-gray-900 mb-2">📝 Markdown 기반</h3>
                <p className="text-sm text-gray-600">문서 기반 컴포넌트 정의</p>
              </div>
              <div className="p-4 border rounded-lg bg-green-50">
                <h3 className="font-semibold text-gray-900 mb-2">📋 템플릿 (현재)</h3>
                <p className="text-sm text-gray-600">미리 정의된 컴포넌트 세트</p>
              </div>
            </div>
            <div className="mt-6">
              <Button variant="outline" onClick={() => alert('npm run init 명령어로 다시 초기화할 수 있습니다')}>
                다른 방법으로 초기화하기
              </Button>
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
