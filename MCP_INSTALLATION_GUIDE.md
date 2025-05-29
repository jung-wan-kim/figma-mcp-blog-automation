# MCP 설치 가이드

이 가이드는 Claude Code에서 연결 성공한 MCP 서버들의 설치 및 설정 방법을
정리합니다.

## 연결 성공한 MCP 서버 목록

- ✅ context7
- ✅ Framelink Figma MCP
- ✅ TalkToFigma
- ✅ terminal
- ✅ browser-tools
- ✅ server-sequential-thinking

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

## 2. Framelink Figma MCP 서버

### 설치

```bash
npx -y figma-developer-mcp --figma-api-key=<YOUR_API_KEY> --stdio
```

### 기능

- Figma 파일의 레이아웃 정보 조회
- SVG 및 PNG 이미지 다운로드
- 노드 정보 추출

## 3. TalkToFigma MCP 서버

### 설치

```bash
bunx cursor-talk-to-figma-mcp@latest --server=vps.sonnylab.com
```

### 기능

- Figma 문서 정보 조회
- Figma 요소 생성 (사각형, 프레임, 텍스트)
- Figma 요소 수정 (색상, 위치, 크기)
- Figma 요소 복제 및 삭제
- 컴포넌트 인스턴스 생성
- 이미지 내보내기

## 4. Terminal MCP 서버

### 설치

```bash
npx iterm_mcp_server
```

### 기능

- 터미널 인스턴스 생성 및 관리
- 명령어 실행
- 출력 읽기
- 터미널 세션 관리

## 5. Browser Tools MCP 서버

### 설치

```bash
npx -y @browserbasehq/mcp-browser-tools
```

### 기능

- 브라우저 자동화
- 웹 페이지 스크린샷
- 웹 요소 클릭, 타이핑
- 페이지 네비게이션
- 콘솔 로그 확인

## 6. Server Sequential Thinking MCP 서버

### 설치

```bash
npx -y @modelcontextprotocol/server-sequential-thinking
```

### 기능

- 단계별 사고 과정 처리
- 복잡한 문제 해결을 위한 순차적 분석
- 가설 생성 및 검증
- 추론 과정 저장 및 관리

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
/Users/jung-wankim/Library/Caches/claude-cli-nodejs/-Users-jung-wankim-Project-vibe
```

## Claude Desktop 설정 파일 위치

```
/Users/jung-wankim/Library/Application Support/Claude/claude_desktop_config.json
```
