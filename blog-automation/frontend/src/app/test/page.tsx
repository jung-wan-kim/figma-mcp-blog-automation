import Link from 'next/link';

export default function TestPage() {
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <h1 className="text-3xl font-bold">테스트 페이지</h1>
      <p className="mt-4">이 페이지가 보인다면 Next.js는 정상 작동 중입니다.</p>
      <Link href="/" className="mt-4 inline-block text-blue-500 hover:underline">
        메인 페이지로 이동
      </Link>
    </div>
  );
}
