from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Application
    app_name: str = "Blog Automation System"
    debug: bool = False
    secret_key: str
    api_prefix: str = "/api/v1"
    
    # Database (Deprecated - Using Supabase instead)
    database_url: Optional[str] = None
    
    # Supabase
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None
    
    # Redis
    redis_url: str
    
    # Celery
    celery_broker_url: str
    celery_result_backend: str
    
    # AI APIs
    openai_api_key: Optional[str] = None
    claude_api_key: str
    claude_model: str = "claude-3-5-sonnet-20241022"
    claude_max_tokens: int = 4000
    
    # Image APIs
    unsplash_access_key: Optional[str] = None
    
    # Encryption
    encryption_key: str
    
    # JWT
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 30
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # Email
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # Rate limiting
    rate_limit_per_minute: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()