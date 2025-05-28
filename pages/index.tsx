import React from 'react'
import Link from 'next/link'
import { Card } from '../src/components/generated/Card'
import { Button } from '../src/components/generated/Button'

export default function Home() {
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
            Figma MCP + Next.js + Supabase
          </h1>
          <p className="text-xl text-gray-600 mb-12">
            자동화 시스템 대시보드
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <Card variant="elevated" padding="large">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">Generated Components</h2>
            <p className="text-gray-600 mb-4">Figma에서 생성된 컴포넌트들</p>
            <div className="space-y-4">
              <Button>Sample Button</Button>
            </div>
          </Card>
          
          <Card variant="elevated" padding="large">
            <h2 className="text-xl font-semibold text-gray-900 mb-2">시스템 상태</h2>
            <p className="text-gray-600 mb-4">현재 시스템 상태를 확인하세요</p>
            <div className="text-sm text-gray-600 mb-4">
              <p>• MCP 서버: 활성</p>
              <p>• Figma 연동: 준비됨</p>
              <p>• Supabase 연결: 준비됨</p>
            </div>
            <Link href="/dashboard">
              <Button variant="primary">실시간 대시보드 보기</Button>
            </Link>
          </Card>
        </div>
      </div>
    </div>
  )
}
