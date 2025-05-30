from sqlalchemy import Column, Integer, Float, Date, DateTime, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.core.database import Base


class Analytics(Base):
    __tablename__ = "analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("contents.id"), nullable=False)
    publication_id = Column(UUID(as_uuid=True), ForeignKey("publications.id"))
    date = Column(Date, nullable=False)
    
    # Traffic metrics
    views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    
    # Engagement metrics
    shares = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    avg_time_on_page = Column(Float, default=0.0)  # in seconds
    bounce_rate = Column(Float, default=0.0)  # percentage
    
    # SEO metrics
    keyword_rankings = Column(JSON)  # {"keyword": rank}
    search_impressions = Column(Integer, default=0)
    search_clicks = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    content = relationship("Content", backref="analytics")
    publication = relationship("Publication", backref="analytics")