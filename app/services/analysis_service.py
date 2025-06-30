"""
Analysis Service for Task 2.2: Analysis Results Persistence
Provides database persistence for repository analysis results with cache-first strategy
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

import json
from sqlalchemy import text

from app.services.database_service import DatabaseService
from app.services.cache_service import cache_service
from app.services.repository_service import RepositoryService
from app.database.models import AnalysisResult
from app.models.repository_schemas import RepositoryAnalysis
from app.engines.vector_service import VectorService

logger = logging.getLogger(__name__)


@dataclass
class CodeSnippet:
    """Represents a code snippet extracted for RAG context"""
    content: str
    file_path: str
    function_name: Optional[str]
    class_name: Optional[str]
    language: str
    start_line: int
    end_line: int
    snippet_type: str  # 'function', 'class', 'import', 'config'
    metadata: Dict[str, Any]


@dataclass
class AnalysisResultData:
    """Wrapper for analysis result with additional metadata"""
    analysis_result: AnalysisResult
    code_snippets: List[CodeSnippet]
    cached: bool = False


class AnalysisService:
    """Service for persisting and retrieving repository analysis results"""
    
    def __init__(self):
        self.db_service = DatabaseService()
        self.cache_service = cache_service
        self.repository_service = RepositoryService()
        self.vector_service = VectorService()
        
        # Cache configuration
        self._cache_prefix = "analysis:"
        self._cache_ttl = 3600  # 1 hour
        
        # Code snippet extraction configuration
        self._max_snippet_length = 500  # Maximum characters per snippet
        self._snippet_types = ['function', 'class', 'import', 'config', 'comment']
        
    async def save_analysis_results(
        self, 
        repository_id: str, 
        analysis: RepositoryAnalysis,
        branch: str = "main"
    ) -> AnalysisResultData:
        """
        Save analysis results with database persistence and code snippet extraction
        
        Args:
            repository_id: Repository identifier
            analysis: RepositoryAnalysis object to persist
            branch: Git branch (for future multi-branch support)
            
        Returns:
            AnalysisResultData with persisted analysis and extracted snippets
        """
        try:
            logger.info(f"Saving analysis results for repository {repository_id}")
            
            # Extract code snippets for RAG context
            code_snippets = await self._extract_code_snippets(analysis)
            
            # Prepare analysis data for database storage
            analysis_id = f"{repository_id}_{branch}_{int(datetime.utcnow().timestamp())}"
            
            # Convert RepositoryAnalysis to JSON-serializable format
            analysis_data = self._serialize_dict(self._serialize_analysis(analysis))
            
            # Ensure metrics are JSON serializable
            metrics = self._serialize_dict(analysis.metrics)
            
            # Create database record
            analysis_result = AnalysisResult(
                id=analysis_id,
                repository_id=repository_id,
                analysis_data=analysis_data,
                metrics=metrics,
                frameworks_detected=analysis.frameworks_detected,
                categories_used=analysis.categories_used,
                code_snippets=[self._serialize_snippet(snippet) for snippet in code_snippets],
                vector_indexed=False,
                analysis_version="1.0",
                generated_at=datetime.utcnow()
            )
            
            # Save to database
            async with self.db_service.session_factory() as session:
                session.add(analysis_result)
                await session.commit()
                await session.refresh(analysis_result)
            
            # Cache the result
            cache_key = f"{self._cache_prefix}{repository_id}_{branch}"
            await self.cache_service.set(
                cache_key, 
                self._serialize_analysis_result(analysis_result),
                ttl=self._cache_ttl
            )
            
            logger.info(f"Analysis results saved successfully for {repository_id}")
            logger.info(f"Extracted {len(code_snippets)} code snippets for RAG context")
            
            return AnalysisResultData(
                analysis_result=analysis_result,
                code_snippets=code_snippets,
                cached=False
            )
            
        except Exception as e:
            logger.error(f"Error saving analysis results for {repository_id}: {e}")
            raise
    
    async def get_analysis_results(
        self, 
        repository_id: str, 
        branch: str = "main"
    ) -> Optional[AnalysisResultData]:
        """
        Get analysis results with cache-first strategy
        
        Args:
            repository_id: Repository identifier
            branch: Git branch
            
        Returns:
            AnalysisResultData if found, None otherwise
        """
        try:
            cache_key = f"{self._cache_prefix}{repository_id}_{branch}"
            
            # Try cache first
            cached_data = await self.cache_service.get(cache_key)
            if cached_data:
                logger.debug(f"Analysis results cache hit for {repository_id}")
                logger.debug(f"Cached data type: {type(cached_data)}")
                analysis_result = self._deserialize_analysis_result(cached_data)
                code_snippets = [
                    self._deserialize_snippet(snippet_data) 
                    for snippet_data in analysis_result.code_snippets or []
                ]
                return AnalysisResultData(
                    analysis_result=analysis_result,
                    code_snippets=code_snippets,
                    cached=True
                )
            
            # Fallback to database
            logger.debug(f"Analysis results cache miss for {repository_id}, checking database")
            async with self.db_service.session_factory() as session:
                # Get the most recent analysis for this repository/branch
                result = await session.execute(
                    text("""
                    SELECT * FROM analysis_results 
                    WHERE repository_id = :repo_id 
                    ORDER BY generated_at DESC 
                    LIMIT 1
                    """),
                    {"repo_id": repository_id}
                )
                row = result.fetchone()
                
                if row:
                    logger.debug(f"Database row types: analysis_data={type(row.analysis_data)}, metrics={type(row.metrics)}")
                    
                    # Parse JSON fields if they are strings
                    analysis_data = json.loads(row.analysis_data) if isinstance(row.analysis_data, str) else row.analysis_data
                    metrics = json.loads(row.metrics) if isinstance(row.metrics, str) else row.metrics
                    frameworks_detected = json.loads(row.frameworks_detected) if isinstance(row.frameworks_detected, str) else row.frameworks_detected
                    categories_used = json.loads(row.categories_used) if isinstance(row.categories_used, str) else row.categories_used
                    code_snippets = json.loads(row.code_snippets) if isinstance(row.code_snippets, str) else row.code_snippets
                    
                    # Convert row to AnalysisResult object
                    analysis_result = AnalysisResult(
                        id=row.id,
                        repository_id=row.repository_id,
                        analysis_data=analysis_data,
                        metrics=metrics,
                        frameworks_detected=frameworks_detected,
                        categories_used=categories_used,
                        code_snippets=code_snippets,
                        vector_indexed=row.vector_indexed,
                        analysis_version=row.analysis_version,
                        generated_at=row.generated_at
                    )
                    
                    # Cache for future requests (use parsed data)
                    cache_data = {
                        "id": row.id,
                        "repository_id": row.repository_id,
                        "analysis_data": analysis_data,
                        "metrics": metrics,
                        "frameworks_detected": frameworks_detected,
                        "categories_used": categories_used,
                        "code_snippets": code_snippets,
                        "vector_indexed": row.vector_indexed,
                        "analysis_version": row.analysis_version,
                        "generated_at": row.generated_at.isoformat() if hasattr(row.generated_at, 'isoformat') else row.generated_at
                    }
                    await self.cache_service.set(
                        cache_key,
                        cache_data,
                        ttl=self._cache_ttl
                    )
                    
                    # Deserialize code snippets
                    code_snippets = [
                        self._deserialize_snippet(snippet_data) 
                        for snippet_data in analysis_result.code_snippets or []
                    ]
                    
                    logger.debug(f"Analysis results found in database for {repository_id}")
                    return AnalysisResultData(
                        analysis_result=analysis_result,
                        code_snippets=code_snippets,
                        cached=False
                    )
            
            logger.debug(f"No analysis results found for {repository_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving analysis results for {repository_id}: {e}")
            return None
    
    async def list_analysis_results(self) -> List[Dict[str, Any]]:
        """List all analysis results with summary information"""
        try:
            async with self.db_service.session_factory() as session:
                result = await session.execute(
                    text("""
                    SELECT 
                        id, repository_id, generated_at, analysis_version,
                        vector_indexed, frameworks_detected, categories_used
                    FROM analysis_results 
                    ORDER BY generated_at DESC
                    """)
                )
                rows = result.fetchall()
                
                return [
                    {
                        "id": row.id,
                        "repository_id": row.repository_id,
                        "generated_at": row.generated_at.isoformat() if hasattr(row.generated_at, 'isoformat') else row.generated_at,
                        "analysis_version": row.analysis_version,
                        "vector_indexed": row.vector_indexed,
                        "frameworks_detected": json.loads(row.frameworks_detected) if isinstance(row.frameworks_detected, str) else (row.frameworks_detected or []),
                        "categories_used": json.loads(row.categories_used) if isinstance(row.categories_used, str) else (row.categories_used or []),
                        "snippet_count": len(row.code_snippets) if hasattr(row, 'code_snippets') and row.code_snippets else 0
                    }
                    for row in rows
                ]
                
        except Exception as e:
            logger.error(f"Error listing analysis results: {e}")
            return []
    
    async def delete_analysis_results(self, repository_id: str) -> bool:
        """Delete analysis results for a repository"""
        try:
            async with self.db_service.session_factory() as session:
                await session.execute(
                    text("DELETE FROM analysis_results WHERE repository_id = :repo_id"),
                    {"repo_id": repository_id}
                )
                await session.commit()
            
            # Clear cache
            cache_key = f"{self._cache_prefix}{repository_id}_main"
            await self.cache_service.delete(cache_key)
            
            logger.info(f"Analysis results deleted for repository {repository_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting analysis results for {repository_id}: {e}")
            return False
    
    async def search_code_snippets(
        self, 
        query: str, 
        repository_id: Optional[str] = None,
        snippet_type: Optional[str] = None
    ) -> List[CodeSnippet]:
        """
        Search code snippets by content or metadata
        
        Args:
            query: Search query
            repository_id: Optional repository filter
            snippet_type: Optional snippet type filter
            
        Returns:
            List of matching code snippets
        """
        try:
            # Build SQL query with filters
            sql = """
                SELECT code_snippets FROM analysis_results 
                WHERE 1=1
            """
            params = {}
            
            if repository_id:
                sql += " AND repository_id = :repo_id"
                params["repo_id"] = repository_id
            
            async with self.db_service.session_factory() as session:
                result = await session.execute(text(sql), params)
                rows = result.fetchall()
                
                # Extract and filter snippets
                matching_snippets = []
                for row in rows:
                    if row.code_snippets:
                        # Parse JSON if it's a string
                        code_snippets = json.loads(row.code_snippets) if isinstance(row.code_snippets, str) else row.code_snippets
                        for snippet_data in code_snippets:
                            snippet = self._deserialize_snippet(snippet_data)
                            
                            # Apply filters
                            if snippet_type and snippet.snippet_type != snippet_type:
                                continue
                            
                            # Simple text search (can be enhanced with vector search later)
                            if query.lower() in snippet.content.lower() or \
                               query.lower() in snippet.file_path.lower():
                                matching_snippets.append(snippet)
                
                logger.debug(f"Found {len(matching_snippets)} matching code snippets")
                return matching_snippets
                
        except Exception as e:
            logger.error(f"Error searching code snippets: {e}")
            return []
    
    async def get_analysis_stats(self) -> Dict[str, Any]:
        """Get analysis service statistics"""
        try:
            # Get cache service stats
            cache_stats = await self.cache_service.get_cache_stats()
            
            # Count analysis entries in cache
            analysis_cache_count = 0
            if hasattr(self.cache_service, 'cache') and self.cache_service.cache:
                for key in self.cache_service.cache.keys():
                    if key.startswith(self._cache_prefix):
                        analysis_cache_count += 1
            
            # Get database stats
            async with self.db_service.session_factory() as session:
                result = await session.execute(
                    text("""
                    SELECT 
                        COUNT(*) as total_analyses,
                        COUNT(CASE WHEN vector_indexed = true THEN 1 END) as vector_indexed_count,
                        AVG(json_array_length(code_snippets)) as avg_snippets_per_analysis
                    FROM analysis_results
                    """)
                )
                row = result.fetchone()
                
                total_analyses = row.total_analyses if row else 0
                vector_indexed_count = row.vector_indexed_count if row else 0
                avg_snippets = row.avg_snippets_per_analysis if row else 0
            
            return {
                "total_analysis_results": total_analyses,
                "vector_indexed_results": vector_indexed_count,
                "vector_indexing_percentage": (vector_indexed_count / total_analyses * 100) if total_analyses > 0 else 0,
                "average_snippets_per_analysis": avg_snippets or 0,
                "cache_stats": cache_stats,
                "analysis_cache_entries": analysis_cache_count,
                "cache_prefix": self._cache_prefix,
                "max_snippet_length": self._max_snippet_length,
                "supported_snippet_types": self._snippet_types
            }
            
        except Exception as e:
            logger.error(f"Error getting analysis stats: {e}")
            return {"error": str(e)}
    
    async def _extract_code_snippets(self, analysis: RepositoryAnalysis) -> List[CodeSnippet]:
        """Extract code snippets from analysis for RAG context"""
        snippets = []
        
        try:
            for file in analysis.files:
                # Extract function snippets
                for element in file.elements:
                    if element.element_type == "function":
                        snippet = CodeSnippet(
                            content=element.code_snippet[:self._max_snippet_length],
                            file_path=file.file_path,
                            function_name=element.name,
                            class_name=None,
                            language=file.language,
                            start_line=element.start_line,
                            end_line=element.end_line,
                            snippet_type="function",
                            metadata={
                                "complexity": getattr(element, 'complexity_score', None),
                                "dependencies": element.dependencies,
                                "description": element.description
                            }
                        )
                        snippets.append(snippet)
                    
                    elif element.element_type == "class":
                        snippet = CodeSnippet(
                            content=element.code_snippet[:self._max_snippet_length],
                            file_path=file.file_path,
                            function_name=None,
                            class_name=element.name,
                            language=file.language,
                            start_line=element.start_line,
                            end_line=element.end_line,
                            snippet_type="class",
                            metadata={
                                "methods": getattr(element, 'methods', []),
                                "dependencies": element.dependencies,
                                "description": element.description
                            }
                        )
                        snippets.append(snippet)
            
            logger.debug(f"Extracted {len(snippets)} code snippets from analysis")
            return snippets
            
        except Exception as e:
            logger.error(f"Error extracting code snippets: {e}")
            return []
    
    def _serialize_analysis(self, analysis: RepositoryAnalysis) -> Dict[str, Any]:
        """Convert RepositoryAnalysis to JSON-serializable format"""
        try:
            return {
                "repository": analysis.repository.dict() if hasattr(analysis.repository, 'dict') else analysis.repository,
                "files": [file.dict() if hasattr(file, 'dict') else file for file in analysis.files],
                "dependency_graph": analysis.dependency_graph.dict() if hasattr(analysis.dependency_graph, 'dict') else analysis.dependency_graph,
                "metrics": analysis.metrics,
                "categories_used": analysis.categories_used,
                "frameworks_detected": analysis.frameworks_detected
            }
        except Exception as e:
            logger.error(f"Error serializing analysis: {e}")
            return {}
    
    def _serialize_snippet(self, snippet: CodeSnippet) -> Dict[str, Any]:
        """Convert CodeSnippet to JSON-serializable format"""
        return {
            "content": snippet.content,
            "file_path": snippet.file_path,
            "function_name": snippet.function_name,
            "class_name": snippet.class_name,
            "language": snippet.language,
            "start_line": snippet.start_line,
            "end_line": snippet.end_line,
            "snippet_type": snippet.snippet_type,
            "metadata": snippet.metadata
        }
    
    def _deserialize_snippet(self, snippet_data: Dict[str, Any]) -> CodeSnippet:
        """Convert JSON data back to CodeSnippet"""
        return CodeSnippet(
            content=snippet_data.get("content", ""),
            file_path=snippet_data.get("file_path", ""),
            function_name=snippet_data.get("function_name"),
            class_name=snippet_data.get("class_name"),
            language=snippet_data.get("language", "unknown"),
            start_line=snippet_data.get("start_line", 0),
            end_line=snippet_data.get("end_line", 0),
            snippet_type=snippet_data.get("snippet_type", "unknown"),
            metadata=snippet_data.get("metadata", {})
        )
    
    def _serialize_dict(self, data: Any) -> Any:
        """Convert any data structure to JSON-serializable format"""
        if isinstance(data, datetime):
            return data.isoformat()
        elif isinstance(data, str):
            # Already a string, return as-is
            return data
        elif isinstance(data, dict):
            return {k: self._serialize_dict(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self._serialize_dict(item) for item in data]
        elif hasattr(data, 'dict'):
            return self._serialize_dict(data.dict())
        else:
            return data
    
    def _serialize_analysis_result(self, analysis_result: AnalysisResult) -> Dict[str, Any]:
        """Convert AnalysisResult to JSON-serializable format for caching"""
        return {
            "id": analysis_result.id,
            "repository_id": analysis_result.repository_id,
            "analysis_data": analysis_result.analysis_data,
            "metrics": analysis_result.metrics,
            "frameworks_detected": analysis_result.frameworks_detected,
            "categories_used": analysis_result.categories_used,
            "code_snippets": analysis_result.code_snippets,
            "vector_indexed": analysis_result.vector_indexed,
            "analysis_version": analysis_result.analysis_version,
            "generated_at": analysis_result.generated_at.isoformat() if analysis_result.generated_at else None
        }
    
    def _deserialize_analysis_result(self, data: Dict[str, Any]) -> AnalysisResult:
        """Convert JSON data back to AnalysisResult"""
        return AnalysisResult(
            id=data.get("id"),
            repository_id=data.get("repository_id"),
            analysis_data=data.get("analysis_data"),
            metrics=data.get("metrics"),
            frameworks_detected=data.get("frameworks_detected"),
            categories_used=data.get("categories_used"),
            code_snippets=data.get("code_snippets"),
            vector_indexed=data.get("vector_indexed", False),
            analysis_version=data.get("analysis_version", "1.0"),
            generated_at=datetime.fromisoformat(data["generated_at"]) if data.get("generated_at") else datetime.utcnow()
        )


# Global analysis service instance
analysis_service = AnalysisService()