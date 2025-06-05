from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum as PyEnum

from .database import Base


class VoteType(PyEnum):
    """投票类型枚举"""
    LIKE = "like"
    DISLIKE = "dislike"


class User(Base):
    """用户表"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    cursor_rules = relationship("CursorRule", back_populates="author", cascade="all, delete-orphan")
    created_categories = relationship("Category", back_populates="creator")
    created_tags = relationship("Tag", back_populates="creator")


class Category(Base):
    """一级类目表"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    creator = relationship("User", back_populates="created_categories")
    cursor_rules = relationship("CursorRule", back_populates="category")


class Tag(Base):
    """标签表"""
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, index=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    creator = relationship("User", back_populates="created_tags")
    cursor_rules = relationship("CursorRule", secondary="cursor_rules_tags", back_populates="tags")


class CursorRule(Base):
    """Cursor Rules表"""
    __tablename__ = "cursor_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    filename = Column(String(100), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    example = Column(Text)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    likes_count = Column(Integer, default=0)
    dislikes_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    category = relationship("Category", back_populates="cursor_rules")
    author = relationship("User", back_populates="cursor_rules")
    tags = relationship("Tag", secondary="cursor_rules_tags", back_populates="cursor_rules")
    votes = relationship("Vote", back_populates="cursor_rule", cascade="all, delete-orphan")


class CursorRuleTag(Base):
    """Cursor Rules标签关联表"""
    __tablename__ = "cursor_rules_tags"
    
    id = Column(Integer, primary_key=True, index=True)
    cursor_rule_id = Column(Integer, ForeignKey("cursor_rules.id", ondelete="CASCADE"), nullable=False)
    tag_id = Column(Integer, ForeignKey("tags.id"), nullable=False)
    
    # 唯一约束
    __table_args__ = (UniqueConstraint('cursor_rule_id', 'tag_id', name='unique_rule_tag'),)


class Vote(Base):
    """点赞点踩记录表"""
    __tablename__ = "votes"
    
    id = Column(Integer, primary_key=True, index=True)
    cursor_rule_id = Column(Integer, ForeignKey("cursor_rules.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=True)  # 登录用户ID
    ip_address = Column(String(45), nullable=False)  # IP地址作为备用标识
    vote_type = Column(Enum(VoteType), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    cursor_rule = relationship("CursorRule", back_populates="votes")
    user = relationship("User")
    
    # 唯一约束：对于登录用户使用user_id，对于未登录用户使用ip_address
    __table_args__ = (
        UniqueConstraint('cursor_rule_id', 'user_id', name='unique_user_rule'),
        UniqueConstraint('cursor_rule_id', 'ip_address', name='unique_ip_rule'),
    )