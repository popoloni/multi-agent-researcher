"""
Test suite for Task 4.2: Enhanced Chat API with RAG Integration
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.main import app
from app.models.rag_schemas import ChatRequest, ChatResponse, RAGResponse
from app.services.rag_service import RAGService
from app.services.chat_history_service import ChatHistoryService


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_rag_service():
    """Create a mock RAG service"""
    mock_service = AsyncMock(spec=RAGService)
    
    # Configure mock response
    mock_response = RAGResponse(
        content="This is a test RAG response",
        sources=[{"source_id": "test-1", "source_type": "code", "file_path": "/test/file.py"}],
        context_used=True,
        query="Test query",
        repository_id="test-repo",
        processing_time=0.1,
        model_used="test-model"
    )
    
    mock_service.generate_response.return_value = mock_response
    return mock_service


@pytest.fixture
def mock_chat_history_service():
    """Create a mock chat history service"""
    mock_service = AsyncMock(spec=ChatHistoryService)
    
    # Configure mock responses
    mock_service.save_message.return_value = {
        "id": "test-message-id",
        "content": "Test message",
        "role": "user",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    mock_service.get_conversation_history.return_value = {
        "messages": [
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
        "session_id": "test-session",
        "branch": "main"
    }
    
    mock_service.get_context_for_rag.return_value = {
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
    
    mock_service.clear_conversation_history.return_value = {
        "success": True,
        "repository_id": "test-repo",
        "session_id": "test-session",
        "branch": "main",
        "message": "Chat history cleared successfully"
    }
    
    mock_service._get_or_create_conversation.return_value = {
        "id": "test-conversation-id",
        "repository_id": "test-repo",
        "session_id": "test-session",
        "branch": "main",
        "created_at": datetime.utcnow().isoformat()
    }
    
    return mock_service


@pytest.fixture
def mock_kenobi_agent():
    """Create a mock Kenobi agent"""
    mock_agent = AsyncMock()
    
    # Configure mock repository service
    mock_repo_service = AsyncMock()
    mock_repo_service.get_repository_metadata.return_value = {
        "id": "test-repo",
        "name": "Test Repository",
        "description": "Test repository for unit tests",
        "url": "https://github.com/test/repo"
    }
    mock_agent.repository_service = mock_repo_service
    
    # Configure mock chat response
    mock_agent.chat_about_repository.return_value = {
        "answer": "This is a test response from Kenobi",
        "sources": [{"source_id": "test-1", "source_type": "code", "file_path": "/test/file.py"}],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return mock_agent


class TestEnhancedChatAPI:
    """Test suite for the enhanced chat API with RAG integration"""
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self, monkeypatch):
        """Set up mocks for all tests in this class"""
        # Create mock services
        self.mock_rag_service = AsyncMock(spec=RAGService)
        self.mock_chat_history_service = AsyncMock(spec=ChatHistoryService)
        self.mock_kenobi_agent = AsyncMock()
        
        # Configure mock repository service
        self.mock_repo_service = AsyncMock()
        self.mock_repo_service.get_repository_metadata.return_value = {
            "id": "test-repo",
            "name": "Test Repository",
            "description": "Test repository for unit tests",
            "url": "https://github.com/test/repo"
        }
        self.mock_kenobi_agent.repository_service = self.mock_repo_service
        
        # Configure mock chat response
        self.mock_kenobi_agent.chat_about_repository.return_value = {
            "answer": "This is a test response from Kenobi",
            "sources": [{"source_id": "test-1", "source_type": "code", "file_path": "/test/file.py"}],
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Configure mock RAG response
        self.mock_rag_service.generate_response.return_value = RAGResponse(
            content="This is a test RAG response",
            sources=[{"source_id": "test-1", "source_type": "code", "file_path": "/test/file.py"}],
            context_used=True,
            query="Test query",
            repository_id="test-repo",
            processing_time=0.1,
            model_used="test-model"
        )
        
        # Configure mock chat history service
        self.mock_chat_history_service.save_message.return_value = {
            "id": "test-message-id",
            "content": "Test message",
            "role": "user",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.mock_chat_history_service.get_conversation_history.return_value = {
            "messages": [
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
            "session_id": "test-session",
            "branch": "main"
        }
        
        self.mock_chat_history_service.get_context_for_rag.return_value = {
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
        
        self.mock_chat_history_service.clear_conversation_history.return_value = {
            "success": True,
            "repository_id": "test-repo",
            "session_id": "test-session",
            "branch": "main",
            "message": "Chat history cleared successfully"
        }
        
        self.mock_chat_history_service._get_or_create_conversation.return_value = {
            "id": "test-conversation-id",
            "repository_id": "test-repo",
            "session_id": "test-session",
            "branch": "main",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Patch the endpoint handlers directly
        original_enhanced_chat = app.enhanced_chat_about_repository
        
        async def mock_enhanced_chat(*args, **kwargs):
            # Store original services
            original_rag = app.rag_service
            original_chat_history = app.chat_history_service
            original_kenobi = app.kenobi_agent
            
            # Replace with mocks
            app.rag_service = self.mock_rag_service
            app.chat_history_service = self.mock_chat_history_service
            app.kenobi_agent = self.mock_kenobi_agent
            
            try:
                # Call original function with mocked services
                result = await original_enhanced_chat(*args, **kwargs)
                return result
            finally:
                # Restore original services
                app.rag_service = original_rag
                app.chat_history_service = original_chat_history
                app.kenobi_agent = original_kenobi
        
        # Patch other endpoint handlers similarly
        original_get_history = app.get_enhanced_chat_history
        original_clear_history = app.clear_enhanced_chat_history
        original_create_session = app.create_chat_session
        
        async def mock_get_history(*args, **kwargs):
            app.kenobi_agent = self.mock_kenobi_agent
            app.chat_history_service = self.mock_chat_history_service
            try:
                return await original_get_history(*args, **kwargs)
            finally:
                pass
        
        async def mock_clear_history(*args, **kwargs):
            app.kenobi_agent = self.mock_kenobi_agent
            app.chat_history_service = self.mock_chat_history_service
            try:
                return await original_clear_history(*args, **kwargs)
            finally:
                pass
        
        async def mock_create_session(*args, **kwargs):
            app.kenobi_agent = self.mock_kenobi_agent
            app.chat_history_service = self.mock_chat_history_service
            try:
                return await original_create_session(*args, **kwargs)
            finally:
                pass
        
        # Apply patches
        monkeypatch.setattr(app, "enhanced_chat_about_repository", mock_enhanced_chat)
        monkeypatch.setattr(app, "get_enhanced_chat_history", mock_get_history)
        monkeypatch.setattr(app, "clear_enhanced_chat_history", mock_clear_history)
        monkeypatch.setattr(app, "create_chat_session", mock_create_session)
    
    @pytest.mark.asyncio
    async def test_enhanced_chat_with_rag(self, test_client):
        """Test enhanced chat endpoint with RAG enabled"""
        # Make request
        response = test_client.post(
            "/chat/repository/test-repo",
            json={"message": "Test query", "context": {}, "history": []},
            params={"session_id": "test-session", "use_rag": "true"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["response"] == "This is a test RAG response"
        assert data["context_used"] is True
        assert len(data["sources"]) > 0
        
        # Verify service calls
        self.mock_rag_service.generate_response.assert_called_once()
        self.mock_chat_history_service.save_message.assert_called()
    
    @pytest.mark.asyncio
    async def test_enhanced_chat_without_rag(self, test_client):
        """Test enhanced chat endpoint with RAG disabled"""
        # Make request
        response = test_client.post(
            "/chat/repository/test-repo",
            json={"message": "Test query", "context": {}, "history": []},
            params={"session_id": "test-session", "use_rag": "false"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["response"] == "This is a test response from Kenobi"
        assert data["context_used"] is False
        
        # Verify service calls
        self.mock_rag_service.generate_response.assert_not_called()
        self.mock_kenobi_agent.chat_about_repository.assert_called_once()
        self.mock_chat_history_service.save_message.assert_called()
    
    @pytest.mark.asyncio
    async def test_enhanced_chat_with_fallback(self, test_client):
        """Test enhanced chat endpoint with fallback to Kenobi when RAG fails"""
        # Configure RAG to fail
        self.mock_rag_service.generate_response.side_effect = Exception("RAG service failed")
        
        # Make request
        response = test_client.post(
            "/chat/repository/test-repo",
            json={"message": "Test query", "context": {}, "history": []},
            params={"session_id": "test-session", "use_rag": "true"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert data["response"] == "This is a test response from Kenobi"
        assert data["context_used"] is False
        
        # Verify service calls
        self.mock_rag_service.generate_response.assert_called_once()
        self.mock_kenobi_agent.chat_about_repository.assert_called_once()
        self.mock_chat_history_service.save_message.assert_called()
        
        # Reset side effect for other tests
        self.mock_rag_service.generate_response.side_effect = None
    
    @pytest.mark.asyncio
    async def test_get_chat_history(self, test_client):
        """Test get chat history endpoint"""
        # Make request
        response = test_client.get(
            "/chat/repository/test-repo/history",
            params={"session_id": "test-session"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) == 2
        assert data["repository_id"] == "test-repo"
        assert data["session_id"] == "test-session"
        
        # Verify service calls
        self.mock_chat_history_service.get_conversation_history.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_chat_history(self, test_client):
        """Test clear chat history endpoint"""
        # Make request
        response = test_client.delete(
            "/chat/repository/test-repo/history",
            params={"session_id": "test-session"}
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["repository_id"] == "test-repo"
        assert data["session_id"] == "test-session"
        
        # Verify service calls
        self.mock_chat_history_service.clear_conversation_history.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_chat_session(self, test_client):
        """Test create chat session endpoint"""
        # Make request
        response = test_client.post(
            "/chat/repository/test-repo/session"
        )
        
        # Verify response
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["repository_id"] == "test-repo"
        
        # Verify service calls
        self.mock_chat_history_service._get_or_create_conversation.assert_called_once()


class TestChatHistoryService:
    """Test suite for the chat history service"""
    
    @pytest.fixture(autouse=True)
    def setup_mocks(self):
        """Set up mocks for all tests in this class"""
        # Create mock database service
        self.mock_db_service = AsyncMock()
        self.mock_session = AsyncMock()
        self.mock_db_service.session_factory.return_value = self.mock_session
        
        # Create mock cache service
        self.mock_cache_service = AsyncMock()
        
        # Create chat history service with mocks
        self.chat_service = ChatHistoryService()
        self.chat_service.db_service = self.mock_db_service
        self.chat_service.cache_service = self.mock_cache_service
    
    @pytest.mark.asyncio
    async def test_save_message(self):
        """Test saving a message to the chat history"""
        # Configure mock for _get_or_create_conversation
        self.chat_service._get_or_create_conversation = AsyncMock()
        self.chat_service._get_or_create_conversation.return_value = {
            "id": "test-conversation-id",
            "repository_id": "test-repo",
            "session_id": "test-session",
            "branch": "main",
            "created_at": datetime.utcnow().isoformat()
        }
        
        # Call the method
        result = await self.chat_service.save_message(
            repository_id="test-repo",
            message="Test message",
            is_user=True,
            session_id="test-session",
            branch="main"
        )
        
        # Verify result
        assert result["content"] == "Test message"
        assert result["role"] == "user"
        
        # Verify _get_or_create_conversation was called
        self.chat_service._get_or_create_conversation.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_conversation_history_with_cache_hit(self):
        """Test getting conversation history with cache hit"""
        # Configure mock cache service with hit
        self.mock_cache_service.get.return_value = {
            "messages": [
                {
                    "id": "test-message-1",
                    "content": "Test message 1",
                    "role": "user",
                    "timestamp": datetime.utcnow().isoformat()
                }
            ],
            "repository_id": "test-repo",
            "session_id": "test-session",
            "branch": "main"
        }
        
        # Call the method
        result = await self.chat_service.get_conversation_history(
            repository_id="test-repo",
            session_id="test-session",
            branch="main"
        )
        
        # Verify result
        assert len(result["messages"]) == 1
        assert result["repository_id"] == "test-repo"
        assert result["session_id"] == "test-session"
        
        # Verify cache was checked
        self.mock_cache_service.get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_conversation_history(self):
        """Test clearing conversation history"""
        # Configure mock for _get_conversation
        self.chat_service._get_conversation = AsyncMock()
        self.chat_service._get_conversation.return_value = {
            "id": "test-conversation-id",
            "repository_id": "test-repo",
            "session_id": "test-session",
            "branch": "main",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Call the method
        result = await self.chat_service.clear_conversation_history(
            repository_id="test-repo",
            session_id="test-session",
            branch="main"
        )
        
        # Verify result
        assert result["success"] is True
        assert result["repository_id"] == "test-repo"
        assert result["session_id"] == "test-session"
        
        # Verify _get_conversation was called
        self.chat_service._get_conversation.assert_called_once()