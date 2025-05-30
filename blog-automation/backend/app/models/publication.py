from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class PublicationStatus(str, enum.Enum):
    PENDING = "pending"
    PUBLISHED = "published"
    FAILED = "failed"
    RETRYING = "retrying"


class Publication(Base):
    __tablename__ = "publications"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("contents.id"), nullable=False)
    blog_account_id = Column(UUID(as_uuid=True), ForeignKey("blog_accounts.id"), nullable=False)
    platform_post_id = Column(String(255))  # 플랫폼에서 생성된 포스트 ID
    platform_post_url = Column(String(500))  # 발행된 포스트 URL
    status = Column(Enum(PublicationStatus), nullable=False, default=PublicationStatus.PENDING)
    published_at = Column(DateTime(timezone=True))
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    
    # 이미지 정보
    featured_image_url = Column(String(1000))
    featured_image_alt = Column(String(200))
    suggested_images = Column(JSON)  # 제안된 이미지들
    
    # 성과 정보
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    last_stats_update = Column(DateTime(timezone=True))
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    content = relationship("Content", back_populates="publications")
    blog_account = relationship("BlogAccount", backref="publications")