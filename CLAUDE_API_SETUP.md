# Claude API 설정 가이드

## 1. Claude API 키 발급

1. [Anthropic Console](https://console.anthropic.com)에 접속
2. 계정 생성 또는 로그인
3. API Keys 메뉴에서 새 API 키 생성
4. 생성된 API 키 복사 (sk-ant-api03-... 형태)

## 2. 환경 변수 설정

`blog-automation/backend/.env` 파일에서 다음 부분을 수정:

```env
# AI APIs
CLAUDE_API_KEY=sk-ant-api03-여기에실제API키입력
# OPENAI_API_KEY=your-openai-api-key  # 선택사항 - GPT-4 사용시에만 필요

# Claude API Settings
CLAUDE_MODEL=claude-3-7-sonnet-20250219
CLAUDE_MAX_TOKENS=128000
```

## 3. 사용 가능한 Claude 모델

- `claude-3-7-sonnet-20250219` (권장): 최신 Claude 3.7 Sonnet (하이브리드 추론 모델)
- `claude-3-5-sonnet-20241022`: Claude 3.5 Sonnet
- `claude-3-5-haiku-20241022`: 빠르고 효율적인 모델
- `claude-3-opus-20240229`: 가장 강력한 모델 (비용 높음)

### Claude 3.7 Sonnet 특징
- **하이브리드 추론**: 즉시 응답 또는 단계별 사고 모드 지원
- **128K 토큰 출력**: 더 긴 콘텐츠 생성 가능
- **향상된 성능**: 더 깊이 있고 논리적인 콘텐츠 생성

## 4. API 사용량 및 비용

- Claude API는 토큰 기반 과금
- 입력 토큰과 출력 토큰에 따라 비용 책정
- [공식 가격표](https://www.anthropic.com/pricing) 참고

## 5. 설정 확인

서버 재시작 후 콘텐츠 생성 시 다음과 같이 확인 가능:
- 성공 시: 실제 Claude API로 생성된 고품질 콘텐츠
- 실패 시: 자동으로 시뮬레이션 모드로 전환

## 6. 주의사항

- API 키는 보안이 중요하므로 공개 저장소에 커밋하지 마세요
- `.env` 파일은 `.gitignore`에 포함되어 있습니다
- API 사용량을 정기적으로 모니터링하세요

## 7. 문제 해결

### API 키 오류
```
Claude API 키가 설정되지 않았습니다
```
→ `.env` 파일의 `CLAUDE_API_KEY` 확인

### 권한 오류
```
anthropic.APIError: 401 Unauthorized
```
→ API 키가 올바른지 확인, Anthropic Console에서 키 상태 확인

### 사용량 초과
```
anthropic.APIError: 429 Too Many Requests
```
→ API 사용량 한도 확인, 요금제 업그레이드 필요할 수 있음