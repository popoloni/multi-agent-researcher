"""
Test suite for Task 4.2: Enhanced Chat API with RAG Integration
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.main import app, enhanced_chat_about_repository, get_enhanced_chat_history, clear_enhanced_chat_history, create_chat_session
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
    
    @pytest.mark.asyncio
    async def test_enhanced_chat_with_rag(self, test_client):
        """Test enhanced chat endpoint with RAG enabled"""
        # Create mock services
        mock_rag = AsyncMock()
        mock_chat_history = AsyncMock()
        
        # Configure mock responses
        mock_rag.generate_response.return_value = RAGResponse(
            content="This is a test RAG response",
            sources=[{"source_id": "test-1", "source_type": "code", "file_path": "/test/file.py"}],
            context_used=True,
            query="Test query",
            repository_id="test-repo",
            processing_time=0.1,
            model_used="test-model"
        )
        
        mock_chat_history.save_message.return_value = {
            "id": "test-message-id",
            "content": "Test message",
            "role": "user",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        mock_chat_history.get_context_for_rag.return_value = {
            "history": [],
            "repository_id": "test-repo",
            "branch": "main"
        }
        
        # Import app.main and create the global variables if they don't exist
        import app.main
        if not hasattr(app.main, 'rag_service'):
            app.main.rag_service = mock_rag
        if not hasattr(app.main, 'chat_history_service'):
            app.main.chat_history_service = mock_chat_history
        
        # Mock the global services in the main module
        with patch.object(app.main, 'rag_service', mock_rag), \
             patch.object(app.main, 'chat_history_service', mock_chat_history), \
             patch('app.main.kenobi_agent') as mock_kenobi:
            
            # Configure mock repository service
            mock_repo_service = AsyncMock()
            mock_repo_service.get_repository_metadata.return_value = {
                "id": "test-repo",
                "name": "Test Repository",
                "description": "Test repository for unit tests",
                "url": "https://github.com/test/repo"
            }
            mock_kenobi.repository_service = mock_repo_service
            
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
            mock_rag.generate_response.assert_called_once()
            mock_chat_history.save_message.assert_called()
    
    @pytest.mark.asyncio
    async def test_enhanced_chat_without_rag(self, test_client):
        """Test enhanced chat endpoint with RAG disabled"""
        # Create mock services
        mock_rag = AsyncMock()
        mock_chat_history = AsyncMock()
        
        mock_chat_history.save_message.return_value = {
            "id": "test-message-id",
            "content": "Test message",
            "role": "user",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Configure get_context_for_rag to return a proper dictionary
        mock_chat_history.get_context_for_rag.return_value = {
            "history": [],
            "repository_id": "test-repo",
            "branch": "main"
        }
        
        # Import app.main and create the global variables if they don't exist
        import app.main
        if not hasattr(app.main, 'rag_service'):
            app.main.rag_service = mock_rag
        if not hasattr(app.main, 'chat_history_service'):
            app.main.chat_history_service = mock_chat_history
        
        # Mock the global services in the main module
        with patch.object(app.main, 'rag_service', mock_rag), \
             patch.object(app.main, 'chat_history_service', mock_chat_history), \
             patch('app.main.kenobi_agent') as mock_kenobi:
            
            # Configure mock repository service
            mock_repo_service = AsyncMock()
            mock_repo_service.get_repository_metadata.return_value = {
                "id": "test-repo",
                "name": "Test Repository",
                "description": "Test repository for unit tests",
                "url": "https://github.com/test/repo"
            }
            mock_kenobi.repository_service = mock_repo_service
            
            # Configure mock chat response - make it an AsyncMock
            mock_chat_response = AsyncMock()
            mock_chat_response.return_value = {
                "answer": "This is a test response from Kenobi",
                "sources": [{"source_id": "test-1", "source_type": "code", "file_path": "/test/file.py"}],
                "timestamp": datetime.utcnow().isoformat()
            }
            mock_kenobi.chat_about_repository = mock_chat_response
            
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
            mock_rag.generate_response.assert_not_called()
            mock_kenobi.chat_about_repository.assert_called_once()
            mock_chat_history.save_message.assert_called()
    
    @pytest.mark.asyncio
    async def test_enhanced_chat_with_fallback(self, test_client):
        """Test enhanced chat endpoint with fallback to Kenobi when RAG fails"""
        # Create mock services
        mock_rag = AsyncMock()
        mock_chat_history = AsyncMock()
        
        # Configure RAG to fail
        mock_rag.generate_response.side_effect = Exception("RAG service failed")
        
        mock_chat_history.save_message.return_value = {
            "id": "test-message-id",
            "content": "Test message",
            "role": "user",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Configure get_context_for_rag to return a proper dictionary
        mock_chat_history.get_context_for_rag.return_value = {
            "history": [],
            "repository_id": "test-repo",
            "branch": "main"
        }
        
        # Import app.main and create the global variables if they don't exist
        import app.main
        if not hasattr(app.main, 'rag_service'):
            app.main.rag_service = mock_rag
        if not hasattr(app.main, 'chat_history_service'):
            app.main.chat_history_service = mock_chat_history
        
        # Mock the global services in the main module
        with patch.object(app.main, 'rag_service', mock_rag), \
             patch.object(app.main, 'chat_history_service', mock_chat_history), \
             patch('app.main.kenobi_agent') as mock_kenobi:
            
            # Configure mock repository service
            mock_repo_service = AsyncMock()
            mock_repo_service.get_repository_metadata.return_value = {
                "id": "test-repo",
                "name": "Test Repository",
                "description": "Test repository for unit tests",
                "url": "https://github.com/test/repo"
            }
            mock_kenobi.repository_service = mock_repo_service
            
            # Configure mock chat response - make it an AsyncMock
            mock_chat_response = AsyncMock()
            mock_chat_response.return_value = {
                "answer": "This is a test response from Kenobi",
                "sources": [{"source_id": "test-1", "source_type": "code", "file_path": "/test/file.py"}],
                "timestamp": datetime.utcnow().isoformat()
            }
            mock_kenobi.chat_about_repository = mock_chat_response
            
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
            mock_rag.generate_response.assert_called_once()
            mock_kenobi.chat_about_repository.assert_called_once()
            mock_chat_history.save_message.assert_called()
    
    @pytest.mark.asyncio
    async def test_get_chat_history(self, test_client):
        """Test get chat history endpoint"""
        # Create mock services
        mock_chat_history = AsyncMock()
        
        # Import app.main and create the global variables if they don't exist
        import app.main
        if not hasattr(app.main, 'chat_history_service'):
            app.main.chat_history_service = mock_chat_history
        
        # Mock the global services in the main module
        with patch.object(app.main, 'chat_history_service', mock_chat_history), \
             patch('app.main.kenobi_agent') as mock_kenobi:
            
            # Configure mock repository service
            mock_repo_service = AsyncMock()
            mock_repo_service.get_repository_metadata.return_value = {
                "id": "test-repo",
                "name": "Test Repository",
                "description": "Test repository for unit tests",
                "url": "https://github.com/test/repo"
            }
            mock_kenobi.repository_service = mock_repo_service
            
            mock_chat_history.get_conversation_history.return_value = {
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
            mock_chat_history.get_conversation_history.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_chat_history(self, test_client):
        """Test clear chat history endpoint"""
        # Create mock services
        mock_chat_history = AsyncMock()
        
        # Import app.main and create the global variables if they don't exist
        import app.main
        if not hasattr(app.main, 'chat_history_service'):
            app.main.chat_history_service = mock_chat_history
        
        # Mock the global services in the main module
        with patch.object(app.main, 'chat_history_service', mock_chat_history), \
             patch('app.main.kenobi_agent') as mock_kenobi:
            
            # Configure mock repository service
            mock_repo_service = AsyncMock()
            mock_repo_service.get_repository_metadata.return_value = {
                "id": "test-repo",
                "name": "Test Repository",
                "description": "Test repository for unit tests",
                "url": "https://github.com/test/repo"
            }
            mock_kenobi.repository_service = mock_repo_service
            
            mock_chat_history.clear_conversation_history.return_value = {
                "success": True,
                "repository_id": "test-repo",
                "session_id": "test-session",
                "branch": "main",
                "message": "Chat history cleared successfully"
            }
            
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
            mock_chat_history.clear_conversation_history.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_chat_session(self, test_client):
        """Test create chat session endpoint"""
        # Create mock services
        mock_chat_history = AsyncMock()
        
        # Import app.main and create the global variables if they don't exist
        import app.main
        if not hasattr(app.main, 'chat_history_service'):
            app.main.chat_history_service = mock_chat_history
        
        # Mock the global services in the main module
        with patch.object(app.main, 'chat_history_service', mock_chat_history), \
             patch('app.main.kenobi_agent') as mock_kenobi:
            
            # Configure mock repository service
            mock_repo_service = AsyncMock()
            mock_repo_service.get_repository_metadata.return_value = {
                "id": "test-repo",
                "name": "Test Repository",
                "description": "Test repository for unit tests",
                "url": "https://github.com/test/repo"
            }
            mock_kenobi.repository_service = mock_repo_service
            
            mock_chat_history._get_or_create_conversation.return_value = {
                "id": "test-conversation-id",
                "repository_id": "test-repo",
                "session_id": "test-session",
                "branch": "main",
                "created_at": datetime.utcnow().isoformat()
            }
            
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
            mock_chat_history._get_or_create_conversation.assert_called_once()


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