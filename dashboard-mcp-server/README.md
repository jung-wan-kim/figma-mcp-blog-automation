# Dashboard MCP Server

실시간 모니터링 및 시각화를 위한 MCP (Model Context Protocol) 서버입니다.

## 기능

- **실시간 메트릭 추적**: 워크플로우 및 컴포넌트 메트릭 실시간 업데이트
- **알림 시스템**: 중요 이벤트에 대한 실시간 알림
- **WebSocket 지원**: 대시보드와의 실시간 통신
- **성능 모니터링**: 평균 실행 시간, 성공률 등 추적

## 메트릭 구조

### 워크플로우 메트릭
- `total`: 총 실행된 워크플로우 수
- `running`: 현재 실행 중인 워크플로우
- `completed`: 성공적으로 완료된 워크플로우
- `failed`: 실패한 워크플로우

### 컴포넌트 메트릭
- `total`: 총 처리된 컴포넌트 수
- `generated`: 새로 생성된 컴포넌트
- `updated`: 업데이트된 컴포넌트

### 성능 메트릭
- `avgWorkflowTime`: 평균 워크플로우 실행 시간
- `successRate`: 워크플로우 성공률
- `lastUpdated`: 마지막 업데이트 시간

## 설정

1. `.env` 파일 생성:
```bash
cp .env.example .env
```

2. WebSocket 포트 설정 (기본값: 3001)

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

### update-workflow-metrics
워크플로우 실행 상태를 업데이트합니다.

### update-component-metrics
컴포넌트 처리 상태를 업데이트합니다.

### get-dashboard-metrics
현재 모든 메트릭을 조회합니다.

### send-notification
새로운 알림을 생성하고 전송합니다.

### get-notifications
최근 알림 목록을 조회합니다.

### start-websocket-server
WebSocket 서버를 시작하여 실시간 통신을 활성화합니다.

## WebSocket 이벤트

### 클라이언트 → 서버
- 연결 시 자동으로 초기 메트릭 수신

### 서버 → 클라이언트
- `initial-metrics`: 연결 시 전체 메트릭
- `workflow-metrics`: 워크플로우 메트릭 업데이트
- `component-metrics`: 컴포넌트 메트릭 업데이트
- `notification`: 새로운 알림

## 대시보드 연동 예시

```javascript
const ws = new WebSocket('ws://localhost:3001');

ws.onmessage = (event) => {
  const { type, data } = JSON.parse(event.data);
  
  switch (type) {
    case 'workflow-metrics':
      updateWorkflowChart(data);
      break;
    case 'notification':
      showNotification(data);
      break;
  }
};
```