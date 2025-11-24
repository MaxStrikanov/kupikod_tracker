from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class Blogger(Base):
    __tablename__ = "bloggers"
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String, index=True)
    external_id = Column(String, index=True)
    handle = Column(String, nullable=True)
    name = Column(String, nullable=True)
    posts = relationship("Post", back_populates="blogger")

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, index=True)
    blogger_id = Column(Integer, ForeignKey("bloggers.id"))
    platform = Column(String, index=True)
    external_id = Column(String, index=True)
    text = Column(Text)
    published_at = Column(DateTime, default=datetime.utcnow)
    blogger = relationship("Blogger", back_populates="posts")
    integrations = relationship("KupikodIntegration", back_populates="post")

class KupikodIntegration(Base):
    __tablename__ = "kupikod_integrations"
    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    is_ad = Column(Boolean, default=False)
    confidence = Column(Float, default=0.0)
    promo_codes = Column(JSON, default=list)
    detected_at = Column(DateTime, default=datetime.utcnow)
    brief_check = Column(JSON, nullable=True)
    post = relationship("Post", back_populates="integrations")
