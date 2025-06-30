"""
RAG Schemas for Multi-Agent Researcher
Task 4.1: RAG Service Implementation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
from uuid import UUID, uuid4

class Source(BaseModel):
    """Source of information used in RAG response"""
    source_id: str
    source_type: str  # 'code', 'documentation', 'readme', etc.
    file_path: Optional[str] = None
    line_numbers: Optional[tuple[int, int]] = None
    url: Optional[str] = None
    title: Optional[str] = None
    relevance_score: float = 1.0
    content_preview: Optional[str] = None

class RAGResponse(BaseModel):
    """Response from RAG service"""
    content: str
    sources: List[Dict[str, Any]] = []
    context_used: bool = True
    query: str
    repository_id: str
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    processing_time: float
    token_count: Optional[int] = None
    model_used: str
    cached: bool = False

class ChatRequest(BaseModel):
    """Chat request with optional context"""
    message: str
    context: Optional[Dict[str, Any]] = None
    history: Optional[List[Dict[str, Any]]] = None
    use_rag: bool = True

class ChatResponse(BaseModel):
    """Chat response with sources and context information"""
    response: str
    sources: List[Dict[str, Any]] = []
    context_used: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    repository_id: Optional[str] = None
    branch: Optional[str] = None