"""
Test repository health checking and auto-recovery functionality
"""
import pytest
import pytest_asyncio
import asyncio
import os
import tempfile
import shutil
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from app.services.repository_service import RepositoryService
from app.models.repository_schemas import Repository, LanguageType, CloneStatus
from app.services.database_service import DatabaseService


@pytest_asyncio.fixture
async def temp_repo_service():
    """Create a temporary repository service for testing"""
    service = RepositoryService()
    service.db_service = AsyncMock(spec=DatabaseService)
    
    # Mock database operations
    service.db_service.save_repository = AsyncMock(return_value=None)
    service.db_service.get_repository = AsyncMock(return_value=None)
    service.db_service.list_repositories = AsyncMock(return_value=[])
    service.db_service.delete_repository = AsyncMock(return_value=True)
    
    await service.initialize()
    return service


@pytest.fixture
def temp_repository():
    """Create a temporary test repository"""
    temp_dir = tempfile.mkdtemp()
    
    # Create a simple Python file
    test_file = Path(temp_dir) / "test.py"
    test_file.write_text("""
def hello_world():
    '''A simple hello world function'''
    print("Hello, World!")

class TestClass:
    '''A simple test class'''
    def test_method(self):
        return "test"
""")
    
    repository = Repository(
        id="test-repo-health",
        name="test-repository",
        url="https://github.com/test/test-repo.git",
        local_path=temp_dir,
        language=LanguageType.PYTHON,
        framework="Python",
        description="Test repository for health checking",
        clone_status=CloneStatus.COMPLETED,
        file_count=1,
        line_count=10
    )
    
    yield repository, temp_dir
    
    # Cleanup
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)


class TestRepositoryHealthCheck:
    """Test repository health checking functionality"""
    
    @pytest.mark.asyncio
    async def test_healthy_repository(self, temp_repo_service, temp_repository):
        """Test health check on a healthy repository"""
        repository, temp_dir = temp_repository
        temp_repo_service.repositories[repository.id] = repository
        
        health_status = await temp_repo_service.check_repository_health(repository.id)
        
        assert health_status["healthy"] is True
        assert health_status["status"] == "healthy"
        assert health_status["accessible_files"] >= 1
        assert "Repository is healthy" in health_status["message"]
    
    @pytest.mark.asyncio
    async def test_repository_not_found(self, temp_repo_service):
        """Test health check on non-existent repository"""
        health_status = await temp_repo_service.check_repository_health("non-existent-repo")
        
        assert health_status["healthy"] is False
        assert health_status["status"] == "repository_not_found"
        assert "not found in database" in health_status["message"]
    
    @pytest.mark.asyncio
    async def test_missing_local_path(self, temp_repo_service, temp_repository):
        """Test health check when local path is missing"""
        repository, temp_dir = temp_repository
        
        # Remove the directory
        shutil.rmtree(temp_dir)
        
        temp_repo_service.repositories[repository.id] = repository
        
        health_status = await temp_repo_service.check_repository_health(repository.id)
        
        assert health_status["healthy"] is False
        assert health_status["status"] == "local_path_missing"
        assert "does not exist" in health_status["message"]
        assert "entire_repository" in health_status["missing_files"]
        assert "Auto-recovery available" in health_status["recommendations"][1]
    
    @pytest.mark.asyncio
    async def test_empty_directory(self, temp_repo_service, temp_repository):
        """Test health check on empty repository directory"""
        repository, temp_dir = temp_repository
        
        # Empty the directory
        for file in Path(temp_dir).iterdir():
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                shutil.rmtree(file)
        
        temp_repo_service.repositories[repository.id] = repository
        
        health_status = await temp_repo_service.check_repository_health(repository.id)
        
        assert health_status["healthy"] is False
        assert health_status["status"] == "empty_directory"
        assert "directory is empty" in health_status["message"]
        assert "repository_content" in health_status["missing_files"]


