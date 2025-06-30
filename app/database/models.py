"""
Database models for Multi-Agent Researcher
"""
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey, JSON, Integer, Boolean
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

class LanguageType(PyEnum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JAVA = "java"
    CSHARP = "csharp"
    GO = "go"
    R = "r"
    JUPYTER = "jupyter"
    UNKNOWN = "unknown"

class Repository(Base):
    __tablename__ = "repositories"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    url = Column(String)
    local_path = Column(String)
    github_owner = Column(String)
    github_repo = Column(String)
    language = Column(Enum(LanguageType), default=LanguageType.UNKNOWN)
    framework = Column(String)
    description = Column(Text)
    clone_status = Column(Enum(CloneStatus), default=CloneStatus.PENDING)
    file_count = Column(Integer, default=0)
    total_lines = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documentation = relationship("Documentation", back_populates="repository")
    chat_conversations = relationship("ChatConversation", back_populates="repository")
    analysis_results = relationship("AnalysisResult", back_populates="repository")

class Documentation(Base):
    __tablename__ = "documentation"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"))
    content = Column(Text)
    format = Column(String, default="markdown")
    vector_indexed = Column(Boolean, default=False)
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="documentation")

class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"))
    analysis_data = Column(JSON)  # Store the complete RepositoryAnalysis as JSON
    metrics = Column(JSON)  # Store metrics separately for easy querying
    frameworks_detected = Column(JSON)  # Store detected frameworks
    categories_used = Column(JSON)  # Store categories found
    code_snippets = Column(JSON)  # Store extracted code snippets for RAG
    vector_indexed = Column(Boolean, default=False)  # Track vector indexing status
    analysis_version = Column(String, default="1.0")  # Track analysis version for migrations
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="analysis_results")

class ChatConversation(Base):
    __tablename__ = "chat_conversations"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"))
    session_id = Column(String, nullable=False)
    branch = Column(String, default="main")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="chat_conversations")
    messages = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")


class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True)
    conversation_id = Column(String, ForeignKey("chat_conversations.id"))
    content = Column(Text, nullable=False)
    role = Column(String, default="user")  # user or assistant
    metadata_json = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("ChatConversation", back_populates="messages")

class VectorDocument(Base):
    __tablename__ = "vector_documents"
    
    document_id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"))
    document_type = Column(String)  # code_file, documentation, readme, etc.
    file_path = Column(String)
    content_preview = Column(Text)  # First 500 chars for keyword search
    metadata_json = Column(JSON)
    embedding_dimension = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository")

class VectorIndex(Base):
    __tablename__ = "vector_indexes"
    
    id = Column(String, primary_key=True)
    repository_id = Column(String, ForeignKey("repositories.id"))
    index_name = Column(String)
    document_count = Column(Integer, default=0)
    embedding_model = Column(String)
    index_metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository")
