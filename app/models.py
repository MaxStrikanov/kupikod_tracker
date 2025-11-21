from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    JSON,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import relationship
from .database import Base


class Blogger(Base):
    __tablename__ = "bloggers"

    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String(32), index=True)  # "vk", "instagram"
    external_id = Column(String(255), index=True, unique=True)
    handle = Column(String(255), index=True)   # @username / screen_name
    name = Column(String(255), nullable=True)

    posts = relationship("Post", back_populates="blogger")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    blogger_id = Column(Integer, ForeignKey("bloggers.id"), index=True)
    platform = Column(String(32), index=True)
    external_id = Column(String(255), index=True)
    published_at = Column(DateTime, index=True)
    text = Column(Text, default="")
    links = Column(JSON, default=list)
    media = Column(JSON, default=list)
    raw = Column(JSON, default=dict)
    created_at = Column(DateTime, default=datetime.utcnow)

    blogger = relationship("Blogger", back_populates="posts")
    integration = relationship(
        "Integration",
        back_populates="post",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Integration(Base):
    __tablename__ = "integrations"

    id = Column(Integer, primary_key=True, index=True)
    post_id = Column(Integer, ForeignKey("posts.id"), index=True)
    brand = Column(String(128), index=True)  # "kupikod"
    is_ad = Column(Boolean, default=False)
    confidence = Column(Integer, default=0)  # 0-100
    promo_codes = Column(JSON, default=list)
    has_logo = Column(Boolean, default=False)
    has_ad_label = Column(Boolean, default=False)
    detected_at = Column(DateTime, default=datetime.utcnow)

    post = relationship("Post", back_populates="integration")
