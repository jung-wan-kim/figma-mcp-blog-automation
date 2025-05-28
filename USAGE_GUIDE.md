# 📋 Vibe 자동화 시스템 사용 가이드

## 🎯 개요

이 가이드는 Figma 디자인 변경사항을 자동으로 감지하여 React 컴포넌트를 생성하고 GitHub에 배포하는 완전 자동화 시스템의 사용법을 설명합니다.

## 🏗️ 시스템 아키텍처

```
Figma Design → MCP Servers → React Components → GitHub → Deployment
     ↓              ↓              ↓           ↓         ↓
 디자인 변경     자동 감지      컴포넌트 생성   PR 생성   자동 배포
```

---

## 🚀 1단계: 초기 설정

### 1.1 프로젝트 클론

```bash
git clone https://github.com/jung-wan-kim/figma-mcp-nextjs-supabase.git
cd figma-mcp-nextjs-supabase
```

### 1.2 자동 설정 실행

```bash
npm run setup
```

이 명령어는 다음 작업을 수행합니다:
- 모든 의존성 설치
- 필요한 디렉토리 생성
- 환경 변수 템플릿 파일 생성

---

## 🔑 2단계: API 키 설정

### 2.1 Figma API 토큰 설정

1. [Figma 개발자 설정](https://www.figma.com/developers/api#access-tokens)에서 Personal Access Token 생성
2. `figma-mcp-server/.env` 파일 편집:

```env
FIGMA_TOKEN=figd_your_figma_token_here
FIGMA_FILE_KEY=your_figma_file_key_here
```

**Figma File Key 찾는 방법:**
- Figma 파일 URL: `https://www.figma.com/file/ABC123DEF456/My-Design`
- File Key: `ABC123DEF456`

### 2.2 GitHub API 토큰 설정

1. [GitHub Personal Access Tokens](https://github.com/settings/tokens) 페이지에서 토큰 생성
2. **필수 권한**: `repo`, `workflow`
3. `github-mcp-server/.env` 파일 편집:

```env
GITHUB_TOKEN=ghp_your_github_token_here
DEFAULT_REPOSITORY=your-username/your-repo
```

### 2.3 Supabase 설정 (선택사항)

1. [Supabase](https://supabase.com)에서 프로젝트 생성
2. `supabase-mcp-server/.env` 파일 편집:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key_here
```

---

## 🧪 3단계: 시스템 테스트

### 3.1 통합 테스트 실행

```bash
npm run test:integration
```

**예상 결과:**
```
🧪 MCP 서버 통합 테스트 시작
✅ TaskManager: 성공
✅ Figma: 성공  
✅ GitHub: 성공
✅ Supabase: 성공
✅ Dashboard: 성공
📊 테스트 결과 요약: 성공 5/5
```

### 3.2 개별 MCP 서버 테스트

각 서버를 개별적으로 테스트할 수 있습니다:

```bash
# TaskManager MCP 서버
npm run mcp:taskmanager

# Figma MCP 서버  
npm run mcp:figma

# GitHub MCP 서버
npm run mcp:github

# Supabase MCP 서버
npm run mcp:supabase

# Dashboard MCP 서버
npm run mcp:dashboard
```

---

## 🎨 4단계: Figma 파일 준비

### 4.1 디자인 시스템 구조 준비

Figma 파일에서 다음 구조를 권장합니다:

```
📁 Design System
├── 🎨 Colors (색상 토큰)
├── 📝 Typography (타이포그래피)
├── 🧩 Components
│   ├── Button
│   ├── Card  
│   ├── Input
│   └── Modal
└── 📐 Spacing (간격 토큰)
```

### 4.2 컴포넌트 명명 규칙

- **컴포넌트 이름**: PascalCase (예: `Button`, `InputField`)
- **변형(Variants)**: camelCase (예: `primary`, `secondary`)
- **속성(Properties)**: camelCase (예: `size`, `variant`)

### 4.3 컴포넌트 설명 추가

각 컴포넌트에 설명을 추가하면 자동 생성된 코드에 JSDoc 주석으로 포함됩니다.

---

## 🚀 5단계: 자동화 워크플로우 실행

### 5.1 웹 대시보드 시작

실시간 모니터링을 위해 대시보드를 시작합니다:

```bash
npm run dashboard:server
```

브라우저에서 http://localhost:3000/dashboard 접속하여 실시간 상태를 확인할 수 있습니다.

### 5.2 완전 자동화 실행

```bash
npm run orchestrate YOUR_FIGMA_FILE_KEY
```

**실행 예시:**
```bash
npm run orchestrate ABC123DEF456
```

### 5.3 실행 과정 모니터링

터미널에서 다음과 같은 진행 상황을 확인할 수 있습니다:

```
🚀 Starting Complete Automation Workflow
📋 Figma File: ABC123DEF456

📊 Step 1: Detecting Figma Changes...
🎨 Step 2: Extracting Components...
⚡ Step 3: Generating React Components...
🌿 Step 4: Creating GitHub Branch...
💾 Step 5: Committing Files...
📝 Step 6: Creating Pull Request...
💾 Step 7: Saving Metadata...
📱 Step 8: Sending Notifications...

✅ Workflow Completed Successfully!
⏱️ Total Duration: 45.2s
```

---

## 📊 6단계: 결과 확인

### 6.1 생성된 파일 확인

자동화 실행 후 다음 파일들이 생성됩니다:

```
src/components/generated/
├── Button.tsx         # 버튼 컴포넌트
├── Card.tsx          # 카드 컴포넌트  
├── InputField.tsx    # 입력 필드 컴포넌트
└── index.ts          # 컴포넌트 내보내기
```

### 6.2 생성된 컴포넌트 예시

```typescript
import React from 'react';

interface ButtonProps {
  children: React.ReactNode;
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'small' | 'medium' | 'large';
  onClick?: () => void;
  disabled?: boolean;
}

/**
 * Button component
 * Auto-generated from Figma
 * 기본 버튼 컴포넌트
 */
export const Button: React.FC<ButtonProps> = ({ 
  children,
  variant = 'primary',
  size = 'medium',
  onClick,
  disabled = false
}) => {
  return (
    <button 
      className={`${baseClasses} ${variantClasses} ${sizeClasses}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
};
```

### 6.3 GitHub Pull Request 확인

1. GitHub 저장소에서 새로운 PR 확인
2. PR 제목: `🎨 Design System Update from Figma`
3. 변경사항 리뷰 및 머지

---

## 🔄 7단계: 반복 사용

### 7.1 디자인 변경 감지

Figma에서 디자인을 변경한 후:

1. 24시간 이내 변경사항은 자동으로 감지됩니다
2. 수동으로 즉시 실행하려면 다시 orchestrate 명령어 실행

### 7.2 Webhook 설정 (고급)

실시간 자동화를 위해 Figma Webhook을 설정할 수 있습니다:

1. Figma 플러그인에서 Webhook URL 설정
2. 엔드포인트: `https://your-domain.com/webhook/figma`
3. 디자인 변경 시 자동으로 워크플로우 실행

---

## 📱 8단계: 대시보드 활용

### 8.1 실시간 모니터링

웹 대시보드에서 확인할 수 있는 정보:

- **워크플로우 메트릭**: 실행 중/완료/실패 수
- **컴포넌트 메트릭**: 생성/업데이트된 컴포넌트 수  
- **성능 메트릭**: 평균 실행 시간, 성공률
- **실시간 알림**: 워크플로우 상태 변경 알림

### 8.2 알림 설정

대시보드에서 다음 알림을 받을 수 있습니다:

- ✅ 워크플로우 성공 완료
- ❌ 워크플로우 실행 실패  
- 📝 새로운 PR 생성
- 🎨 컴포넌트 업데이트

---

## 🛠️ 9단계: 고급 설정

### 9.1 워크플로우 커스터마이징

`workflows/` 디렉토리에서 YAML 파일을 편집하여 커스텀 워크플로우를 만들 수 있습니다:

```yaml
name: "Custom Figma Sync"
description: "커스텀 Figma 동기화 워크플로우"

steps:
  - id: detect_changes
    name: "디자인 변경 감지"
    mcp: figma-mcp
    action: detect-design-changes
    params:
      fileKey: "${input.figmaFileKey}"
      
  - id: generate_components  
    name: "컴포넌트 생성"
    mcp: figma-mcp
    action: extract-components
    params:
      fileKey: "${input.figmaFileKey}"
      
  - id: create_pr
    name: "GitHub PR 생성"
    mcp: github-mcp
    action: create-pull-request
    params:
      repository: "${input.repository}"
      title: "🎨 Design Update: ${results.detect_changes.summary}"
```

### 9.2 환경별 설정

개발/스테이징/프로덕션 환경별로 다른 설정을 사용할 수 있습니다:

```bash
# 개발 환경
cp .env.development .env

# 프로덕션 환경  
cp .env.production .env
```

---

## 🔧 10단계: 문제 해결

### 10.1 일반적인 오류

**오류: "Figma API 접근 권한이 없습니다"**
```bash
해결방법:
1. FIGMA_TOKEN이 올바른지 확인
2. Figma 파일에 읽기 권한이 있는지 확인
3. 토큰이 만료되지 않았는지 확인
```

**오류: "GitHub API rate limit"**
```bash
해결방법:
1. GitHub 토큰의 권한 확인
2. 다른 GitHub 토큰 사용
3. 요청 간격 조정
```

### 10.2 로그 확인

각 MCP 서버의 로그를 확인할 수 있습니다:

```bash
# TaskManager 로그
tail -f taskmanager-mcp-server/logs/server.log

# Figma MCP 로그  
tail -f figma-mcp-server/logs/server.log
```

### 10.3 디버깅 모드

상세한 디버깅 정보를 보려면:

```bash
DEBUG=true npm run orchestrate YOUR_FIGMA_FILE_KEY
```

---

## 📚 11단계: 참고 자료

### 11.1 API 문서

- [Figma API 문서](https://www.figma.com/developers/api)
- [GitHub API 문서](https://docs.github.com/en/rest)
- [Supabase API 문서](https://supabase.com/docs/reference/javascript)

### 11.2 MCP 서버 문서

각 MCP 서버의 자세한 사용법은 해당 디렉토리의 README.md 파일을 참조하세요:

- `figma-mcp-server/README.md`
- `github-mcp-server/README.md`  
- `supabase-mcp-server/README.md`
- `dashboard-mcp-server/README.md`
- `taskmanager-mcp-server/README.md`

### 11.3 커뮤니티 지원

- **GitHub Issues**: 버그 리포트 및 기능 요청
- **Discussions**: 질문 및 토론
- **Wiki**: 고급 사용법 및 팁

---

## 🎉 완료!

축하합니다! 이제 Figma에서 React까지의 완전 자동화 시스템을 성공적으로 구축했습니다.

### 다음 단계

1. **팀과 공유**: 다른 개발자들에게 사용법 안내
2. **워크플로우 최적화**: 팀의 워크플로우에 맞게 커스터마이징
3. **모니터링**: 대시보드를 통한 지속적인 성능 모니터링
4. **개선**: 사용 패턴에 따른 시스템 개선

---

**💡 팁**: 이 가이드를 북마크하고 팀원들과 공유하세요!

**📞 문의사항**: 문제가 발생하면 GitHub Issues에 남겨주세요.

---

*마지막 업데이트: 2025-05-28*