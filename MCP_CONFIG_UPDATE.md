# MCP 서버 설정 업데이트

## 변경 내용 (2025-05-29)

### 1. browser-tools-mcp → browser-tools

- 기존: 로컬 서버 파일 실행
- 변경: npx로 @browserbasehq/mcp-browser-tools 실행
- 이유: 로컬 서버 연결 타임아웃 문제 해결

### 2. server-sequential-thinking 추가

- 새로 추가된 MCP 서버
- npx로 @modelcontextprotocol/server-sequential-thinking 실행
- 기능: 단계별 사고 과정 처리, 복잡한 문제 해결

## 현재 활성 MCP 서버

1. **terminal** - 터미널 명령어 실행
2. **Framelink Figma MCP** - Figma 파일 정보 조회
3. **TalkToFigma** - Figma 요소 생성/수정
4. **context7** - 컨텍스트 관리 (로컬 서버)
5. **browser-tools** - 브라우저 자동화
6. **server-sequential-thinking** - 순차적 사고 처리

## 설정 파일 위치

```
/Users/jung-wankim/Library/Application Support/Claude/claude_desktop_config.json
```

## 확인 방법

```bash
# MCP 서버 상태 확인
mcp

# 디버그 모드로 실행
claude --mcp-debug
```
