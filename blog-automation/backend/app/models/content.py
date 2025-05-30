from sqlalchemy import Column, String, Text, Integer, DateTime, Enum, ForeignKey, ARRAY, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class ContentStatus(str, enum.Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    FAILED = "failed"


class ContentType(str, enum.Enum):
    BLOG_POST = "blog_post"
    REVIEW = "review"
    HOWTO = "howto"
    NEWS = "news"
    COMPARISON = "comparison"


class Content(Base):
    __tablename__ = "contents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    title = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    content_type = Column(Enum(ContentType), default=ContentType.BLOG_POST)
    meta_description = Column(Text)
    keywords = Column(ARRAY(String))
    target_keywords = Column(ARRAY(String))
    seo_score = Column(Integer, default=0)
    readability_score = Column(Integer, default=0)
    word_count = Column(Integer, default=0)
    status = Column(Enum(ContentStatus), default=ContentStatus.DRAFT)
    scheduled_at = Column(DateTime(timezone=True))
    style_preset = Column(String(100))  # 브랜드 톤앤매너
    ai_model_used = Column(String(50))  # gpt-4, claude-3.5, etc
    generation_prompt = Column(Text)  # 생성에 사용된 프롬프트 저장
    
    # 이미지 정보
    featured_image_url = Column(String(1000))
    featured_image_alt = Column(String(200))
    suggested_images = Column(JSON)  # 제안된 이미지들
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="contents")
    publications = relationship("Publication", back_populates="content")