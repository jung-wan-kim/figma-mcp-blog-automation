# 🤖 AI 블로그 자동화 시스템

AI 기반 자동 블로그 콘텐츠 생성 및 발행 시스템으로, 키워드 분석부터 SEO 최적화된
글 작성, 다중 플랫폼 동시 발행까지 완전 자동화하는 솔루션입니다.

## 🌟 주요 기능

### 🔥 AI 콘텐츠 생성

- **GPT-4 & Claude 3.5** 기반 고품질 블로그 글 자동 생성
- **키워드 기반** 주제 발굴 및 콘텐츠 기획
- **브랜드 톤앤매너**에 맞춘 글쓰기 스타일 적용
- **다양한 글 형식** 지원 (리뷰, 하우투, 뉴스, 비교분석 등)

### 📈 SEO 자동 최적화

- **키워드 밀도** 자동 조절
- **메타 태그 및 설명** 자동 생성
- **헤딩 구조** 최적화
- **내부/외부 링크** 자동 삽입
- **이미지 alt 태그** 자동 생성

### 📝 다중 플랫폼 발행

- **WordPress, Tistory, Naver Blog** 동시 발행
- **각 플랫폼별 최적화**된 포맷 자동 변환
- **플랫폼별 태그 및 카테고리** 자동 설정
- **발행 결과 모니터링** 및 오류 처리

### ⏰ 콘텐츠 스케줄링

- **최적 발행 시간** 자동 분석
- **콘텐츠 캘린더** 관리
- **반복 발행 스케줄** 설정
- **긴급 콘텐츠** 우선순위 처리

### 📊 성과 분석

- **실시간 트래픽** 모니터링
- **키워드 순위** 추적
- **참여도 분석** (댓글, 공유, 체류시간)
- **ROI 계산** 및 성과 리포트

## 🛠 기술 스택

### Backend

- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL + Redis
- **Queue**: Celery + RabbitMQ
- **AI APIs**: OpenAI GPT-4, Anthropic Claude 3.5
- **Automation**: Playwright, Selenium

### Infrastructure

- **Containerization**: Docker, Docker Compose
- **Monitoring**: Prometheus, Grafana
- **Logging**: Structured logging (structlog)
- **Testing**: pytest, pytest-asyncio

## 🚀 빠른 시작

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd blog-automation
```

### 2. 환경 설정

```bash
# 환경 변수 파일 복사
cp backend/.env.example backend/.env

# 환경 변수 설정 (API 키 등)
vi backend/.env
```

### 3. Docker로 실행

```bash
cd backend
docker-compose up -d
```

### 4. 데이터베이스 마이그레이션

```bash
docker-compose exec api alembic upgrade head
```

### 5. API 문서 확인

http://localhost:8000/docs

## 📋 환경 변수 설정

### 필수 설정

```env
# 애플리케이션
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://bloguser:blogpass@db:5432/blog_automation
REDIS_URL=redis://redis:6379

# AI APIs
OPENAI_API_KEY=your-openai-api-key
CLAUDE_API_KEY=your-anthropic-api-key

# 암호화
ENCRYPTION_KEY=your-fernet-encryption-key
```

### 선택 설정

```env
# 이메일 (알림용)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Google Analytics (분석용)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

## 🔧 개발 환경 설정

### 1. Python 가상환경

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. 데이터베이스 설정

```bash
# PostgreSQL 실행 (Docker)
docker run -d --name blog-postgres \
  -e POSTGRES_DB=blog_automation \
  -e POSTGRES_USER=bloguser \
  -e POSTGRES_PASSWORD=blogpass \
  -p 5432:5432 postgres:15

# Redis 실행 (Docker)
docker run -d --name blog-redis -p 6379:6379 redis:7-alpine
```

### 3. 개발 서버 실행

```bash
# API 서버
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Celery Worker
celery -A app.celery_app worker --loglevel=info

# Celery Beat (스케줄러)
celery -A app.celery_app beat --loglevel=info

# Flower (Celery 모니터링)
celery -A app.celery_app flower
```

### 4. 테스트 실행

```bash
# 전체 테스트
pytest

# 커버리지 포함
pytest --cov=app --cov-report=html

# 특정 테스트 파일
pytest tests/test_auth.py -v
```

## 📚 API 사용법

### 1. 사용자 등록 및 로그인

```bash
# 사용자 등록
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123",
    "full_name": "홍길동"
  }'

# 로그인
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=user@example.com&password=password123'
```

### 2. 블로그 계정 연결

```bash
# WordPress 계정 추가
curl -X POST "http://localhost:8000/api/v1/blog-accounts/" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "wordpress",
    "account_name": "내 워드프레스 블로그",
    "blog_url": "https://myblog.com",
    "auth_credentials": {
      "site_url": "https://myblog.com",
      "username": "admin",
      "password": "app_password"
    }
  }'
```

### 3. 콘텐츠 생성

