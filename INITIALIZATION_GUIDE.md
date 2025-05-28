# 🚀 프로젝트 초기화 가이드

Vibe 프로젝트는 3가지 방법으로 초기화할 수 있습니다. 각 방법은 서로 다른 사용 사례에 최적화되어 있습니다.

---

## 🎯 초기화 방법 선택

### 1️⃣ 🎨 Figma 연동으로 시작

**언제 사용하나요?**
- 이미 Figma에 디자인 시스템이 구축되어 있는 경우
- 디자이너와 개발자 간 실시간 동기화가 필요한 경우
- 디자인 변경사항을 자동으로 코드에 반영하고 싶은 경우

**장점:**
- ✅ 실제 디자인에서 컴포넌트 자동 추출
- ✅ 디자인 토큰 자동 동기화
- ✅ 디자인 변경사항 실시간 감지
- ✅ 디자이너-개발자 협업 최적화

**필요 사항:**
- Figma Personal Access Token
- Figma 파일 키
- 컴포넌트가 정의된 Figma 파일

### 2️⃣ 📝 Markdown 파일 기반으로 시작

**언제 사용하나요?**
- 컴포넌트 명세를 문서로 먼저 정의하고 싶은 경우
- 팀 내 컴포넌트 표준을 문서화하여 관리하는 경우
- Figma 없이도 체계적인 컴포넌트 개발을 하고 싶은 경우

**장점:**
- ✅ 문서 기반의 명확한 컴포넌트 명세
- ✅ 버전 관리 가능한 컴포넌트 정의
- ✅ 개발자 친화적인 텍스트 기반 관리
- ✅ 팀 협업 및 리뷰 용이

**필요 사항:**
- 컴포넌트 명세가 작성된 Markdown 파일
- 표준 형식을 따르는 문서 구조

### 3️⃣ 📋 템플릿에서 시작

**언제 사용하나요?**
- 빠르게 프로토타입을 만들고 싶은 경우
- 일반적인 UI 패턴으로 시작하고 싶은 경우
- 학습 목적이나 데모 제작이 필요한 경우

**장점:**
- ✅ 즉시 사용 가능한 컴포넌트 세트
- ✅ 빠른 프로토타이핑 가능
- ✅ 모범 사례가 적용된 구조
- ✅ 다양한 도메인별 템플릿 제공

**필요 사항:**
- 없음 (바로 시작 가능)

---

## 🛠️ 초기화 실행 방법

### 대화형 선택 (권장)

```bash
npm run init
```

이 명령어는 대화형 인터페이스를 통해 초기화 방법을 선택할 수 있습니다.

### 직접 방법 선택

원하는 방법을 미리 알고 있다면 직접 실행할 수 있습니다:

```bash
# Figma 연동
npm run init:figma

# Markdown 파일 기반  
npm run init:markdown

# 템플릿 기반
npm run init:template
```

---

## 📋 초기화 과정 상세

### 🎨 1. Figma 연동 초기화

```bash
npm run init:figma
```

**단계별 과정:**

1. **Figma 인증 정보 입력**
   - Figma Personal Access Token
   - Figma 파일 키
   - 자동 동기화 설정 여부

2. **Figma 파일 분석**
   - 컴포넌트 자동 감지
   - 디자인 토큰 추출
   - 스타일 가이드 생성

3. **코드 생성**
   - React 컴포넌트 자동 생성
   - TypeScript 타입 정의
   - Tailwind CSS 클래스 매핑

4. **워크플로우 설정**
   - Figma 동기화 워크플로우 생성
   - 자동화 스케줄 설정

**생성되는 파일:**
```
src/components/generated/
├── Button.tsx
├── Card.tsx  
├── Modal.tsx
└── index.ts

figma-mcp-server/.env
workflows/figma-sync.yaml
```

### 📝 2. Markdown 기반 초기화

```bash
npm run init:markdown
```

**단계별 과정:**

1. **Markdown 파일 선택**
   - 컴포넌트 명세 파일 경로 지정
   - 파일 형식 선택 (표준/Storybook/JSON-like)

2. **문서 파싱**
   - 컴포넌트 정의 추출
   - Props 및 타입 분석
   - 예시 코드 파싱

3. **코드 생성**
   - 명세에 따른 컴포넌트 생성
   - 문서화된 Props 반영
   - 예시 코드 기반 사용법 생성

**Markdown 형식 예시:**

```markdown
## Button

기본 버튼 컴포넌트입니다.

### Props

- **variant**: `'primary' | 'secondary' | 'outline'` - 버튼 스타일 (기본값: 'primary')
- **size**: `'small' | 'medium' | 'large'` - 버튼 크기 (기본값: 'medium')
- **onClick**: `() => void` - 클릭 이벤트 핸들러

### Examples

```tsx
<Button variant="primary" size="medium">
  클릭하세요
