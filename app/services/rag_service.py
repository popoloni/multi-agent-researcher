"""
RAG Service Implementation
Task 4.1: RAG Service Implementation

This service provides RAG (Retrieval-Augmented Generation) capabilities for intelligent
responses about repository code and documentation, leveraging the vector database
and content indexing infrastructure.
"""

import asyncio
import logging
import time
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime
from dataclasses import dataclass, asdict

from app.services.vector_database_service import VectorDatabaseService, DocumentType, SearchResult
from app.services.documentation_service import DocumentationService
from app.services.analysis_service import AnalysisService
from app.services.content_indexing_service import ContentIndexingService, ContentType
from app.services.cache_service import cache_service
from app.engines.ai_engine import AIEngine, AnalysisType, ModelComplexity, AnalysisRequest
from app.models.rag_schemas import RAGResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ContextDocument:
    """Document retrieved for context building"""
    content: str
    source_type: str
    file_path: Optional[str] = None
    line_numbers: Optional[Tuple[int, int]] = None
    relevance_score: float = 1.0
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class RAGService:
    """
    RAG (Retrieval-Augmented Generation) service for intelligent responses
    about repository code and documentation.
    
    Features:
    - Semantic search for relevant context
    - Context aggregation from multiple sources
    - Intelligent prompt construction
    - Response generation with source attribution
    - Response caching for performance
    - Health monitoring and diagnostics
    """
    
    def __init__(self):
        self.vector_db_service = VectorDatabaseService()
        self.documentation_service = DocumentationService()
        self.analysis_service = AnalysisService()
        self.content_indexing_service = ContentIndexingService()
        self.ai_engine = AIEngine()
        self.cache_service = cache_service
        
        # Cache configuration
        self._cache_prefix = "rag_response:"
        self._cache_ttl = 3600  # 1 hour
        
        # Context configuration
        self.max_context_documents = 10
        self.max_context_length = 6000  # Maximum context length in characters
        self.relevance_threshold = 0.6  # Minimum relevance score for context inclusion
        
        # Performance tracking
        self.performance_stats = {
            "total_requests": 0,
            "cache_hits": 0,
            "avg_processing_time": 0.0,
            "last_processing_time": None
        }
        
        logger.info("RAGService initialized")
    
    async def generate_response(
        self, 
        query: str, 
        repo_id: str, 
        context: Dict[str, Any] = None
    ) -> RAGResponse:
        """
        Generate intelligent response using RAG (Retrieval-Augmented Generation).
        
        Args:
            query: User query
            repo_id: Repository identifier
            context: Additional context (conversation history, etc.)
            
        Returns:
            RAGResponse with generated content and source attribution
        """
        start_time = time.time()
        self.performance_stats["total_requests"] += 1
        
        try:
            # Check cache first
            cache_key = self._build_cache_key(query, repo_id, context)
            cached_response = await self.cache_service.get(cache_key)
            
            if cached_response:
                self.performance_stats["cache_hits"] += 1
                logger.debug(f"Cache hit for query: {query[:50]}...")
                cached_response["cached"] = True
                return RAGResponse(**cached_response)
            
            # 1. Retrieve relevant documents and code using vector search
            relevant_documents = await self._retrieve_relevant_documents(query, repo_id)
            
            # 2. Combine with repository analysis data
            analysis_context = await self._get_analysis_context(repo_id)
            
            # 3. Build context-aware prompt
            prompt, sources = self._build_prompt(query, relevant_documents, analysis_context, context)
            
            # 4. Generate response using existing AI infrastructure
            response_content = await self._generate_ai_response(prompt, query, repo_id)
            
            # Calculate processing time
            processing_time = time.time() - start_time
            self._update_performance_stats(processing_time)
            
            # Create RAG response
            rag_response = RAGResponse(
                content=response_content,
                sources=sources,
                context_used=len(relevant_documents) > 0,
                query=query,
                repository_id=repo_id,
                generated_at=datetime.utcnow(),
                processing_time=processing_time,
                model_used=self.ai_engine.model_name,
                cached=False
            )
            
            # 5. Cache response for performance
            await self.cache_service.set(
                cache_key,
                rag_response.model_dump(),
                ttl=self._cache_ttl
            )
            
            logger.info(f"Generated RAG response for query in {processing_time:.3f}s")
            
            return rag_response
            
        except Exception as e:
            logger.error(f"Failed to generate RAG response: {e}")
            processing_time = time.time() - start_time
            
            # Return error response
            return RAGResponse(
                content=f"I encountered an error while processing your question: {str(e)}. Please try again or contact support if the issue persists.",
                sources=[],
                context_used=False,
                query=query,
                repository_id=repo_id,
                generated_at=datetime.utcnow(),
                processing_time=processing_time,
                model_used=self.ai_engine.model_name,
                cached=False
            )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """Get RAG service health status and performance metrics"""
        try:
            # Check vector database health
            vector_db_health = await self.vector_db_service.get_health_status()
            
            # Check AI engine health
            ai_engine_health = {
                "status": "healthy",
                "model": self.ai_engine.model_name,
                "provider": self.ai_engine.provider_name
            }
            
            # Get cache stats
            cache_stats = await self.cache_service.get_stats() if hasattr(self.cache_service, 'get_stats') else {}
            
            return {
                "status": "healthy",
                "vector_database": vector_db_health,
                "ai_engine": ai_engine_health,
                "performance": self.performance_stats,
                "cache": cache_stats,
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "last_updated": datetime.utcnow().isoformat()
            }
    
    # Private helper methods
    
    async def _retrieve_relevant_documents(self, query: str, repo_id: str) -> List[ContextDocument]:
        """Retrieve relevant documents for context building"""
        try:
            # Search for code and documentation using vector search
            search_results = await self.vector_db_service.search_documents(
                query=query,
                repository_id=repo_id,
                limit=self.max_context_documents,
                similarity_threshold=self.relevance_threshold
            )
            
            # Convert search results to context documents
            context_documents = []
            for result in search_results:
                doc_type = result.document_type.value if hasattr(result, 'document_type') else "unknown"
                
                context_doc = ContextDocument(
                    content=result.document.content,
                    source_type=doc_type,
                    file_path=result.file_path,
                    line_numbers=result.line_numbers,
                    relevance_score=result.similarity_score,
                    metadata=result.document.metadata
                )
                context_documents.append(context_doc)
            
            # If we don't have enough context, try content indexing service
            if len(context_documents) < self.max_context_documents / 2:
                content_results = await self.content_indexing_service.search_content(
                    query=query,
                    repository_id=repo_id,
                    limit=self.max_context_documents - len(context_documents)
                )
                
                for result in content_results:
                    # Avoid duplicates
                    if any(doc.content == result["content"] for doc in context_documents):
                        continue
                        
                    context_doc = ContextDocument(
                        content=result["content"],
                        source_type=result.get("content_type", "unknown"),
                        file_path=result.get("file_path"),
                        line_numbers=result.get("line_numbers"),
                        relevance_score=result.get("similarity_score", 0.7),
                        metadata=result.get("metadata", {})
                    )
                    context_documents.append(context_doc)
            
            # Sort by relevance score
            context_documents.sort(key=lambda x: x.relevance_score, reverse=True)
            
            # Limit context length
            total_length = 0
            filtered_documents = []
            for doc in context_documents:
                doc_length = len(doc.content)
                if total_length + doc_length <= self.max_context_length:
                    filtered_documents.append(doc)
                    total_length += doc_length
                else:
                    # Truncate the last document if needed
                    remaining_length = self.max_context_length - total_length
                    if remaining_length > 100:  # Only include if we can get a meaningful chunk
                        doc.content = doc.content[:remaining_length] + "..."
                        filtered_documents.append(doc)
                    break
            
            logger.debug(f"Retrieved {len(filtered_documents)} context documents for query")
            return filtered_documents
            
        except Exception as e:
            logger.error(f"Failed to retrieve relevant documents: {e}")
            return []
    
    async def _get_analysis_context(self, repo_id: str) -> Dict[str, Any]:
        """Get repository analysis context"""
        try:
            # Get analysis results from analysis service
            analysis_result = await self.analysis_service.get_analysis_results(repo_id)
            
            if not analysis_result or not analysis_result.analysis_result:
                return {}
            
            # Extract relevant information from analysis
            analysis_data = analysis_result.analysis_result
            
            # Build analysis context
            context = {
                "repository_id": repo_id,
                "language": analysis_data.language,
                "framework": analysis_data.framework,
                "file_count": analysis_data.file_count,
                "total_lines": analysis_data.total_lines,
                "code_snippets": []
            }
            
            # Add code snippets if available
            if hasattr(analysis_result, 'code_snippets'):
                for snippet in analysis_result.code_snippets[:5]:  # Limit to top 5 snippets
                    context["code_snippets"].append({
                        "content": snippet.content,
                        "file_path": snippet.file_path,
                        "function_name": snippet.function_name,
                        "class_name": snippet.class_name,
                        "language": snippet.language,
                        "snippet_type": snippet.snippet_type
                    })
            
            return context
            
        except Exception as e:
            logger.error(f"Failed to get analysis context: {e}")
            return {}
    
    def _build_prompt(
        self, 
        query: str, 
        context_documents: List[ContextDocument],
        analysis_context: Dict[str, Any],
        user_context: Optional[Dict[str, Any]]
    ) -> Tuple[str, List[Dict[str, Any]]]:
        """Build context-aware prompt for AI response generation"""
        # Initialize sources list for attribution
        sources = []
        
        # Build context section
        context_text = "# Repository Context\n\n"
        
        # Add analysis context
        if analysis_context:
            context_text += f"Repository Language: {analysis_context.get('language', 'Unknown')}\n"
            if analysis_context.get('framework'):
                context_text += f"Framework: {analysis_context.get('framework')}\n"
            context_text += f"File Count: {analysis_context.get('file_count', 0)}\n"
            context_text += f"Total Lines: {analysis_context.get('total_lines', 0)}\n\n"
        
        # Add retrieved documents
        if context_documents:
            context_text += "# Relevant Code and Documentation\n\n"
            
            for i, doc in enumerate(context_documents):
                # Add document to context
                context_text += f"## Document {i+1}: {doc.source_type.capitalize()}\n"
                
                if doc.file_path:
                    context_text += f"File: {doc.file_path}\n"
                
                if doc.line_numbers:
                    context_text += f"Lines: {doc.line_numbers[0]}-{doc.line_numbers[1]}\n"
                
                context_text += f"\n```\n{doc.content}\n```\n\n"
                
                # Add to sources for attribution
                source = {
                    "source_id": f"doc-{i+1}",
                    "source_type": doc.source_type,
                    "file_path": doc.file_path,
                    "line_numbers": doc.line_numbers,
                    "relevance_score": doc.relevance_score,
                    "content_preview": doc.content[:100] + "..." if len(doc.content) > 100 else doc.content
                }
                sources.append(source)
        else:
            context_text += "No specific code or documentation found for this query.\n\n"
        
        # Add code snippets from analysis if available
        if analysis_context and analysis_context.get("code_snippets"):
            context_text += "# Key Code Snippets from Analysis\n\n"
            
            for i, snippet in enumerate(analysis_context["code_snippets"]):
                context_text += f"## Snippet {i+1}: {snippet.get('snippet_type', 'Code').capitalize()}\n"
                if snippet.get("file_path"):
                    context_text += f"File: {snippet.get('file_path')}\n"
                if snippet.get("function_name"):
                    context_text += f"Function: {snippet.get('function_name')}\n"
                if snippet.get("class_name"):
                    context_text += f"Class: {snippet.get('class_name')}\n"
                
                context_text += f"\n```{snippet.get('language', '')}\n{snippet.get('content', '')}\n```\n\n"
                
                # Add to sources
                source = {
                    "source_id": f"snippet-{i+1}",
                    "source_type": "code_snippet",
                    "file_path": snippet.get("file_path"),
                    "function_name": snippet.get("function_name"),
                    "class_name": snippet.get("class_name"),
                    "content_preview": snippet.get("content", "")[:100] + "..." if len(snippet.get("content", "")) > 100 else snippet.get("content", "")
                }
                sources.append(source)
        
        # Add user context if available
        conversation_history = ""
        if user_context and user_context.get("history"):
            conversation_history = "# Conversation History\n\n"
            for message in user_context["history"]:
                role = message.get("role", "user")
                content = message.get("content", "")
                conversation_history += f"{role.capitalize()}: {content}\n\n"
        
        # Build the final prompt
        prompt = f"""You are an intelligent code assistant that helps users understand and work with codebases.
Answer the following question based on the provided repository context.

{context_text}

{conversation_history}

User Question: {query}

Provide a clear, accurate, and helpful response. Reference specific files, functions, or code snippets when relevant.
If the context doesn't contain enough information to answer the question fully, acknowledge the limitations and provide the best guidance possible based on what's available.
"""
        
        return prompt, sources
    
    async def _generate_ai_response(self, prompt: str, query: str, repo_id: str) -> str:
        """Generate response using AI engine"""
        try:
            # Create analysis request
            analysis_request = AnalysisRequest(
                analysis_type=AnalysisType.CODE_EXPLANATION,
                code_element=None,  # Not needed for this use case
                context={
                    "repository_id": repo_id,
                    "query": query,
                    "prompt": prompt
                },
                complexity=ModelComplexity.MEDIUM,
                streaming=False,
                max_tokens=2000
            )
            
            # Generate response
            ai_response = await self.ai_engine.analyze(analysis_request)
            
            # Extract response content
            if ai_response and "analysis" in ai_response:
                return ai_response["analysis"].get("explanation", "I couldn't generate a response for your question.")
            else:
                return "I couldn't generate a response for your question. Please try again or rephrase your query."
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return f"I encountered an error while generating a response: {str(e)}. Please try again or contact support if the issue persists."
    
    def _build_cache_key(self, query: str, repo_id: str, context: Optional[Dict[str, Any]]) -> str:
        """Build cache key for RAG response"""
        # Use only the last message from history if available
        history_key = ""
        if context and context.get("history"):
            last_messages = context["history"][-3:] if len(context["history"]) > 3 else context["history"]
            history_key = "_".join([msg.get("content", "")[:20] for msg in last_messages])
        
        return f"{self._cache_prefix}{repo_id}_{query[:50]}_{history_key}"
    
    def _update_performance_stats(self, processing_time: float):
        """Update performance statistics"""
        self.performance_stats["last_processing_time"] = processing_time
        
        # Update average processing time
        total_requests = self.performance_stats["total_requests"]
        current_avg = self.performance_stats["avg_processing_time"]
        
        if total_requests == 1:
            self.performance_stats["avg_processing_time"] = processing_time
        else:
            # Weighted average (more weight to recent times)
            self.performance_stats["avg_processing_time"] = (current_avg * 0.8) + (processing_time * 0.2)