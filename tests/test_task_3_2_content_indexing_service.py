"""
Test Suite for Task 3.2: Content Indexing Service
Tests content extraction, indexing pipeline, and RAG content preparation.
"""

import pytest
import pytest_asyncio
import asyncio
import tempfile
import os
import shutil
from datetime import datetime
from typing import List

from app.services.content_indexing_service import (
    ContentIndexingService,
    ContentType,
    ContentChunk,
    ExtractionResult,
    IndexingProgress
)
from app.services.database_service import DatabaseService
from app.models.repository_schemas import Repository


class TestContentIndexingService:
    """Test suite for ContentIndexingService"""
    
    @pytest_asyncio.fixture
    async def content_service(self):
        """Create a test content indexing service"""
        service = ContentIndexingService()
        
        # Initialize database
        await service.db_service.initialize_database()
        
        yield service
        
        # Cleanup
        await service.db_service.close()
    
    @pytest.fixture
    def temp_repository(self):
        """Create a temporary repository with sample files"""
        temp_dir = tempfile.mkdtemp()
        
        # Create sample Python file
        python_file = os.path.join(temp_dir, "sample.py")
        with open(python_file, 'w') as f:
            f.write('''
"""
Sample Python module for testing
"""

def fibonacci(n):
    """Calculate fibonacci number recursively"""
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    """A simple calculator class"""
    
    def __init__(self):
        self.history = []
    
    def add(self, a, b):
        """Add two numbers"""
        result = a + b
        self.history.append(f"{a} + {b} = {result}")
        return result
    
    def multiply(self, a, b):
        """Multiply two numbers"""
        result = a * b
        self.history.append(f"{a} * {b} = {result}")
        return result
''')
        
        # Create sample markdown file
        md_file = os.path.join(temp_dir, "README.md")
        with open(md_file, 'w') as f:
            f.write('''
# Sample Project

This is a sample project for testing content indexing.

## Features

- Fibonacci calculation
- Basic calculator operations
- History tracking

## Usage

```python
calc = Calculator()
result = calc.add(2, 3)
```

## Installation

1. Clone the repository
2. Install dependencies
3. Run the application
''')
        
        # Create sample configuration file
        config_file = os.path.join(temp_dir, "config.json")
        with open(config_file, 'w') as f:
            f.write('''
{
    "app_name": "Sample App",
    "version": "1.0.0",
    "debug": true,
    "database": {
        "host": "localhost",
        "port": 5432,
        "name": "sample_db"
    }
}
''')
        
        # Create sample JavaScript file
        js_file = os.path.join(temp_dir, "script.js")
        with open(js_file, 'w') as f:
            f.write('''
// Sample JavaScript file
function greet(name) {
    // Return greeting message
    return `Hello, ${name}!`;
}

class User {
    constructor(name, email) {
        this.name = name;
        this.email = email;
    }
    
    getInfo() {
        return `${this.name} (${this.email})`;
    }
}
''')
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def sample_repository(self, temp_repository):
        """Create a sample repository object"""
        return Repository(
            id="test-repo-123",
            name="sample-project",
            url="https://github.com/test/sample-project",
            local_path=temp_repository
        )
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, content_service):
        """Test that the content indexing service initializes correctly"""
        assert content_service is not None
        assert content_service.vector_db_service is not None
        assert content_service.documentation_service is not None
        assert content_service.analysis_service is not None
        assert content_service.db_service is not None
        
        # Check configuration
        assert content_service.max_chunk_size > 0
        assert content_service.overlap_size > 0
        assert content_service.min_chunk_size > 0
    
    @pytest.mark.asyncio
    async def test_extract_python_file_content(self, content_service, temp_repository):
        """Test extracting content from Python files"""
        python_file = os.path.join(temp_repository, "sample.py")
        
        result = await content_service.extract_file_content(python_file)
        
        assert isinstance(result, ExtractionResult)
        assert result.success is True
        assert result.file_path == python_file
        assert len(result.chunks) > 0
        assert result.extraction_time > 0
        
        # Check that we have different types of content
        content_types = {chunk.content_type for chunk in result.chunks}
        assert ContentType.SOURCE_CODE in content_types
        
        # Check for specific code elements
        chunk_contents = [chunk.content for chunk in result.chunks]
        assert any("fibonacci" in content for content in chunk_contents)
        assert any("Calculator" in content for content in chunk_contents)
    
    @pytest.mark.asyncio
    async def test_extract_markdown_content(self, content_service, temp_repository):
        """Test extracting content from markdown files"""
        md_file = os.path.join(temp_repository, "README.md")
        
        result = await content_service.extract_file_content(
            md_file, 
            content_types=[ContentType.DOCUMENTATION]
        )
        
        assert result.success is True
        assert len(result.chunks) > 0
        
        # Check content type
        for chunk in result.chunks:
            assert chunk.content_type == ContentType.DOCUMENTATION
        
        # Check that sections are properly extracted
        chunk_contents = [chunk.content for chunk in result.chunks]
        assert any("Sample Project" in content for content in chunk_contents)
        assert any("Features" in content for content in chunk_contents)
    
    @pytest.mark.asyncio
    async def test_extract_configuration_content(self, content_service, temp_repository):
        """Test extracting content from configuration files"""
        config_file = os.path.join(temp_repository, "config.json")
        
        result = await content_service.extract_file_content(
            config_file,
            content_types=[ContentType.CONFIGURATION]
        )
        
        assert result.success is True
        assert len(result.chunks) > 0
        
        # Check content type
        for chunk in result.chunks:
            assert chunk.content_type == ContentType.CONFIGURATION
        
        # Check content
        chunk_contents = [chunk.content for chunk in result.chunks]
        assert any("app_name" in content for content in chunk_contents)
    
    @pytest.mark.asyncio
    async def test_extract_javascript_content(self, content_service, temp_repository):
        """Test extracting content from JavaScript files"""
        js_file = os.path.join(temp_repository, "script.js")
        
        result = await content_service.extract_file_content(js_file)
        
        assert result.success is True
        assert len(result.chunks) > 0
        
        # Check for code content
        chunk_contents = [chunk.content for chunk in result.chunks]
        assert any("greet" in content for content in chunk_contents)
        assert any("User" in content for content in chunk_contents)
    
    @pytest.mark.asyncio
    async def test_extract_nonexistent_file(self, content_service):
        """Test handling of nonexistent files"""
        result = await content_service.extract_file_content("/nonexistent/file.py")
        
        assert result.success is False
        assert result.error_message is not None
        assert len(result.chunks) == 0
    
    @pytest.mark.asyncio
    async def test_content_chunking(self, content_service):
        """Test content chunking with overlap"""
        # Create a large content string
        large_content = "This is a test sentence. " * 100  # ~2500 characters
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(large_content)
            temp_file = f.name
        
        try:
            result = await content_service.extract_file_content(temp_file)
            
            assert result.success is True
            assert len(result.chunks) > 1  # Should be split into multiple chunks
            
            # Check chunk sizes
            for chunk in result.chunks:
                assert len(chunk.content) <= content_service.max_chunk_size
                assert len(chunk.content) >= content_service.min_chunk_size
            
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_repository_content_indexing(self, content_service, sample_repository):
        """Test full repository content indexing"""
        # Mock the repository in database
        async with content_service.db_service.session_factory() as session:
            from sqlalchemy import text
            await session.execute(
                text("INSERT INTO repositories (id, name, url, local_path) VALUES (?, ?, ?, ?)"),
                (sample_repository.id, sample_repository.name, sample_repository.url, sample_repository.local_path)
            )
            await session.commit()
        
        # Index repository content
        progress = await content_service.index_repository_content(sample_repository.id)
        
        assert isinstance(progress, IndexingProgress)
        assert progress.repository_id == sample_repository.id
        assert progress.total_files > 0
        assert progress.processed_files == progress.total_files
        assert progress.indexed_chunks > 0
        assert progress.progress_percentage == 100.0
    
    @pytest.mark.asyncio
    async def test_content_search(self, content_service, sample_repository):
        """Test searching indexed content"""
        # First index the repository
        async with content_service.db_service.session_factory() as session:
            from sqlalchemy import text
            await session.execute(
                text("INSERT INTO repositories (id, name, url, local_path) VALUES (?, ?, ?, ?)"),
                (sample_repository.id, sample_repository.name, sample_repository.url, sample_repository.local_path)
            )
            await session.commit()
        
        await content_service.index_repository_content(sample_repository.id)
        
        # Search for content
        results = await content_service.search_content(
            query="fibonacci calculation function",
            repository_id=sample_repository.id,
            limit=5
        )
        
        assert isinstance(results, list)
        # Note: Results might be empty due to vector search limitations in test environment
        # but the search should not fail
    
    @pytest.mark.asyncio
    async def test_repository_content_stats(self, content_service, sample_repository):
        """Test getting repository content statistics"""
        # First index the repository
        async with content_service.db_service.session_factory() as session:
            from sqlalchemy import text
            await session.execute(
                text("INSERT INTO repositories (id, name, url, local_path) VALUES (?, ?, ?, ?)"),
                (sample_repository.id, sample_repository.name, sample_repository.url, sample_repository.local_path)
            )
            await session.commit()
        
        await content_service.index_repository_content(sample_repository.id)
        
        # Get content stats
        stats = await content_service.get_repository_content_stats(sample_repository.id)
        
        assert isinstance(stats, dict)
        assert "repository_id" in stats
        assert "total_documents" in stats
        assert "total_files" in stats
        assert "content_types" in stats
        assert stats["repository_id"] == sample_repository.id
    
    @pytest.mark.asyncio
    async def test_indexing_progress_tracking(self, content_service, sample_repository):
        """Test indexing progress tracking"""
        # Mock the repository in database
        async with content_service.db_service.session_factory() as session:
            from sqlalchemy import text
            await session.execute(
                text("INSERT INTO repositories (id, name, url, local_path) VALUES (?, ?, ?, ?)"),
                (sample_repository.id, sample_repository.name, sample_repository.url, sample_repository.local_path)
            )
            await session.commit()
        
        # Start indexing (this will run in background)
        indexing_task = asyncio.create_task(
            content_service.index_repository_content(sample_repository.id)
        )
        
        # Check progress while indexing
        await asyncio.sleep(0.1)  # Give it a moment to start
        
        progress = await content_service.get_indexing_progress(sample_repository.id)
        if progress:  # Progress might be None if indexing completed very quickly
            assert isinstance(progress, IndexingProgress)
            assert progress.repository_id == sample_repository.id
        
        # Wait for completion
        final_progress = await indexing_task
        assert final_progress.progress_percentage == 100.0
    
    @pytest.mark.asyncio
    async def test_content_type_filtering(self, content_service, temp_repository):
        """Test filtering content by type during extraction"""
        python_file = os.path.join(temp_repository, "sample.py")
        
        # Extract only source code
        result = await content_service.extract_file_content(
            python_file,
            content_types=[ContentType.SOURCE_CODE]
        )
        
        assert result.success is True
        for chunk in result.chunks:
            assert chunk.content_type == ContentType.SOURCE_CODE
    
    @pytest.mark.asyncio
    async def test_chunk_metadata(self, content_service, temp_repository):
        """Test that chunks contain proper metadata"""
        python_file = os.path.join(temp_repository, "sample.py")
        
        result = await content_service.extract_file_content(python_file)
        
        assert result.success is True
        assert len(result.chunks) > 0
        
        for chunk in result.chunks:
            assert isinstance(chunk, ContentChunk)
            assert chunk.id is not None
            assert chunk.content is not None
            assert chunk.content_type is not None
            assert chunk.file_path == python_file
            assert isinstance(chunk.metadata, dict)
    
    @pytest.mark.asyncio
    async def test_error_handling_invalid_repository(self, content_service):
        """Test error handling for invalid repository"""
        with pytest.raises(ValueError):
            await content_service.index_repository_content("nonexistent-repo")
    
    @pytest.mark.asyncio
    async def test_incremental_indexing_flag(self, content_service, sample_repository):
        """Test incremental indexing flag (basic test)"""
        # Mock the repository in database
        async with content_service.db_service.session_factory() as session:
            from sqlalchemy import text
            await session.execute(
                text("INSERT INTO repositories (id, name, url, local_path) VALUES (?, ?, ?, ?)"),
                (sample_repository.id, sample_repository.name, sample_repository.url, sample_repository.local_path)
            )
            await session.commit()
        
        # Test incremental indexing (should work without errors)
        progress = await content_service.index_repository_content(
            sample_repository.id,
            incremental=True
        )
        
        assert isinstance(progress, IndexingProgress)
        assert progress.repository_id == sample_repository.id
    
    @pytest.mark.asyncio
    async def test_large_file_handling(self, content_service):
        """Test handling of large files"""
        # Create a large file
        large_content = "# Large file content\n" + "This is line content. " * 1000
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(large_content)
            temp_file = f.name
        
        try:
            result = await content_service.extract_file_content(temp_file)
            
            assert result.success is True
            assert len(result.chunks) > 1  # Should be chunked
            
            # Verify no chunk exceeds max size
            for chunk in result.chunks:
                assert len(chunk.content) <= content_service.max_chunk_size
                
        finally:
            os.unlink(temp_file)
    
    @pytest.mark.asyncio
    async def test_concurrent_file_processing(self, content_service, temp_repository):
        """Test concurrent processing of multiple files"""
        files = [
            os.path.join(temp_repository, "sample.py"),
            os.path.join(temp_repository, "README.md"),
            os.path.join(temp_repository, "config.json"),
            os.path.join(temp_repository, "script.js")
        ]
        
        # Process files concurrently
        tasks = [content_service.extract_file_content(file_path) for file_path in files]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(result.success for result in results)
        assert len(results) == len(files)
        
        # Each should have extracted content
        assert all(len(result.chunks) > 0 for result in results)


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])