</Button>
```
```

**생성되는 파일:**
```
src/components/generated/
├── Button.tsx
├── Card.tsx
├── Input.tsx
└── index.ts

workflows/markdown-sync.yaml
```

### 📋 3. 템플릿 기반 초기화

```bash
npm run init:template
```

**단계별 과정:**

1. **템플릿 선택**
   - 기본 UI 템플릿 (Button, Card, Input 등)
   - 대시보드 템플릿 (Chart, Table, Sidebar 등)
   - 이커머스 템플릿 (ProductCard, Cart 등)

2. **기능 선택**
   - 다크 모드 지원
   - 애니메이션 효과
   - 접근성 기능
   - 테스트 코드

3. **컴포넌트 생성**
   - 선택한 템플릿의 컴포넌트 생성
   - 기능별 추가 코드 적용
   - 스타일 시스템 설정

**사용 가능한 템플릿:**

| 템플릿 | 포함 컴포넌트 | 적합한 용도 |
|-------|--------------|------------|
| **기본 UI** | Button, Card, Input, Modal, Badge | 일반적인 웹 애플리케이션 |
| **대시보드** | Chart, Table, Sidebar, Stats, KPI | 관리자 대시보드 |
| **이커머스** | ProductCard, Cart, Checkout, Rating | 온라인 쇼핑몰 |

**생성되는 파일:**
```
src/components/generated/
├── Button.tsx
├── Card.tsx
├── Input.tsx
├── Modal.tsx
├── Badge.tsx
└── index.ts

src/styles/generated.css
workflows/template-development.yaml
```

---

## 🔧 초기화 후 설정

### 환경 변수 설정

초기화 방법에 따라 필요한 환경 변수가 다릅니다:

**Figma 연동:**
```env
FIGMA_TOKEN=figd_your_token_here
FIGMA_FILE_KEY=your_file_key_here
AUTO_SYNC=true
```

**Markdown 기반:**
```env
COMPONENT_SPEC_PATH=./docs/components.md
SPEC_FORMAT=standard
```

**템플릿 기반:**
```env
TEMPLATE_TYPE=basic
FEATURES=darkMode,animations
```

### 워크플로우 활성화

생성된 워크플로우를 활성화하여 자동화를 시작할 수 있습니다:

```bash
# 통합 테스트 실행
npm run test:integration

# 워크플로우 실행
npm run orchestrate YOUR_FIGMA_FILE_KEY  # Figma 연동의 경우
```

### 개발 서버 시작

```bash
# Next.js 개발 서버
npm run dev

# 실시간 대시보드
npm run dashboard:server
```

---

## 🔄 방법 변경하기

초기화 후에도 다른 방법으로 전환할 수 있습니다:

### Figma → Markdown

```bash
# 현재 컴포넌트를 Markdown으로 문서화
npm run export:markdown

# 새로운 Markdown 기반 초기화
npm run init:markdown
```

### Template → Figma

```bash
# 템플릿 컴포넌트를 Figma와 연동
npm run connect:figma
```

### 하이브리드 방식

여러 방식을 조합하여 사용할 수도 있습니다:

```bash
# 1. 템플릿으로 빠른 시작
npm run init:template

# 2. Figma 연동 추가
npm run add:figma-sync

# 3. Markdown 문서화
npm run add:markdown-docs
```

---

## 💡 Best Practices

### 팀 협업 시 권장사항

1. **Figma 연동**: 디자이너와 긴밀한 협업이 필요한 프로젝트
2. **Markdown 기반**: 컴포넌트 표준화가 중요한 대규모 팀
3. **템플릿 기반**: 빠른 프로토타이핑이나 학습 목적

### 프로젝트 단계별 추천

| 프로젝트 단계 | 추천 방법 | 이유 |
|-------------|----------|-----|
| **기획/설계** | Markdown | 컴포넌트 명세 문서화 |
| **디자인** | Figma 연동 | 실시간 디자인 반영 |
| **프로토타입** | 템플릿 | 빠른 검증 |
| **개발** | Figma + Markdown | 하이브리드 접근 |
| **유지보수** | Figma 연동 | 자동화된 업데이트 |

---

## 🆘 문제 해결

초기화 과정에서 문제가 발생하면:

1. **의존성 설치 확인**
   ```bash
   npm install
   ```

2. **권한 문제**
   ```bash
   chmod +x bin/vibe-init.js
   ```

3. **환경 변수 확인**
   - `.env` 파일이 올바르게 설정되었는지 확인

4. **상세 오류 로그**
   ```bash
   DEBUG=true npm run init
   ```

더 많은 도움이 필요하면 [TROUBLESHOOTING.md](./TROUBLESHOOTING.md)를 참조하세요.

---

*마지막 업데이트: 2025-05-28*