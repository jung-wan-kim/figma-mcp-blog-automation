# Claude Desktop MCP 설정 가이드

이 프로젝트의 모든 MCP 서버를 Claude Desktop에서 사용하기 위한 설정
가이드입니다.

## 🎯 MCP 서버 목록

프로젝트에 포함된 MCP 서버들:

1. **figma-mcp-server** (포트: 3001) - Figma 디자인 관리
2. **github-mcp-server** (포트: 3002) - GitHub 저장소 관리
3. **taskmanager-mcp-server** (포트: 3003) - 워크플로우 오케스트레이션
4. **supabase-mcp-server** (포트: 3004) - 데이터베이스 관리
5. **dashboard-mcp-server** (포트: 3005) - 실시간 모니터링
6. **context7-mcp-server** (포트: 3006) - 컨텍스트 관리
7. **browser-tools-mcp-server** (포트: 3007) - 브라우저 자동화
8. **playwright** - 웹 브라우저 자동화 및 테스팅

## 📝 Claude Desktop 설정 파일

Claude Desktop의 설정 파일 위치:

- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`

## ⚙️ 설정 파일 내용

아래 JSON 설정을 Claude Desktop 설정 파일에 추가하세요:

```json
{
  "mcpServers": {
    "figma-mcp": {
      "command": "node",
      "args": [
        "/Users/jung-wankim/Project/Claude/figma-mcp-nextjs-supabase/figma-mcp-server/server.js"
      ],
      "env": {
        "FIGMA_TOKEN": "여기에_피그마_토큰_입력",
        "FIGMA_FILE_KEY": "여기에_피그마_파일키_입력"
      }
    },
    "github-mcp": {
      "command": "node",
      "args": [
        "/Users/jung-wankim/Project/Claude/figma-mcp-nextjs-supabase/github-mcp-server/server.js"
      ],
      "env": {
        "GITHUB_TOKEN": "여기에_깃허브_토큰_입력",
        "GITHUB_OWNER": "jung-wan-kim",
        "GITHUB_REPO": "figma-mcp-nextjs-supabase"
      }
    },
    "taskmanager-mcp": {
      "command": "node",
      "args": [
        "/Users/jung-wankim/Project/Claude/figma-mcp-nextjs-supabase/taskmanager-mcp-server/server.js"
      ],
      "env": {
        "NODE_ENV": "production",
        "LOG_LEVEL": "info"
      }
    },
    "supabase-mcp": {
      "command": "node",
      "args": [
        "/Users/jung-wankim/Project/Claude/figma-mcp-nextjs-supabase/supabase-mcp-server/server.js"
      ],
      "env": {
        "SUPABASE_URL": "여기에_supabase_url_입력",
        "SUPABASE_ANON_KEY": "여기에_supabase_anon_key_입력"
      }
    },
    "dashboard-mcp": {
      "command": "node",
      "args": [
        "/Users/jung-wankim/Project/Claude/figma-mcp-nextjs-supabase/dashboard-mcp-server/server.js"
      ],
      "env": {
        "NODE_ENV": "production",
        "LOG_LEVEL": "info"
      }
    },
    "context7-mcp": {
      "command": "node",
      "args": [
        "/Users/jung-wankim/Project/Claude/figma-mcp-nextjs-supabase/context7-mcp-server/server.js"
      ],
      "env": {
        "NODE_ENV": "production",
        "LOG_LEVEL": "info"
      }
    },
    "browser-tools-mcp": {
      "command": "npx",
      "args": [
        "-y",
        "@smithery/cli@latest",
        "run",
        "@diulela/browser-tools-mcp",
        "--key",
        "3e7735c8-b9d5-45ec-a2da-4d5ca70dfc17"
      ]
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@anthropic-ai/mcp-playwright", "--disable-security"]
    }
  }
}
```

## 🔐 환경변수 설정

각 서비스에 필요한 환경변수들을 준비하세요:

### Figma 서비스

1. [Figma 개발자 설정](https://www.figma.com/developers/api#access-tokens)에서
   Personal Access Token 생성
2. `FIGMA_TOKEN` 설정
3. 작업할 Figma 파일의 키를 `FIGMA_FILE_KEY`에 설정

### GitHub 서비스

1. [GitHub Personal Access Token](https://github.com/settings/tokens) 생성
2. `repo`, `workflow`, `write:packages` 권한 필요
3. `GITHUB_TOKEN`, `GITHUB_OWNER`, `GITHUB_REPO` 설정

### Supabase 서비스

1. [Supabase 프로젝트](https://app.supabase.com/) 생성
2. Project Settings → API에서 URL과 anon key 복사
3. `SUPABASE_URL`, `SUPABASE_ANON_KEY` 설정

## 🚀 설정 적용 방법

1. **설정 파일 편집**:

   ```bash
   # macOS
   code ~/Library/Application\ Support/Claude/claude_desktop_config.json

   # 또는 직접 편집
   nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. **경로 수정**: 위 JSON에서 절대 경로를 실제 프로젝트 경로로 변경

3. **환경변수 입력**: 각 서비스의 실제 토큰/키 값 입력

4. **Claude Desktop 재시작**: 설정 적용을 위해 Claude Desktop 앱 재시작

## ✅ 연결 확인

Claude Desktop을 재시작한 후, 채팅에서 다음과 같이 확인할 수 있습니다:

```
/mcp list-tools
```

또는 직접 도구 사용:

```
피그마 파일의 변경사항을 확인해줘
```

## 🔧 문제 해결

### 서버 연결 실패 시

1. **경로 확인**: JSON의 args에 있는 절대 경로가 정확한지 확인
2. **권한 확인**: 파일 실행 권한이 있는지 확인
3. **의존성 확인**: 각 MCP 서버 디렉토리에서 `npm install` 실행
4. **로그 확인**: Claude Desktop 개발자 도구에서 MCP 관련 오류 메시지 확인

### 환경변수 오류 시

1. **토큰 유효성**: API 토큰들이 유효하고 올바른 권한을 가지는지 확인
2. **Figma 파일 키**: Figma URL에서 파일 키를 정확히 추출했는지 확인
3. **GitHub 저장소**: GITHUB_OWNER와 GITHUB_REPO가 실제 저장소와 일치하는지 확인

## 🎉 사용 예시

모든 설정이 완료되면 Claude Desktop에서 다음과 같은 자동화가 가능합니다:

1. **Figma → GitHub 워크플로우**:

   ```
   피그마에서 디자인이 변경되면 자동으로 GitHub에 새 브랜치를 만들고 PR을 생성해줘
   ```

2. **브라우저 자동화**:

   ```
   example.com 사이트에 접속해서 스크린샷을 찍어줘
   ```

3. **Playwright 웹 테스팅**:

   ```
   웹사이트의 로그인 폼을 테스트해줘
   ```

4. **통합 모니터링**:
   ```
   현재 모든 워크플로우의 상태를 대시보드에서 확인해줘
   ```
