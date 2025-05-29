# Browser Tools MCP Server

브라우저 자동화 및 웹 상호작용을 위한 MCP 서버입니다.

## 🎯 주요 기능

### 웹 네비게이션

- **navigate**: 웹 페이지로 이동
- **get_page_info**: 현재 페이지 정보 수집

### 요소 상호작용

- **click**: 웹 요소 클릭
- **type**: 텍스트 입력
- **get_text**: 요소 텍스트 추출
- **wait_for_element**: 요소 대기

### 고급 기능

- **screenshot**: 페이지 스크린샷 캡처
- **evaluate_js**: JavaScript 실행

## 🚀 사용법

### 서버 시작

```bash
cd browser-tools-mcp-server
npm install
npm start
```

### 환경변수 설정

```bash
# .env 파일에 추가
BROWSER_TOOLS_MCP_PORT=3007
```

### MCP 도구 호출 예시

#### 페이지 이동

```json
{
  "name": "navigate",
  "arguments": {
    "url": "https://example.com"
  }
}
```

#### 요소 클릭

```json
{
  "name": "click",
  "arguments": {
    "selector": "#submit-button"
  }
}
```

#### 텍스트 입력

```json
{
  "name": "type",
  "arguments": {
    "selector": "#email-input",
    "text": "user@example.com"
  }
}
```

#### 스크린샷 캡처

```json
{
  "name": "screenshot",
  "arguments": {
    "filename": "page-capture.png"
  }
}
```

## 🔧 통합 정보

### Figma 자동화 워크플로우 연동

- Figma 디자인 변경 감지 시 자동으로 관련 웹 페이지 테스트
- 디자인 시스템 문서 자동 업데이트
- 컴포넌트 라이브러리 웹사이트 자동 갱신

### GitHub 연동

- PR 생성 시 자동 테스트 실행
- 브라우저 테스트 결과를 GitHub 이슈로 자동 보고

### Dashboard 연동

- 브라우저 테스트 결과 실시간 모니터링
- 웹 페이지 성능 메트릭 수집

## 📊 로깅

모든 브라우저 작업은 구조화된 로그로 기록됩니다:

- 네비게이션 이벤트
- 요소 상호작용
- 성능 메트릭
- 오류 및 예외

## 🔐 보안 고려사항

- 신뢰할 수 있는 도메인에서만 실행
- 민감한 정보 입력 시 로그에서 자동 마스킹
- HTTPS 연결 권장

## 🤝 다른 MCP 서버와의 연동

이 서버는 다음 MCP 서버들과 함께 작동합니다:

- **Figma MCP**: 디자인 변경 감지 → 브라우저 테스트 실행
- **GitHub MCP**: 코드 변경 → 브라우저 테스트 → PR 업데이트
- **Supabase MCP**: 테스트 결과 저장 및 이력 관리
- **Dashboard MCP**: 실시간 테스트 현황 모니터링
