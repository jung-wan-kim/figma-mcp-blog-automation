# UI 컴포넌트 명세서

이 문서는 Vibe 프로젝트에서 사용하는 UI 컴포넌트들을 정의합니다.

---

## Button

사용자 상호작용을 위한 기본 버튼 컴포넌트입니다. 다양한 스타일과 크기를 지원하며, 접근성을 고려하여 설계되었습니다.

### Props

- **variant**: `'primary' | 'secondary' | 'outline' | 'ghost'` - 버튼 스타일 (기본값: 'primary')
- **size**: `'xs' | 'sm' | 'md' | 'lg' | 'xl'` - 버튼 크기 (기본값: 'md')
- **disabled**: `boolean` - 비활성화 여부 (기본값: false)
- **loading**: `boolean` - 로딩 상태 표시 (기본값: false)
- **fullWidth**: `boolean` - 전체 너비 사용 (기본값: false)
- **onClick**: `() => void` - 클릭 이벤트 핸들러

### Variants

- **primary**: 기본 파란색 버튼, 주요 액션에 사용
- **secondary**: 회색 배경의 보조 버튼, 일반적인 액션에 사용
- **outline**: 테두리만 있는 버튼, 덜 중요한 액션에 사용
- **ghost**: 배경이 투명한 버튼, 텍스트 링크와 유사

### Examples

```tsx
// 기본 사용법
<Button variant="primary" size="md">
  확인
</Button>

// 로딩 상태
<Button variant="primary" loading>
  저장 중...
</Button>

// 전체 너비 버튼
<Button variant="outline" fullWidth onClick={() => alert('클릭!')}>
  전체 너비 버튼
</Button>

// 비활성화 상태
<Button variant="secondary" disabled>
  비활성화
</Button>
```

---

## Card

콘텐츠를 그룹화하고 시각적으로 구분하는 카드 컴포넌트입니다.

### Props

- **variant**: `'default' | 'elevated' | 'outlined' | 'filled'` - 카드 스타일 (기본값: 'default')
- **padding**: `'none' | 'sm' | 'md' | 'lg' | 'xl'` - 내부 여백 (기본값: 'md')
- **radius**: `'none' | 'sm' | 'md' | 'lg' | 'full'` - 모서리 둥글기 (기본값: 'md')
- **shadow**: `'none' | 'sm' | 'md' | 'lg' | 'xl'` - 그림자 크기 (기본값: 'sm')
- **hoverable**: `boolean` - 호버 효과 활성화 (기본값: false)

### Variants

- **default**: 기본 흰색 배경의 카드
- **elevated**: 그림자가 강조된 카드
- **outlined**: 테두리가 있는 카드
- **filled**: 배경색이 있는 카드

### Examples

```tsx
// 기본 카드
<Card variant="default" padding="lg">
  <h3>카드 제목</h3>
  <p>카드 내용입니다.</p>
</Card>

// 호버 효과가 있는 카드
<Card variant="elevated" hoverable>
  <img src="image.jpg" alt="이미지" />
  <div>
    <h4>제목</h4>
    <p>설명</p>
  </div>
</Card>
```

---

## Input

사용자 입력을 받는 텍스트 필드 컴포넌트입니다.

### Props

- **type**: `'text' | 'email' | 'password' | 'number' | 'tel' | 'url'` - 입력 타입 (기본값: 'text')
- **size**: `'sm' | 'md' | 'lg'` - 입력 필드 크기 (기본값: 'md')
- **variant**: `'default' | 'filled' | 'outlined'` - 입력 필드 스타일 (기본값: 'default')
- **placeholder**: `string` - 플레이스홀더 텍스트
- **disabled**: `boolean` - 비활성화 여부 (기본값: false)
- **required**: `boolean` - 필수 입력 여부 (기본값: false)
- **error**: `boolean` - 오류 상태 (기본값: false)
- **helperText**: `string` - 도움말 텍스트
- **value**: `string` - 입력값
- **onChange**: `(value: string) => void` - 값 변경 이벤트 핸들러

### Examples

```tsx
// 기본 입력 필드
<Input 
  type="text" 
  placeholder="이름을 입력하세요"
  value={name}
  onChange={setName}
/>

// 오류 상태 입력 필드
<Input 
  type="email" 
  placeholder="이메일"
  value={email}
  onChange={setEmail}
  error
  helperText="올바른 이메일 형식을 입력하세요"
/>

// 필수 입력 필드
<Input 
  type="password" 
  placeholder="비밀번호"
  required
  helperText="8자 이상 입력하세요"
/>
```

---

## Modal

사용자의 주의를 집중시키고 추가 정보나 액션을 제공하는 모달 컴포넌트입니다.

### Props

