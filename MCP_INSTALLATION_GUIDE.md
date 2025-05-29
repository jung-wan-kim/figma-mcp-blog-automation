# MCP 설치 가이드

이 가이드는 Claude Code에서 연결 성공한 MCP 서버들의 설치 및 설정 방법을
정리합니다.

## 연결 성공한 MCP 서버 목록

- ✅ context7
- ✅ figma-local
- ✅ playwright
- ✅ sequential-thinking
- ✅ TalkToFigma

## 1. Context7 MCP 서버

### 설치

```bash
cd context7-mcp-server
npm install
```

### 실행

```bash
node server.js
```

### 기능

- 컨텍스트 검색, 생성, 업데이트, 삭제
- 컨텍스트 간 링크 생성

## 2. Figma Local MCP 서버

### 설치

figma-local은 Claude Code에 내장된 MCP 서버입니다.

### 기능

- Figma 파일의 디자인 변경사항 감지
- 컴포넌트 정보 추출
- 디자인 토큰 추출
- 컴포넌트 JSON 생성

## 3. Playwright MCP 서버

### 설치

playwright는 Claude Code에 내장된 MCP 서버입니다.

### 기능

- 브라우저 자동화
- 웹 페이지 스크린샷
- 웹 요소 클릭, 타이핑, 호버
- 페이지 네비게이션
- 테스트 코드 생성

## 4. Sequential Thinking MCP 서버

### 설치

sequential-thinking은 Claude Code에 내장된 MCP 서버입니다.

### 기능

- 단계별 사고 과정 처리
- 복잡한 문제 해결을 위한 순차적 분석
- 가설 생성 및 검증

## 5. TalkToFigma MCP 서버

### 설치

TalkToFigma는 Claude Code에 내장된 MCP 서버입니다.

### 기능

- Figma 문서 정보 조회
- Figma 요소 생성 (사각형, 프레임, 텍스트)
- Figma 요소 수정 (색상, 위치, 크기)
- Figma 요소 복제 및 삭제
- 컴포넌트 인스턴스 생성
- 이미지 내보내기

## 설정 확인

MCP 서버 연결 상태는 다음 명령어로 확인할 수 있습니다:

```bash
mcp
```

## 문제 해결

연결에 실패한 MCP 서버가 있는 경우, 디버그 모드로 실행하여 오류 로그를 확인할 수
있습니다:

```bash
claude --mcp-debug
```

또는 로그 파일을 직접 확인할 수 있습니다:

```
/Users/jung-wankim/Library/Caches/claude-cli-nodejs/-Users-jung-wankim-Project-Claude-figma-mcp-nextjs-supabase
```
