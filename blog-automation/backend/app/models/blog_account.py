from sqlalchemy import Column, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.core.database import Base


class BlogPlatform(str, enum.Enum):
    WORDPRESS = "wordpress"
    TISTORY = "tistory"
    NAVER = "naver"


class AccountStatus(str, enum.Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class BlogAccount(Base):
    __tablename__ = "blog_accounts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    platform = Column(Enum(BlogPlatform), nullable=False)
    account_name = Column(String(255), nullable=False)
    blog_url = Column(String(500))
    auth_credentials = Column(JSON, nullable=False)  # Encrypted credentials
    status = Column(Enum(AccountStatus), default=AccountStatus.ACTIVE)
    last_sync_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", backref="blog_accounts")