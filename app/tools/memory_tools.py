import json
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from uuid import UUID

from app.models.schemas import ResearchResult
from app.core.config import settings

class MemoryStore:
    """
    In-memory store for agent context and results
    
    In production, this would use Redis or another persistent store
    """
    
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._ttl: Dict[str, datetime] = {}
        
    async def save_context(self, research_id: UUID, context: Dict[str, Any]):
        """Save research context"""
        key = f"context:{research_id}"
        self._store[key] = context
        self._ttl[key] = datetime.utcnow() + timedelta(seconds=settings.MEMORY_TTL)
        
    async def get_context(self, research_id: UUID) -> Optional[Dict[str, Any]]:
        """Retrieve research context"""
        key = f"context:{research_id}"
        
        # Check if expired
        if key in self._ttl and datetime.utcnow() > self._ttl[key]:
            del self._store[key]
            del self._ttl[key]
            return None
            
        return self._store.get(key)
        
    async def save_result(self, research_id: UUID, result: ResearchResult):
        """Save final research result"""
        key = f"result:{research_id}"
        self._store[key] = result.dict()
        self._ttl[key] = datetime.utcnow() + timedelta(seconds=settings.MEMORY_TTL)
        
    async def get_result(self, research_id: UUID) -> Optional[ResearchResult]:
        """Retrieve research result"""
        key = f"result:{research_id}"
        
        if key in self._ttl and datetime.utcnow() > self._ttl[key]:
            del self._store[key]
            del self._ttl[key]
            return None
            
        data = self._store.get(key)
        if data:
            return ResearchResult(**data)
        return None
        
    async def cleanup_expired(self):
        """Remove expired entries"""
        now = datetime.utcnow()
        expired_keys = [
            key for key, expiry in self._ttl.items()
            if now > expiry
        ]
        
        for key in expired_keys:
            del self._store[key]
            del self._ttl[key]