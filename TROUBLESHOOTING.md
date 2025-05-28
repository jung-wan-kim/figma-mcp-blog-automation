# 🔧 문제 해결 가이드

## 🚨 일반적인 문제들

### 1. 설치 및 초기 설정 문제

#### ❌ `npm run setup` 실행 시 권한 오류
```bash
Error: EACCES: permission denied
```

**해결방법:**
```bash
# macOS/Linux
chmod +x setup.sh
npm run setup

# Windows
# PowerShell에서 실행 정책 변경
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

#### ❌ Node.js 버전 호환성 문제
```bash
Error: Node.js version 16.x.x is not supported
```

**해결방법:**
```bash
# Node.js 18+ 설치 확인
node --version  # v18.0.0 이상이어야 함

# nvm 사용시
nvm install 18
nvm use 18
```

---

### 2. API 연동 문제

#### ❌ Figma API 접근 오류
```bash
Error: Figma API 접근 권한이 없습니다
```

**체크리스트:**
- [ ] FIGMA_TOKEN이 올바르게 설정되었는지 확인
- [ ] 토큰이 만료되지 않았는지 확인
- [ ] Figma 파일에 읽기 권한이 있는지 확인
- [ ] FIGMA_FILE_KEY가 올바른지 확인

**토큰 확인 방법:**
```bash
# Figma API 테스트
curl -H "X-Figma-Token: YOUR_TOKEN" \
  "https://api.figma.com/v1/files/YOUR_FILE_KEY"
```

#### ❌ GitHub API Rate Limit 오류
```bash
Error: API rate limit exceeded
```

**해결방법:**
```bash
# 1. GitHub 토큰 권한 확인
# repo, workflow 권한이 있는지 확인

# 2. 다른 토큰 사용 또는 잠시 대기

# 3. Rate limit 상태 확인
curl -H "Authorization: token YOUR_TOKEN" \
  https://api.github.com/rate_limit
```

#### ❌ Supabase 연결 오류
```bash
Error: Invalid API URL or anon key
```

**해결방법:**
```bash
# 1. Supabase 프로젝트 설정에서 URL 및 키 확인
# 2. .env 파일의 형식 확인
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...

# 3. 네트워크 연결 확인
ping your-project.supabase.co
```

---

### 3. MCP 서버 문제

#### ❌ MCP 서버 시작 실패
```bash
Error: Cannot find module '@modelcontextprotocol/sdk'
```

**해결방법:**
```bash
# 각 MCP 서버 디렉토리에서 의존성 재설치
cd figma-mcp-server && npm install
cd github-mcp-server && npm install
cd supabase-mcp-server && npm install
cd dashboard-mcp-server && npm install
cd taskmanager-mcp-server && npm install
```

#### ❌ MCP 서버 통신 오류
```bash
Error: MCP server communication timeout
```

**디버깅 단계:**
```bash
# 1. 개별 서버 테스트
npm run mcp:figma
npm run mcp:github
npm run mcp:supabase

# 2. 로그 확인
tail -f figma-mcp-server/logs/server.log

# 3. 포트 충돌 확인
lsof -i :3001  # 대시보드 WebSocket 포트
```

---

### 4. 워크플로우 실행 문제

#### ❌ 통합 테스트 실패
```bash
❌ GitHub: 실패
```

**체크리스트:**
```bash
# 1. API 토큰 확인
echo $GITHUB_TOKEN

# 2. 저장소 권한 확인
# DEFAULT_REPOSITORY 설정이 올바른지 확인

# 3. 개별 테스트
cd github-mcp-server
node server.js
```

#### ❌ 자동화 실행 중 실패
```bash
Step 3: Generating React Components...
❌ Step failed: Component generation
```

**디버깅 방법:**
```bash
# 1. 상세 로그 활성화
DEBUG=true npm run orchestrate YOUR_FIGMA_FILE_KEY

# 2. 단계별 실행
cd automation
node enhanced-orchestrator.js YOUR_FIGMA_FILE_KEY

# 3. 특정 단계만 테스트
# TaskManager MCP에서 개별 도구 호출 테스트
```

---

### 5. 대시보드 문제

#### ❌ WebSocket 연결 실패
```bash
WebSocket connection failed
```

**해결방법:**
```bash
# 1. 대시보드 서버 시작 확인
npm run dashboard:server

# 2. 포트 사용 여부 확인
lsof -i :3001

# 3. 방화벽 설정 확인 (필요시)
# Windows: Windows Defender 방화벽 설정
# macOS: 시스템 환경설정 > 보안 및 개인정보 보호 > 방화벽
```

#### ❌ 대시보드에 데이터가 표시되지 않음
```bash
No metrics data available
```

**해결방법:**
```bash
# 1. 대시보드 MCP 서버 로그 확인
cd dashboard-mcp-server
npm start

# 2. WebSocket 메시지 확인
# 브라우저 개발자 도구 > 네트워크 탭에서 WebSocket 연결 확인

