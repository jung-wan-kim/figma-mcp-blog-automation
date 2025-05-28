# Figma MCP Server

Figma 디자인 시스템 자동화를 위한 MCP (Model Context Protocol) 서버입니다.

## 기능

- **디자인 변경 감지**: Figma 파일의 변경사항을 자동으로 감지
- **컴포넌트 추출**: Figma 컴포넌트 정보를 구조화된 데이터로 추출
- **디자인 토큰 추출**: 색상, 타이포그래피, 간격 등의 디자인 토큰 추출
- **JSON 변환**: 컴포넌트 정보를 React 컴포넌트 생성에 적합한 JSON으로 변환

## 설정

1. `.env` 파일 생성:
```bash
cp .env.example .env
```

2. Figma Personal Access Token 설정:
   - [Figma 설정](https://www.figma.com/settings)에서 Personal Access Token 생성
   - `.env` 파일에 토큰 추가

3. Figma 파일 키 설정:
   - Figma 파일 URL에서 파일 키 확인 (예: `https://www.figma.com/file/[FILE_KEY]/...`)
   - `.env` 파일에 파일 키 추가

## 사용법

### 서버 시작
```bash
npm start
```

### 개발 모드 (파일 변경 감지)
```bash
npm run dev
```

## MCP 도구

### detect-design-changes
Figma 파일의 변경사항을 감지합니다.

### extract-components
Figma 파일에서 모든 컴포넌트를 추출합니다.

### extract-design-tokens
디자인 시스템의 토큰(색상, 타이포그래피 등)을 추출합니다.

### generate-component-json
특정 컴포넌트의 상세 정보를 JSON으로 변환합니다.

## 다음 단계

- [ ] 실제 Figma API 연동
- [ ] 웹훅 엔드포인트 구현
- [ ] 컴포넌트 변경 비교 로직
- [ ] React 컴포넌트 생성기 연동