# GitHub MCP Server

GitHub 자동화를 위한 MCP (Model Context Protocol) 서버입니다.

## 기능

- **브랜치 생성**: 새로운 feature 브랜치 자동 생성
- **Pull Request 관리**: PR 생성, 리뷰어 할당, 라벨 추가
- **파일 커밋**: 여러 파일을 한 번에 커밋
- **저장소 정보 조회**: 저장소 설정 및 기본 정보 확인

## 설정

1. `.env` 파일 생성:
```bash
cp .env.example .env
```

2. GitHub Personal Access Token 설정:
   - [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens)
   - 필요한 권한: `repo`, `write:packages`, `read:user`
   - `.env` 파일에 토큰 추가

## 사용법

### 서버 시작
```bash
npm start
```

### 개발 모드
```bash
npm run dev
```

## MCP 도구

### create-branch
새로운 브랜치를 생성합니다.
- `repository`: 저장소 이름 (owner/repo)
- `branchName`: 생성할 브랜치 이름
- `baseBranch`: 기준 브랜치 (기본값: main)

### create-pull-request
Pull Request를 생성합니다.
- `repository`: 저장소 이름
- `title`: PR 제목
- `description`: PR 설명
- `head`: 소스 브랜치
- `base`: 대상 브랜치
- `reviewers`: 리뷰어 목록 (선택)
- `labels`: 라벨 목록 (선택)

### commit-files
파일들을 커밋합니다.
- `repository`: 저장소 이름
- `branch`: 커밋할 브랜치
- `files`: 파일 배열 [{path, content}]
- `message`: 커밋 메시지

### get-repository-info
저장소 정보를 조회합니다.
- `repository`: 저장소 이름

## 워크플로우 예시

1. Figma에서 디자인 변경 감지
2. **브랜치 생성** (feature/auto-update-20250528)
3. 컴포넌트 파일 생성
4. **파일 커밋**
5. **Pull Request 생성**
6. 리뷰어 자동 할당

## 보안 주의사항

- GitHub 토큰은 절대 커밋하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있어야 합니다
- 최소한의 필요한 권한만 부여하세요