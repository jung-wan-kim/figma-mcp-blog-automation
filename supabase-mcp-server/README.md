# Supabase MCP Server

데이터 저장 및 상태 관리를 위한 MCP (Model Context Protocol) 서버입니다.

## 기능

- **워크플로우 상태 관리**: 워크플로우 실행 상태 저장 및 이력 조회
- **컴포넌트 메타데이터**: 생성된 컴포넌트 정보 저장 및 추적
- **디자인 토큰 버전 관리**: 디자인 시스템 토큰의 버전별 저장
- **실시간 동기화**: Supabase의 실시간 기능 활용 (향후 구현)

## 데이터베이스 스키마

### workflow_states 테이블
```sql
CREATE TABLE workflow_states (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  workflow_id TEXT NOT NULL,
  status TEXT NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### component_metadata 테이블
```sql
CREATE TABLE component_metadata (
  component_id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  figma_data JSONB,
  generated_files TEXT[],
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### design_tokens 테이블
```sql
CREATE TABLE design_tokens (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  tokens JSONB NOT NULL,
  version TEXT NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

## 설정

1. Supabase 프로젝트 생성:
   - [Supabase Dashboard](https://app.supabase.com)에서 새 프로젝트 생성
   - 위의 SQL 스키마로 테이블 생성

2. `.env` 파일 설정:
```bash
cp .env.example .env
```

3. Supabase 자격 증명 추가:
   - 프로젝트 설정에서 URL과 anon key 복사
   - `.env` 파일에 추가

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

### save-workflow-state
워크플로우 실행 상태를 저장합니다.

### get-workflow-history
워크플로우 실행 이력을 조회합니다.

### save-component-metadata
컴포넌트 관련 메타데이터를 저장합니다.

### get-component-metadata
특정 컴포넌트의 메타데이터를 조회합니다.

### save-design-tokens
디자인 토큰을 버전과 함께 저장합니다.

## 시뮬레이션 모드

Supabase 자격 증명이 없는 경우 자동으로 시뮬레이션 모드로 실행됩니다.
이 모드에서는 실제 데이터베이스 대신 모의 데이터를 반환합니다.