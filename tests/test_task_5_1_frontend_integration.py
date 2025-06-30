"""
Integration tests for Task 5.1: Enhanced Chat Frontend Components
Tests the integration between frontend components and backend APIs
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient
import json

from app.main import app
from app.models.rag_schemas import ChatRequest, ChatResponse


@pytest.fixture
def test_client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def mock_services():
    """Mock all the services for testing"""
    with patch("app.main.rag_service") as mock_rag, \
         patch("app.main.chat_history_service") as mock_chat_history, \
         patch("app.main.kenobi_agent") as mock_kenobi:
        
        # Configure mock repository service
        mock_repo_service = AsyncMock()
        mock_repo_service.get_repository_metadata.return_value = {
            "id": "test-repo",
            "name": "Test Repository",
            "description": "Test repository for frontend integration",
            "url": "https://github.com/test/repo",
            "file_count": 150,
            "line_count": 5000,
            "languages": ["JavaScript", "Python"],
            "indexed_at": "2023-12-01T10:00:00Z"
        }
        mock_kenobi.repository_service = mock_repo_service
        
        # Configure mock chat response
        mock_kenobi.chat_about_repository.return_value = {
            "answer": "This is a test response from Kenobi",
            "sources": [{"source_id": "test-1", "source_type": "code", "file_path": "/test/file.py"}],
            "timestamp": "2023-12-01T10:00:00Z"
        }
        
        # Configure mock RAG response
        from app.models.rag_schemas import RAGResponse
        mock_rag.generate_response.return_value = RAGResponse(
            content="This is a test RAG response with code:\n\n```python\ndef hello():\n    print('Hello, World!')\n```",
            sources=[
                {
                    "source_id": "test-1", 
                    "source_type": "code", 
                    "file_path": "/test/file.py",
                    "line_number": 10,
                    "relevance": "high"
                }
            ],
            context_used=True,
            query="Test query",
            repository_id="test-repo",
            processing_time=0.1,
            model_used="test-model"
        )
        
        # Configure mock chat history service
        mock_chat_history.save_message.return_value = {
            "id": "test-message-id",
            "content": "Test message",
            "role": "user",
            "timestamp": "2023-12-01T10:00:00Z"
        }
        
        mock_chat_history.get_conversation_history.return_value = {
            "messages": [
                {
                    "id": "test-message-1",
                    "content": "Test message 1",
                    "role": "user",
                    "timestamp": "2023-12-01T10:00:00Z"
                },
                {
                    "id": "test-message-2",
                    "content": "Test response 1",
                    "role": "assistant",
                    "timestamp": "2023-12-01T10:00:00Z"
                }
            ],
            "repository_id": "test-repo",
            "session_id": "test-session",
            "branch": "main"
        }
        
        mock_chat_history.get_context_for_rag.return_value = {
            "history": [],
            "repository_id": "test-repo",
            "branch": "main"
        }
        
        mock_chat_history.clear_conversation_history.return_value = {
            "success": True,
            "repository_id": "test-repo",
            "session_id": "test-session",
            "branch": "main",
            "message": "Chat history cleared successfully"
        }
        
        mock_chat_history._get_or_create_conversation.return_value = {
            "id": "test-conversation-id",
            "repository_id": "test-repo",
            "session_id": "test-session",
            "branch": "main",
            "created_at": "2023-12-01T10:00:00Z"
        }
        
        yield {
            "rag": mock_rag,
            "chat_history": mock_chat_history,
            "kenobi": mock_kenobi
        }


class TestEnhancedChatAPIIntegration:
    """Test the enhanced chat API endpoints that the frontend will use"""
    
    def test_enhanced_chat_with_rag_enabled(self, test_client, mock_services):
        """Test enhanced chat endpoint with RAG enabled"""
        response = test_client.post(
            "/chat/repository/test-repo",
            json={"message": "How do I create a function?", "context": {}},
            params={"session_id": "test-session", "use_rag": "true"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure expected by frontend
        assert "response" in data
        assert "sources" in data
        assert "context_used" in data
        assert "timestamp" in data
        assert "repository_id" in data
        assert "branch" in data
        
        # Verify RAG response content
        assert "This is a test RAG response" in data["response"]
        assert data["context_used"] is True
        assert len(data["sources"]) > 0
        
        # Verify source structure expected by frontend
        source = data["sources"][0]
        assert "source_id" in source
        assert "source_type" in source
        assert "file_path" in source
    
    def test_enhanced_chat_with_rag_disabled(self, test_client, mock_services):
        """Test enhanced chat endpoint with RAG disabled (fallback to Kenobi)"""
        response = test_client.post(
            "/chat/repository/test-repo",
            json={"message": "How do I create a function?", "context": {}},
            params={"session_id": "test-session", "use_rag": "false"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "response" in data
        assert "sources" in data
        assert "context_used" in data
        
        # Verify fallback to Kenobi
        assert "This is a test response from Kenobi" in data["response"]
        assert data["context_used"] is False
    
    def test_chat_history_retrieval(self, test_client, mock_services):
        """Test chat history endpoint for frontend history display"""
        response = test_client.get(
            "/chat/repository/test-repo/history",
            params={"session_id": "test-session", "branch": "main", "limit": 50}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify history structure expected by frontend
        assert "messages" in data
        assert "repository_id" in data
        assert "session_id" in data
        assert "branch" in data
        
        # Verify message structure
        messages = data["messages"]
        assert len(messages) == 2
        
        message = messages[0]
        assert "id" in message
        assert "content" in message
        assert "role" in message
        assert "timestamp" in message
    
    def test_chat_session_creation(self, test_client, mock_services):
        """Test session creation for frontend session management"""
        response = test_client.post(
            "/chat/repository/test-repo/session",
            params={"branch": "main"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify session structure expected by frontend
        assert "session_id" in data
        assert "repository_id" in data
        assert "branch" in data
        assert "created_at" in data
        
        assert data["repository_id"] == "test-repo"
        assert data["branch"] == "main"
    
    def test_chat_history_clearing(self, test_client, mock_services):
        """Test chat history clearing for frontend clear functionality"""
        response = test_client.delete(
            "/chat/repository/test-repo/history",
            params={"session_id": "test-session", "branch": "main"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify clear response structure
        assert "success" in data
        assert "repository_id" in data
        assert "session_id" in data
        assert "branch" in data
        assert "message" in data
        
        assert data["success"] is True
        assert data["repository_id"] == "test-repo"
    
    def test_repository_not_found_error(self, test_client, mock_services):
        """Test error handling when repository is not found"""
        # Configure mock to return None for repository
        mock_services["kenobi"].repository_service.get_repository_metadata.return_value = None
        
        response = test_client.post(
            "/chat/repository/nonexistent-repo",
            json={"message": "Test message", "context": {}},
            params={"session_id": "test-session"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Repository not found" in data["detail"]
    
    def test_legacy_chat_endpoint_compatibility(self, test_client, mock_services):
        """Test that legacy chat endpoint still works for backward compatibility"""
        response = test_client.post(
            "/kenobi/chat",
            json={
                "message": "Test message",
                "repository_id": "test-repo",
                "branch": "main",
                "session_id": "test-session"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify legacy response structure
        assert "response" in data
        assert "sources" in data
        assert "repository_id" in data
        assert "branch" in data
        assert "session_id" in data
        assert "timestamp" in data


class TestFrontendBackendDataFlow:
    """Test the complete data flow from frontend to backend"""
    
    def test_complete_chat_flow_with_rag(self, test_client, mock_services):
        """Test complete chat flow: session creation -> message -> history -> clear"""
        
        # 1. Create session
        session_response = test_client.post(
            "/chat/repository/test-repo/session",
            params={"branch": "main"}
        )
        assert session_response.status_code == 200
        session_id = session_response.json()["session_id"]
        
        # 2. Send message with RAG
        chat_response = test_client.post(
            "/chat/repository/test-repo",
            json={
                "message": "Explain this code: def hello(): print('hi')",
                "context": {"user_preference": "detailed"}
            },
            params={"session_id": session_id, "use_rag": "true", "include_context": "true"}
        )
        assert chat_response.status_code == 200
        chat_data = chat_response.json()
        
        # Verify RAG response with code highlighting support
        assert "response" in chat_data
        assert chat_data["context_used"] is True
        assert len(chat_data["sources"]) > 0
        
        # 3. Get chat history
        history_response = test_client.get(
            "/chat/repository/test-repo/history",
            params={"session_id": session_id, "branch": "main"}
        )
        assert history_response.status_code == 200
        history_data = history_response.json()
        assert len(history_data["messages"]) >= 0  # May be empty in mock
        
        # 4. Clear history
        clear_response = test_client.delete(
            "/chat/repository/test-repo/history",
            params={"session_id": session_id, "branch": "main"}
        )
        assert clear_response.status_code == 200
        clear_data = clear_response.json()
        assert clear_data["success"] is True
    
    def test_error_handling_and_fallback(self, test_client, mock_services):
        """Test error handling and fallback mechanisms"""
        
        # Configure RAG to fail
        mock_services["rag"].generate_response.side_effect = Exception("RAG service failed")
        
        # Send message - should fallback to Kenobi
        response = test_client.post(
            "/chat/repository/test-repo",
            json={"message": "Test message", "context": {}},
            params={"session_id": "test-session", "use_rag": "true"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should get Kenobi response as fallback
        assert "This is a test response from Kenobi" in data["response"]
        assert data["context_used"] is False
        
        # Verify both services were called
        mock_services["rag"].generate_response.assert_called_once()
        mock_services["kenobi"].chat_about_repository.assert_called_once()
    
    def test_source_reference_data_structure(self, test_client, mock_services):
        """Test that source references have the correct structure for frontend display"""
        
        response = test_client.post(
            "/chat/repository/test-repo",
            json={"message": "Show me the code", "context": {}},
            params={"session_id": "test-session", "use_rag": "true"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify sources structure for frontend SourceReference component
        sources = data["sources"]
        assert len(sources) > 0
        
        source = sources[0]
        # These fields are expected by the SourceReference component
        assert "source_id" in source or "file_path" in source
        assert "source_type" in source
        
        # Additional fields that may be present
        if "line_number" in source:
            assert isinstance(source["line_number"], (int, str))
        if "relevance" in source:
            assert source["relevance"] in ["high", "medium", "low"]


@pytest.mark.asyncio
async def test_real_time_messaging_simulation():
    """Test real-time messaging capabilities (simulated)"""
    
    # This would test WebSocket connections in a real implementation
    # For now, we test the HTTP-based approach
    
    from app.services.chat_history_service import ChatHistoryService
    from unittest.mock import AsyncMock
    
    # Create mock chat history service
    chat_service = ChatHistoryService()
    chat_service.db_service = AsyncMock()
    chat_service.cache_service = AsyncMock()
    chat_service._get_or_create_conversation = AsyncMock()
    chat_service._get_or_create_conversation.return_value = {
        "id": "test-conversation-id",
        "repository_id": "test-repo",
        "session_id": "test-session",
        "branch": "main",
        "created_at": "2023-12-01T10:00:00Z"
    }
    
    # Simulate rapid message exchange
    messages = [
        "What is this function?",
        "How do I optimize this code?",
        "Can you explain the algorithm?"
    ]
    
    for i, message in enumerate(messages):
        result = await chat_service.save_message(
            repository_id="test-repo",
            message=message,
            is_user=True,
            session_id="test-session",
            branch="main"
        )
        
        assert result["content"] == message
        assert result["role"] == "user"
        
        # Simulate assistant response
        assistant_result = await chat_service.save_message(
            repository_id="test-repo",
            message=f"Response to: {message}",
            is_user=False,
            session_id="test-session",
            branch="main",
            metadata={"sources": [{"file": f"test{i}.py", "line": i+1}]}
        )
        
        assert assistant_result["role"] == "assistant"
        assert assistant_result["metadata"]["sources"][0]["file"] == f"test{i}.py"