class TestRepositoryAutoRecovery:
    """Test repository auto-recovery functionality"""
    
    @pytest.mark.asyncio
    async def test_recovery_not_needed(self, temp_repo_service, temp_repository):
        """Test recovery when repository is healthy"""
        repository, temp_dir = temp_repository
        temp_repo_service.repositories[repository.id] = repository
        
        recovery_result = await temp_repo_service.auto_recover_repository(repository.id)
        
        assert recovery_result["success"] is True
        assert recovery_result["status"] == "recovery_not_needed"
        assert "healthy" in recovery_result["message"]
    
    @pytest.mark.asyncio
    async def test_recovery_no_source_url(self, temp_repo_service):
        """Test recovery when no source URL is available"""
        repository = Repository(
            id="test-no-url",
            name="test-no-url",
            url="",  # No URL
            local_path="/tmp/nonexistent",
            language=LanguageType.PYTHON,
            file_count=0,
            line_count=0
        )
        temp_repo_service.repositories[repository.id] = repository
        
        recovery_result = await temp_repo_service.auto_recover_repository(repository.id)
        
        assert recovery_result["success"] is False
        assert recovery_result["status"] == "no_source_url"
        assert "no source URL available" in recovery_result["message"]
    
    @pytest.mark.asyncio
    async def test_force_recovery(self, temp_repo_service, temp_repository):
        """Test forced recovery even when repository is healthy"""
        repository, temp_dir = temp_repository
        temp_repo_service.repositories[repository.id] = repository
        
        # Mock the clone_repository method to avoid actual cloning
        temp_repo_service.clone_repository = AsyncMock(return_value=repository)
        
        recovery_result = await temp_repo_service.auto_recover_repository(
            repository.id, force=True
        )
        
        # Should attempt recovery even though repository is healthy
        assert "initiated_recovery" in recovery_result["actions_taken"]


class TestAnalysisWithHealthCheck:
    """Test repository analysis with health checking"""
    
    @pytest.mark.asyncio
    async def test_analysis_healthy_repository(self, temp_repo_service, temp_repository):
        """Test analysis on healthy repository"""
        repository, temp_dir = temp_repository
        temp_repo_service.repositories[repository.id] = repository
        
        # Mock the analyze_repository method
        mock_analysis = MagicMock()
        mock_analysis.files = []
        temp_repo_service.analyze_repository = AsyncMock(return_value=mock_analysis)
        
        analysis = await temp_repo_service.analyze_repository_with_health_check(repository.id)
        
        assert analysis is not None
        temp_repo_service.analyze_repository.assert_called_once_with(repository.id)
    
    @pytest.mark.asyncio
    async def test_analysis_unhealthy_repository_auto_recover(self, temp_repo_service, temp_repository):
        """Test analysis on unhealthy repository with auto-recovery"""
        repository, temp_dir = temp_repository
        
        # Remove the directory to make it unhealthy
        shutil.rmtree(temp_dir)
        
        temp_repo_service.repositories[repository.id] = repository
        
        # Mock successful auto-recovery
        temp_repo_service.auto_recover_repository = AsyncMock(return_value={
            "success": True,
            "status": "recovery_successful"
        })
        
        # Mock the analyze_repository method
        mock_analysis = MagicMock()
        mock_analysis.files = []
        temp_repo_service.analyze_repository = AsyncMock(return_value=mock_analysis)
        
        analysis = await temp_repo_service.analyze_repository_with_health_check(repository.id)
        
        assert analysis is not None
        temp_repo_service.auto_recover_repository.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_analysis_unhealthy_no_auto_recover(self, temp_repo_service, temp_repository):
        """Test analysis on unhealthy repository without auto-recovery"""
        repository, temp_dir = temp_repository
        
        # Remove the directory to make it unhealthy
        shutil.rmtree(temp_dir)
        
        temp_repo_service.repositories[repository.id] = repository
        
        with pytest.raises(ValueError) as exc_info:
            await temp_repo_service.analyze_repository_with_health_check(
                repository.id, auto_recover=False
            )
        
        assert "unhealthy" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_analysis_auto_recovery_failed(self, temp_repo_service, temp_repository):
        """Test analysis when auto-recovery fails"""
        repository, temp_dir = temp_repository
        
        # Remove the directory to make it unhealthy
        shutil.rmtree(temp_dir)
        
        temp_repo_service.repositories[repository.id] = repository
        
        # Mock failed auto-recovery
        temp_repo_service.auto_recover_repository = AsyncMock(return_value={
            "success": False,
            "status": "clone_failed",
            "message": "Recovery failed: network error"
        })
        
        with pytest.raises(ValueError) as exc_info:
            await temp_repo_service.analyze_repository_with_health_check(repository.id)
        
        assert "auto-recovery failed" in str(exc_info.value)


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 