- **open**: `boolean` - 모달 표시 여부 (기본값: false)
- **size**: `'sm' | 'md' | 'lg' | 'xl' | 'full'` - 모달 크기 (기본값: 'md')
- **closable**: `boolean` - 닫기 버튼 표시 여부 (기본값: true)
- **closeOnOverlay**: `boolean` - 오버레이 클릭 시 닫기 (기본값: true)
- **title**: `string` - 모달 제목
- **onClose**: `() => void` - 모달 닫기 이벤트 핸들러

### Examples

```tsx
// 기본 모달
<Modal 
  open={isOpen}
  title="확인"
  onClose={() => setIsOpen(false)}
>
  <p>정말로 삭제하시겠습니까?</p>
  <div>
    <Button variant="outline" onClick={() => setIsOpen(false)}>
      취소
    </Button>
    <Button variant="primary" onClick={handleDelete}>
      삭제
    </Button>
  </div>
</Modal>

// 큰 모달
<Modal 
  open={isDetailOpen}
  size="lg"
  title="상세 정보"
  onClose={() => setIsDetailOpen(false)}
>
  <DetailForm />
</Modal>
```

---

## Badge

상태나 카테고리를 표시하는 작은 라벨 컴포넌트입니다.

### Props

- **variant**: `'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error'` - 배지 스타일 (기본값: 'default')
- **size**: `'sm' | 'md' | 'lg'` - 배지 크기 (기본값: 'md')
- **dot**: `boolean` - 점 모양 배지 (기본값: false)

### Examples

```tsx
// 기본 배지
<Badge variant="primary">새로운</Badge>

// 상태 배지
<Badge variant="success">완료</Badge>
<Badge variant="warning">대기</Badge>
<Badge variant="error">오류</Badge>

// 점 배지
<Badge variant="primary" dot />
```

---

## Avatar

사용자나 객체를 시각적으로 표현하는 아바타 컴포넌트입니다.

### Props

- **src**: `string` - 이미지 URL
- **alt**: `string` - 이미지 대체 텍스트
- **size**: `'xs' | 'sm' | 'md' | 'lg' | 'xl'` - 아바타 크기 (기본값: 'md')
- **name**: `string` - 이름 (이니셜 표시용)
- **variant**: `'circular' | 'rounded' | 'square'` - 모양 (기본값: 'circular')

### Examples

```tsx
// 이미지 아바타
<Avatar 
  src="https://example.com/avatar.jpg" 
  alt="사용자 아바타"
  size="lg"
/>

// 이니셜 아바타
<Avatar 
  name="김철수" 
  size="md"
  variant="circular"
/>

// 그룹 아바타
<div className="flex -space-x-2">
  <Avatar src="avatar1.jpg" size="sm" />
  <Avatar src="avatar2.jpg" size="sm" />
  <Avatar name="김철수" size="sm" />
</div>
```

---

## Table

데이터를 표 형태로 표시하는 테이블 컴포넌트입니다.

### Props

- **columns**: `Array<{ key: string, title: string, width?: string }>` - 테이블 컬럼 정의
- **data**: `Array<Record<string, any>>` - 테이블 데이터
- **loading**: `boolean` - 로딩 상태 (기본값: false)
- **striped**: `boolean` - 줄무늬 표시 (기본값: false)
- **hoverable**: `boolean` - 행 호버 효과 (기본값: true)
- **onRowClick**: `(row: any) => void` - 행 클릭 이벤트 핸들러

### Examples

```tsx
const columns = [
  { key: 'name', title: '이름' },
  { key: 'email', title: '이메일' },
  { key: 'role', title: '역할', width: '120px' }
];

const data = [
  { name: '김철수', email: 'kim@example.com', role: '관리자' },
  { name: '이영희', email: 'lee@example.com', role: '사용자' }
];

<Table 
  columns={columns}
  data={data}
  striped
  onRowClick={(row) => console.log('클릭된 행:', row)}
/>
```

---

## Tabs

콘텐츠를 탭으로 구분하여 표시하는 탭 컴포넌트입니다.

### Props

- **tabs**: `Array<{ key: string, label: string, content: React.ReactNode }>` - 탭 정의
- **activeTab**: `string` - 활성 탭 키
- **onTabChange**: `(key: string) => void` - 탭 변경 이벤트 핸들러
- **variant**: `'default' | 'pills' | 'underline'` - 탭 스타일 (기본값: 'default')

### Examples

```tsx
const tabs = [
  { 
    key: 'profile', 
    label: '프로필', 
    content: <ProfileForm /> 
  },
  { 
    key: 'settings', 
    label: '설정', 
    content: <SettingsPanel /> 
  }
];

<Tabs 
  tabs={tabs}
  activeTab={activeTab}
  onTabChange={setActiveTab}
  variant="underline"
/>
```