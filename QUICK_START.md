# ⚡ 빠른 시작 가이드

## 🎯 5분만에 Figma → React 자동화 시작하기

### 1️⃣ 설치 (2분)

```bash
git clone https://github.com/jung-wan-kim/figma-mcp-nextjs-supabase.git
cd figma-mcp-nextjs-supabase
npm run setup
```

### 2️⃣ API 키 설정 (2분)

**Figma API 토큰:**
```bash
# figma-mcp-server/.env 파일에 추가
FIGMA_TOKEN=figd_your_token_here
FIGMA_FILE_KEY=your_file_key_here
```

**GitHub API 토큰:**
```bash
# github-mcp-server/.env 파일에 추가  
GITHUB_TOKEN=ghp_your_token_here
DEFAULT_REPOSITORY=username/repo-name
```

### 3️⃣ 테스트 (30초)

```bash
npm run test:integration
```

모든 테스트가 ✅ 성공하면 준비 완료!

### 4️⃣ 실행 (30초)

```bash
# 대시보드 시작 (선택사항)
npm run dashboard:server

# 자동화 실행
npm run orchestrate YOUR_FIGMA_FILE_KEY
```

## 🎉 완료!

- 📱 대시보드: http://localhost:3000/dashboard
- 📝 GitHub에서 자동 생성된 PR 확인
- 🎨 `src/components/generated/` 폴더에서 생성된 컴포넌트 확인

---

## 💡 다음은?

자세한 사용법은 [USAGE_GUIDE.md](./USAGE_GUIDE.md)를 참조하세요!

### 🔑 필수 준비물

1. **Figma 계정** + Personal Access Token
2. **GitHub 계정** + Personal Access Token  
3. **Node.js 18+**

### 🚨 문제 해결

**"토큰이 작동하지 않아요"**
- Figma: 파일 읽기 권한 확인
- GitHub: `repo`, `workflow` 권한 확인

**"테스트가 실패해요"**
```bash
# 개별 서버 테스트
npm run mcp:figma
npm run mcp:github
```

**더 많은 도움이 필요하면:**
- 📖 [상세 가이드](./USAGE_GUIDE.md)
- 🐛 [GitHub Issues](https://github.com/jung-wan-kim/figma-mcp-nextjs-supabase/issues)

---

*⏱️ 총 소요시간: 5분 | 난이도: ⭐⭐☆☆☆*