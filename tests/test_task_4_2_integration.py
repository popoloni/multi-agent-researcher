"""
Integration tests for Task 4.2: Enhanced Chat API with RAG Integration
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
import json

from app.models.rag_schemas import ChatRequest, ChatResponse, RAGResponse
from app.services.rag_service import RAGService
from app.services.chat_history_service import ChatHistoryService


@pytest.mark.asyncio
async def test_rag_service_integration():
    """Test that RAG service can be initialized and used"""
    # Create a RAG service instance
    rag_service = RAGService()
    
    # Mock the dependencies
    rag_service.vector_db_service = AsyncMock()
    rag_service.vector_db_service.search_documents.return_value = []
    
    rag_service.analysis_service = AsyncMock()
    rag_service.analysis_service.get_analysis_results.return_value = None
    
    rag_service.ai_engine = AsyncMock()
    rag_service.ai_engine.model_name = "test-model"
    rag_service.ai_engine.analyze.return_value = {
        "analysis": {
            "explanation": "This is a test response"
        }
    }
    
    rag_service.cache_service = AsyncMock()
    rag_service.cache_service.get.return_value = None
    rag_service.cache_service.set.return_value = None
    
    # Test the generate_response method
    response = await rag_service.generate_response(
        query="Test query",
        repo_id="test-repo"
    )
    
    # Verify response
    assert isinstance(response, RAGResponse)
    assert response.repository_id == "test-repo"
    assert response.query == "Test query"


@pytest.mark.asyncio
async def test_chat_history_service_integration():
    """Test that chat history service can be initialized and used"""
    # Create a chat history service instance
    chat_service = ChatHistoryService()
    
    # Mock the dependencies
    chat_service.db_service = AsyncMock()
    chat_service.db_service.session_factory = AsyncMock()
    mock_session = AsyncMock()
    chat_service.db_service.session_factory.return_value = mock_session
    
    chat_service.cache_service = AsyncMock()
    chat_service.cache_service.get.return_value = None
    chat_service.cache_service.set.return_value = None
    chat_service.cache_service.delete.return_value = None
    
    # Mock the _get_or_create_conversation method
    chat_service._get_or_create_conversation = AsyncMock()
    chat_service._get_or_create_conversation.return_value = {
        "id": "test-conversation-id",
        "repository_id": "test-repo",
        "session_id": "test-session",
        "branch": "main",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Test the save_message method
    result = await chat_service.save_message(
        repository_id="test-repo",
        message="Test message",
        is_user=True,
        session_id="test-session",
        branch="main"
    )
    
    # Verify result
    assert result["content"] == "Test message"
    assert result["role"] == "user"
    
    # Test the get_conversation_history method
    chat_service._get_conversation = AsyncMock()
    chat_service._get_conversation.return_value = {
        "id": "test-conversation-id",
        "repository_id": "test-repo",
        "session_id": "test-session",
        "branch": "main",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    chat_service._get_conversation_messages = AsyncMock()
    chat_service._get_conversation_messages.return_value = [
        {
            "id": "test-message-1",
            "content": "Test message 1",
            "role": "user",
            "timestamp": datetime.utcnow().isoformat()
        },
        {
            "id": "test-message-2",
            "content": "Test response 1",
            "role": "assistant",
            "timestamp": datetime.utcnow().isoformat()
        }
    ]
    
    history = await chat_service.get_conversation_history(
        repository_id="test-repo",
        session_id="test-session",
        branch="main"
    )
    
    # Verify history
    assert len(history["messages"]) == 2
    assert history["repository_id"] == "test-repo"
    assert history["session_id"] == "test-session"


@pytest.mark.asyncio
async def test_rag_and_chat_history_integration():
    """Test that RAG service and chat history service can work together"""
    # Create service instances
    rag_service = RAGService()
    chat_service = ChatHistoryService()
    
    # Mock RAG service dependencies
    rag_service.vector_db_service = AsyncMock()
    rag_service.vector_db_service.search_documents.return_value = []
    
    rag_service.analysis_service = AsyncMock()
    rag_service.analysis_service.get_analysis_results.return_value = None
    
    rag_service.ai_engine = AsyncMock()
    rag_service.ai_engine.model_name = "test-model"
    rag_service.ai_engine.analyze.return_value = {
        "analysis": {
            "explanation": "This is a test response"
        }
    }
    
    rag_service.cache_service = AsyncMock()
    rag_service.cache_service.get.return_value = None
    rag_service.cache_service.set.return_value = None
    
    # Mock chat history service dependencies
    chat_service.db_service = AsyncMock()
    chat_service.db_service.session_factory = AsyncMock()
    mock_session = AsyncMock()
    chat_service.db_service.session_factory.return_value = mock_session
    
    chat_service.cache_service = AsyncMock()
    chat_service.cache_service.get.return_value = None
    chat_service.cache_service.set.return_value = None
    chat_service.cache_service.delete.return_value = None
    
    # Mock the _get_or_create_conversation method
    chat_service._get_or_create_conversation = AsyncMock()
    chat_service._get_or_create_conversation.return_value = {
        "id": "test-conversation-id",
        "repository_id": "test-repo",
        "session_id": "test-session",
        "branch": "main",
        "created_at": datetime.utcnow().isoformat()
    }
    
    # Mock the get_context_for_rag method
    chat_service.get_context_for_rag = AsyncMock()
    chat_service.get_context_for_rag.return_value = {
        "history": [
            {
                "id": "test-message-1",
                "content": "Test message 1",
                "role": "user",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "id": "test-message-2",
                "content": "Test response 1",
                "role": "assistant",
                "timestamp": datetime.utcnow().isoformat()
            }
        ],
        "repository_id": "test-repo",
        "branch": "main"
    }
    
    # Test the integration
    # 1. Save user message
    await chat_service.save_message(
        repository_id="test-repo",
        message="Test query",
        is_user=True,
        session_id="test-session",
        branch="main"
    )
    
    # 2. Get conversation context
    context = await chat_service.get_context_for_rag(
        repository_id="test-repo",
        session_id="test-session",
        branch="main"
    )
    
    # 3. Generate RAG response
    rag_response = await rag_service.generate_response(
        query="Test query",
        repo_id="test-repo",
        context=context
    )
    
    # 4. Save assistant response
    await chat_service.save_message(
        repository_id="test-repo",
        message=rag_response.content,
        is_user=False,
        session_id="test-session",
        branch="main",
        metadata={"sources": rag_response.sources}
    )
    
    # Verify integration
    assert isinstance(rag_response, RAGResponse)
    assert rag_response.repository_id == "test-repo"
    assert rag_response.query == "Test query"
    
    # Verify service calls
    chat_service._get_or_create_conversation.assert_called()
    chat_service.get_context_for_rag.assert_called_once()
    rag_service.vector_db_service.search_documents.assert_called_once()
    rag_service.ai_engine.analyze.assert_called_once()