```bash
# AI 콘텐츠 생성
curl -X POST "http://localhost:8000/api/v1/contents/generate" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "keywords": ["Python", "FastAPI", "API 개발"],
    "content_type": "blog_post",
    "target_length": 1500,
    "style_preset": "technical",
    "tone": "친근하고 전문적인"
  }'
```

### 4. 콘텐츠 발행

```bash
# 다중 플랫폼 발행
curl -X POST "http://localhost:8000/api/v1/publications/publish" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_id": "content-uuid",
    "blog_account_ids": ["account-uuid-1", "account-uuid-2"],
    "publish_immediately": true
  }'
```

## 🔄 플랫폼별 설정

### WordPress

- **REST API** 활성화 필요
- **Application Password** 생성
- **Yoast SEO** 플러그인 권장

### Tistory

- **Open API** 키 발급
- **액세스 토큰** 획득
- **블로그명** 확인

### 네이버 블로그

- **네이버 아이디/비밀번호** 필요
- **2단계 인증** 비활성화 권장
- **자동화 정책** 준수 필요

## 🏗 아키텍처

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Backend       │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Services      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                ▲                       ▲
                                │                       │
                         ┌─────────────────┐    ┌─────────────────┐
                         │   Message       │    │   Database      │
                         │   Queue         │    │   (PostgreSQL   │
                         │   (Redis)       │    │   + Redis)      │
                         └─────────────────┘    └─────────────────┘
                                ▲
                                │
                         ┌─────────────────┐
                         │   Background    │
                         │   Workers       │
                         │   (Celery)      │
                         └─────────────────┘
```

## 🔧 설정 및 커스터마이징

### AI 모델 설정

```python
# app/services/content_generator.py
CONTENT_GENERATION_MODELS = {
    "creative": "gpt-4-turbo-preview",
    "technical": "claude-3-sonnet-20240229",
    "news": "gpt-3.5-turbo"
}
```

### 플랫폼별 설정

```python
# app/core/config.py
PLATFORM_SETTINGS = {
    "wordpress": {
        "max_title_length": 60,
        "max_excerpt_length": 155,
        "supported_formats": ["html"]
    },
    "tistory": {
        "max_title_length": 100,
        "max_tags": 10,
        "supported_formats": ["html", "markdown"]
    }
}
```

## 📊 모니터링 및 로깅

### Prometheus 메트릭

- `content_generated_total`: 생성된 콘텐츠 수
- `content_published_total`: 발행된 콘텐츠 수
- `api_requests_total`: API 요청 수
- `active_users`: 활성 사용자 수

### 로그 구조

```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "logger": "content_generator",
  "message": "Content generated successfully",
  "user_id": "uuid",
  "content_id": "uuid",
  "ai_model": "gpt-4"
}
```

## 🧪 테스트

### 단위 테스트

```bash
# 특정 모듈 테스트
pytest tests/test_content_generator.py -v

# 비동기 테스트
pytest tests/test_api/ -v --asyncio-mode=auto
```

### 통합 테스트

```bash
# API 엔드포인트 테스트
pytest tests/test_api/ -v

# 데이터베이스 테스트
pytest tests/test_models/ -v
```

### 부하 테스트

```bash
# Locust 설치 및 실행
pip install locust
locust -f tests/load_test.py --host=http://localhost:8000
```

## 🚀 배포

### Docker 배포

```bash
# 프로덕션 빌드
docker-compose -f docker-compose.prod.yml build

# 배포
docker-compose -f docker-compose.prod.yml up -d
```

### 환경별 설정

```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  api:
    image: blog-automation:latest
    environment:
      - DEBUG=False
      - DATABASE_URL=postgresql://user:pass@prod-db:5432/blog_automation
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '2'
          memory: 4G
```

## 🤝 기여하기

1. 포크 및 클론
2. 기능 브랜치 생성 (`git checkout -b feature/amazing-feature`)
3. 변경사항 커밋 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시 (`git push origin feature/amazing-feature`)
5. Pull Request 생성

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE)
파일을 참조하세요.

## 🆘 지원 및 문의

- **이슈 리포트**: [GitHub Issues](https://github.com/your-repo/issues)
- **기능 요청**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **문서**: [Wiki](https://github.com/your-repo/wiki)

## 🗺 로드맵

### v1.0 (현재)

- ✅ 기본 콘텐츠 생성 및 발행
- ✅ WordPress, Tistory, 네이버 블로그 지원
- ✅ 기본 SEO 최적화

### v1.1 (예정)

- 🔄 고급 SEO 분석 도구
- 🔄 멀티브랜드 관리
- 🔄 이미지 자동 생성

### v2.0 (계획)

- 📝 음성 인식 콘텐츠 작성
- 📝 AI 기반 성과 예측
- 📝 해외 플랫폼 지원 (Medium, Dev.to)

---

<p align="center">
  Made with ❤️ by AI Blog Automation Team
</p>
