"""
Test suite for Task 4.1: RAG Service Implementation
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
import json
from datetime import datetime

from app.services.rag_service import RAGService, ContextDocument
from app.models.rag_schemas import RAGResponse
from app.services.vector_database_service import SearchResult, DocumentType
from app.engines.vector_service import VectorDocument


# Mock data for testing
@pytest.fixture
def mock_vector_document():
    return VectorDocument(
        id="test-doc-1",
        content="def test_function():\n    return 'Hello, World!'",
        metadata={
            "file_path": "/test/file.py",
            "document_type": "function",
            "repository_id": "test-repo"
        },
        embedding=[0.1, 0.2, 0.3],
        created_at=datetime.utcnow()
    )


@pytest.fixture
def mock_search_result(mock_vector_document):
    return SearchResult(
        document=mock_vector_document,
        similarity_score=0.85,
        document_type=DocumentType.FUNCTION,
        repository_id="test-repo",
        file_path="/test/file.py",
        line_numbers=(1, 2),
        context="Function context"
    )


@pytest.fixture
def mock_context_document():
    return ContextDocument(
        content="def test_function():\n    return 'Hello, World!'",
        source_type="function",
        file_path="/test/file.py",
        line_numbers=(1, 2),
        relevance_score=0.85,
        metadata={"document_type": "function"}
    )


@pytest.fixture
def mock_analysis_context():
    return {
        "repository_id": "test-repo",
        "language": "python",
        "framework": "fastapi",
        "file_count": 10,
        "total_lines": 500,
        "code_snippets": [
            {
                "content": "def another_function():\n    return 'Test'",
                "file_path": "/test/another_file.py",
                "function_name": "another_function",
                "class_name": None,
                "language": "python",
                "snippet_type": "function"
            }
        ]
    }


class TestRAGService:
    """Test suite for RAG Service implementation"""

    @pytest.fixture(autouse=True)
    def setup_service(self):
        """Set up RAG service with mocked dependencies"""
        # Create mocks for dependencies
        self.vector_db_service = AsyncMock()
        self.documentation_service = AsyncMock()
        self.analysis_service = AsyncMock()
        self.content_indexing_service = AsyncMock()
        self.ai_engine = AsyncMock()
        self.cache_service = AsyncMock()
        
        # Create RAG service
        self.rag_service = RAGService()
        
        # Replace dependencies with mocks
        self.rag_service.vector_db_service = self.vector_db_service
        self.rag_service.documentation_service = self.documentation_service
        self.rag_service.analysis_service = self.analysis_service
        self.rag_service.content_indexing_service = self.content_indexing_service
        self.rag_service.ai_engine = self.ai_engine
        self.rag_service.cache_service = self.cache_service
        
        # Configure cache service mock
        self.cache_service.get.return_value = None
        self.cache_service.set.return_value = None
        
        # Configure AI engine mock
        self.ai_engine.model_name = "test-model"
        self.ai_engine.provider_name = "test-provider"
        self.ai_engine.analyze.return_value = {
            "analysis": {
                "explanation": "This is a test response."
            }
        }

    @pytest.mark.asyncio
    async def test_generate_response_retrieves_documents(self, mock_search_result):
        """Test that generate_response retrieves relevant documents"""
        # Configure mocks
        self.vector_db_service.search_documents.return_value = [mock_search_result]
        self.analysis_service.get_analysis_results.return_value = None
        
        # Call the method
        response = await self.rag_service.generate_response(
            query="How does test_function work?",
            repo_id="test-repo"
        )
        
        # Verify document retrieval was called
        self.vector_db_service.search_documents.assert_called_once()
        
        # Verify response
        assert isinstance(response, RAGResponse)
        assert "This is a test response." in response.content
        assert response.context_used is True
        assert len(response.sources) > 0
        assert response.repository_id == "test-repo"

    @pytest.mark.asyncio
    async def test_generate_response_uses_cache(self):
        """Test that generate_response uses cache when available"""
        # Configure cache hit
        cached_response = {
            "content": "Cached response",
            "sources": [{"source_id": "cached-1", "source_type": "function"}],
            "context_used": True,
            "query": "How does test_function work?",
            "repository_id": "test-repo",
            "generated_at": datetime.utcnow().isoformat(),
            "processing_time": 0.5,
            "model_used": "test-model"
        }
        self.cache_service.get.return_value = cached_response
        
        # Call the method
        response = await self.rag_service.generate_response(
            query="How does test_function work?",
            repo_id="test-repo"
        )
        
        # Verify cache was checked
        self.cache_service.get.assert_called_once()
        
        # Verify vector search was not called
        self.vector_db_service.search_documents.assert_not_called()
        
        # Verify response
        assert isinstance(response, RAGResponse)
        assert response.content == "Cached response"
        assert response.cached is True

    @pytest.mark.asyncio
    async def test_generate_response_with_analysis_context(self, mock_search_result, mock_analysis_context):
        """Test that generate_response incorporates analysis context"""
        # Configure mocks
        self.vector_db_service.search_documents.return_value = [mock_search_result]
        
        # Mock analysis service
        analysis_result_mock = AsyncMock()
        analysis_result_mock.analysis_result = AsyncMock()
        analysis_result_mock.analysis_result.language = "python"
        analysis_result_mock.analysis_result.framework = "fastapi"
        analysis_result_mock.analysis_result.file_count = 10
        analysis_result_mock.analysis_result.total_lines = 500
        analysis_result_mock.code_snippets = [
            AsyncMock(
                content="def another_function():\n    return 'Test'",
                file_path="/test/another_file.py",
                function_name="another_function",
                class_name=None,
                language="python",
                snippet_type="function"
            )
        ]
        
        self.analysis_service.get_analysis_results.return_value = analysis_result_mock
        
        # Call the method
        response = await self.rag_service.generate_response(
            query="How does test_function work?",
            repo_id="test-repo"
        )
        
        # Verify analysis service was called
        self.analysis_service.get_analysis_results.assert_called_once_with("test-repo")
        
        # Verify AI engine was called with context
        ai_call_args = self.ai_engine.analyze.call_args[0][0]
        assert "Repository Language: python" in ai_call_args.context["prompt"]
        
        # Verify response
        assert isinstance(response, RAGResponse)
        assert response.context_used is True

    @pytest.mark.asyncio
    async def test_generate_response_handles_errors(self):
        """Test that generate_response handles errors gracefully"""
        # Configure mock to raise exception
        self.vector_db_service.search_documents.side_effect = Exception("Test error")
        
        # Configure AI engine to return error message
        self.ai_engine.analyze.return_value = {
            "analysis": {
                "explanation": "Error occurred: Test error"
            }
        }
        
        # Call the method
        response = await self.rag_service.generate_response(
            query="How does test_function work?",
            repo_id="test-repo"
        )
        
        # Verify response is still returned despite the error
        assert isinstance(response, RAGResponse)
        assert response.context_used is False
        assert len(response.sources) == 0

    @pytest.mark.asyncio
    async def test_build_prompt_formats_correctly(self, mock_context_document, mock_analysis_context):
        """Test that _build_prompt formats the prompt correctly"""
        # Call the method
        prompt, sources = self.rag_service._build_prompt(
            query="How does test_function work?",
            context_documents=[mock_context_document],
            analysis_context=mock_analysis_context,
            user_context=None
        )
        
        # Verify prompt structure
        assert "You are an intelligent code assistant" in prompt
        assert "Repository Language: python" in prompt
        assert "Framework: fastapi" in prompt
        assert "File Count: 10" in prompt
        assert "Total Lines: 500" in prompt
        assert "Document 1: Function" in prompt
        assert "File: /test/file.py" in prompt
        assert "def test_function():" in prompt
        assert "Snippet 1: Function" in prompt
        assert "def another_function():" in prompt
        assert "User Question: How does test_function work?" in prompt
        
        # Verify sources
        assert len(sources) == 2
        assert sources[0]["source_type"] == "function"
        assert sources[0]["file_path"] == "/test/file.py"
        assert sources[1]["source_type"] == "code_snippet"
        assert sources[1]["file_path"] == "/test/another_file.py"

    @pytest.mark.asyncio
    async def test_health_status(self):
        """Test that get_health_status returns correct information"""
        # Configure mocks
        self.vector_db_service.get_health_status.return_value = {
            "status": "healthy",
            "vector_database": {"status": "healthy"}
        }
        
        # Call the method
        health_status = await self.rag_service.get_health_status()
        
        # Verify health status
        assert health_status["status"] == "healthy"
        assert "vector_database" in health_status
        assert "ai_engine" in health_status
        assert "performance" in health_status
        assert health_status["ai_engine"]["model"] == "test-model"
        assert health_status["ai_engine"]["provider"] == "test-provider"