# 3. 더미 데이터로 테스트
# dashboard-mcp-server에서 테스트 메트릭 전송
```

---

### 6. 파일 생성 및 커밋 문제

#### ❌ 컴포넌트 파일 생성 실패
```bash
Error: Cannot write to src/components/generated/
```

**해결방법:**
```bash
# 1. 디렉토리 권한 확인
ls -la src/components/
mkdir -p src/components/generated

# 2. 쓰기 권한 부여
chmod 755 src/components/generated/

# 3. 디스크 공간 확인
df -h
```

#### ❌ GitHub 커밋 실패
```bash
Error: Git push failed
```

**해결방법:**
```bash
# 1. Git 설정 확인
git config --list | grep user

# 2. 원격 저장소 연결 확인
git remote -v

# 3. 브랜치 상태 확인
git status
git log --oneline -5

# 4. 수동 푸시 테스트
git push origin main
```

---

### 7. 환경별 문제

#### ❌ Windows 환경에서 스크립트 실행 오류
```bash
'.' is not recognized as an internal or external command
```

**해결방법:**
```bash
# PowerShell 사용
npm run test:integration

# Git Bash 사용 (권장)
# Git for Windows와 함께 설치된 Git Bash 사용

# WSL 사용 (고급)
wsl --install
# Ubuntu에서 프로젝트 실행
```

#### ❌ macOS 권한 문제
```bash
Operation not permitted
```

**해결방법:**
```bash
# 1. 터미널 전체 디스크 접근 권한 부여
# 시스템 환경설정 > 보안 및 개인정보 보호 > 개인정보 보호 > 전체 디스크 접근 권한

# 2. Xcode Command Line Tools 설치
xcode-select --install

# 3. Homebrew로 Node.js 재설치
brew uninstall node
brew install node
```

---

### 8. 성능 문제

#### ❌ 자동화 실행이 너무 느림
```bash
Total Duration: 180s (예상: 45s)
```

**최적화 방법:**
```bash
# 1. 네트워크 연결 확인
ping api.figma.com
ping api.github.com

# 2. 캐시 클리어
npm cache clean --force

# 3. 병렬 처리 최적화
# enhanced-orchestrator.js에서 병렬 처리 설정 확인

# 4. Figma 파일 크기 확인
# 큰 파일의 경우 처리 시간이 오래 걸릴 수 있음
```

---

### 9. 메모리 및 성능 문제

#### ❌ 메모리 부족 오류
```bash
JavaScript heap out of memory
```

**해결방법:**
```bash
# Node.js 메모리 제한 증가
export NODE_OPTIONS="--max-old-space-size=4096"
npm run orchestrate YOUR_FIGMA_FILE_KEY

# 또는 package.json에서 스크립트 수정
"orchestrate": "node --max-old-space-size=4096 automation/enhanced-orchestrator.js"
```

---

### 10. 로그 및 디버깅

#### 📋 로그 위치
```bash
# MCP 서버 로그
figma-mcp-server/logs/
github-mcp-server/logs/
supabase-mcp-server/logs/
dashboard-mcp-server/logs/
taskmanager-mcp-server/logs/

# 시스템 로그
automation/logs/
```

#### 🔍 디버깅 모드 활성화
```bash
# 상세 로그 출력
DEBUG=* npm run orchestrate YOUR_FIGMA_FILE_KEY

# 특정 컴포넌트만 디버깅
DEBUG=figma-mcp npm run orchestrate YOUR_FIGMA_FILE_KEY
DEBUG=github-mcp npm run orchestrate YOUR_FIGMA_FILE_KEY
```

#### 📊 상태 모니터링
```bash
# 시스템 리소스 확인
top -p $(pgrep -f "node.*server.js")

# 네트워크 연결 확인
netstat -an | grep :3001

# 프로세스 확인
ps aux | grep node
```

---

## 🆘 추가 도움이 필요한 경우

### 📞 지원 채널
1. **GitHub Issues**: [버그 리포트](https://github.com/jung-wan-kim/figma-mcp-nextjs-supabase/issues)
2. **GitHub Discussions**: [질문 및 토론](https://github.com/jung-wan-kim/figma-mcp-nextjs-supabase/discussions)
3. **Wiki**: [고급 사용법](https://github.com/jung-wan-kim/figma-mcp-nextjs-supabase/wiki)

### 🐛 버그 리포트 작성 시 포함사항
```markdown
**환경 정보:**
- OS: [예: macOS 13.0, Windows 11, Ubuntu 20.04]
- Node.js 버전: [예: v18.17.0]
- npm 버전: [예: 9.6.7]

**재현 단계:**
1. 
2. 
3. 

**예상 결과:**

**실제 결과:**

**오류 로그:**
```

**추가 파일:**
- 스크린샷
- 로그 파일
- 설정 파일 (.env는 민감정보 제거 후)

### 🔧 임시 해결책
문제가 해결되지 않을 경우 시뮬레이션 모드로 테스트해볼 수 있습니다:

```bash
# API 연동 없이 시뮬레이션 모드 실행
SIMULATION_MODE=true npm run orchestrate demo-file-key
```

---

*마지막 업데이트: 2025-05-28*