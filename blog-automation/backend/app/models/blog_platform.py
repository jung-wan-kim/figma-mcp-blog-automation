from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from app.core.database import Base


class BlogPlatform(Base):
    __tablename__ = "blog_platforms"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)  # "WordPress", "Tistory", "Naver Blog" 등
    platform_type = Column(String(50), nullable=False)  # "wordpress", "tistory", "naver"
    
    # 연결 정보
    url = Column(String(500), nullable=False)  # 블로그 주소
    username = Column(String(100), nullable=True)
    api_key = Column(Text, nullable=True)  # 암호화된 API 키
    access_token = Column(Text, nullable=True)  # 암호화된 액세스 토큰
    
    # 설정 정보
    config = Column(JSON, nullable=True)  # 플랫폼별 추가 설정
    
    # 상태
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)  # 연결 검증 상태
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # 통계
    total_posts = Column(Integer, default=0)
    last_post_at = Column(DateTime(timezone=True), nullable=True)
    
    # 메타데이터
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 관계
    publications = relationship("Publication", back_populates="platform")