"""
Database models for Multi-Agent Researcher
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum as PyEnum

Base = declarative_base()

class CloneStatus(PyEnum):
    PENDING = "pending"
    CLONING = "cloning"
    COMPLETED = "completed"
    FAILED = "failed"

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String, nullable=False)
    github_owner = Column(String)
    github_repo = Column(String)
    clone_status = Column(Enum(CloneStatus))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documentation = relationship("Documentation", back_populates="repository")
    chat_conversations = relationship("ChatConversation", back_populates="repository")

class Documentation(Base):
    __tablename__ = "documentation"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"))
    content = Column(Text)
    format = Column(String, default="markdown")
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="documentation")

class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"))
    messages = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="chat_conversations")
