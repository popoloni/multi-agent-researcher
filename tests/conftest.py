"""
Shared pytest configuration and fixtures for the Multi-Agent Research System.

This file contains:
- Shared fixtures for database, API client, and test data
- Test utilities and helper functions
- Common setup and teardown procedures
- Mock configurations for external services
"""

import asyncio
import os
import tempfile
import pytest
import pytest_asyncio
from pathlib import Path
from typing import AsyncGenerator, Generator
from unittest.mock import Mock, patch

# Import FastAPI test client
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import application components
from app.main import app
from app.database.models import Base
from app.core.config import settings
from app.services.database_service import DatabaseService
from app.services.github_service import GitHubService
from app.services.rag_service import RAGService
from app.services.research_service import ResearchService

# Test configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_kenobi.db"
TEST_WORKING_DIR = tempfile.mkdtemp(prefix="obione_test_")


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_settings():
    """Provide test-specific settings."""
    # Create a copy of settings for testing
    test_settings = Settings()
    test_settings.DATABASE_URL = TEST_DATABASE_URL
    return test_settings


@pytest.fixture(scope="session")
async def test_database():
    """Create and configure test database."""
    # Create test database
    db_service = DatabaseService()
    db_service.database_url = TEST_DATABASE_URL
    await db_service.initialize()
    
    # Create all tables
    async with db_service.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield db_service
    
    # Cleanup
    await db_service.close()
    # Remove test database file
    if os.path.exists("./test_kenobi.db"):
        os.remove("./test_kenobi.db")


@pytest.fixture
async def db_session(test_database):
    """Provide a database session for tests."""
    async with test_database.get_session() as session:
        yield session
        await session.rollback()


@pytest.fixture
def test_client():
    """Provide a test client for FastAPI application."""
    with TestClient(app) as client:
        yield client


@pytest.fixture
async def async_client():
    """Provide an async test client for FastAPI application."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def mock_github_service():
    """Provide a mocked GitHub service for testing."""
    with patch('app.services.github_service.GitHubService') as mock:
        service = Mock(spec=GitHubService)
        mock.return_value = service
        yield service


@pytest.fixture
def mock_rag_service():
    """Provide a mocked RAG service for testing."""
    with patch('app.services.rag_service.RAGService') as mock:
        service = Mock(spec=RAGService)
        mock.return_value = service
        yield service


@pytest.fixture
def mock_research_service():
    """Provide a mocked research service for testing."""
    with patch('app.services.research_service.ResearchService') as mock:
        service = Mock(spec=ResearchService)
        mock.return_value = service
        yield service


@pytest.fixture
def sample_repository_data():
    """Provide sample repository data for testing."""
    return {
        "name": "test-repo",
        "full_name": "test-org/test-repo",
        "description": "A test repository for unit testing",
        "html_url": "https://github.com/test-org/test-repo",
        "clone_url": "https://github.com/test-org/test-repo.git",
        "default_branch": "main",
        "language": "Python",
        "stars": 100,
        "forks": 50,
        "size": 1024,
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-12-01T00:00:00Z"
    }


@pytest.fixture
def sample_functionality_data():
    """Provide sample functionality data for testing."""
    return {
        "name": "test_functionality",
        "description": "A test functionality for unit testing",
        "file_path": "test_file.py",
        "line_number": 10,
        "function_type": "function",
        "repository_id": 1
    }


@pytest.fixture
def sample_chat_message_data():
    """Provide sample chat message data for testing."""
    return {
        "role": "user",
        "content": "What is the main functionality of this repository?",
        "timestamp": "2023-12-01T00:00:00Z",
        "repository_id": 1
    }


@pytest.fixture
def temp_working_dir():
    """Provide a temporary working directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def mock_ollama_response():
    """Provide a mocked Ollama response for testing."""
    return {
        "model": "llama2",
        "response": "This is a test response from Ollama.",
        "done": True,
        "context": [1, 2, 3, 4, 5]
    }


@pytest.fixture
def mock_anthropic_response():
    """Provide a mocked Anthropic response for testing."""
    return {
        "id": "msg_test123",
        "type": "message",
        "role": "assistant",
        "content": [
            {
                "type": "text",
                "text": "This is a test response from Anthropic."
            }
        ],
        "model": "claude-3-sonnet-20240229",
        "usage": {
            "input_tokens": 10,
            "output_tokens": 20
        }
    }


# Test utilities
class TestUtils:
    """Utility class for common test operations."""
    
    @staticmethod
    def create_test_file(content: str, filename: str = "test.py") -> Path:
        """Create a temporary test file with given content."""
        temp_file = Path(tempfile.gettempdir()) / filename
        temp_file.write_text(content)
        return temp_file
    
    @staticmethod
    def cleanup_test_files(*files: Path):
        """Clean up test files."""
        for file in files:
            if file.exists():
                file.unlink()
    
    @staticmethod
    def assert_response_structure(response_data: dict, expected_fields: list):
        """Assert that response has expected structure."""
        for field in expected_fields:
            assert field in response_data, f"Missing field: {field}"
    
    @staticmethod
    def assert_error_response(response, status_code: int, error_type: str = None):
        """Assert that response is an error with expected status code."""
        assert response.status_code == status_code
        if error_type:
            assert "error" in response.json()
            assert error_type in response.json()["error"]


# Make TestUtils available as a fixture
@pytest.fixture
def test_utils():
    """Provide test utilities."""
    return TestUtils


# Coverage configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        elif "agents" in str(item.fspath):
            item.add_marker(pytest.mark.agents)
        elif "frontend" in str(item.fspath):
            item.add_marker(pytest.mark.frontend)
        elif "e2e" in str(item.fspath):
            item.add_marker(pytest.mark.e2e) 