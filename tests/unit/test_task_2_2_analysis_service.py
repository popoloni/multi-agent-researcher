"""
Test Suite for Task 2.2: Analysis Service Implementation
Tests analysis results persistence with database integration and code snippet extraction
"""

import asyncio
import pytest
import tempfile
import os
import logging
from datetime import datetime

# Enable info logging for tests
logging.basicConfig(level=logging.INFO)
from typing import Dict, Any

# Set up test environment
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///test_analysis_service.db"

from app.services.analysis_service import AnalysisService, CodeSnippet, AnalysisResultData
from app.services.database_service import DatabaseService
from app.models.repository_schemas import (
    Repository, RepositoryAnalysis, ParsedFile, CodeElement, DependencyGraph, ImportInfo
)
from app.database.models import Base


class TestAnalysisService:
    """Test suite for Analysis Service functionality"""
    
    @classmethod
    def setup_class(cls):
        """Set up test environment"""
        print("🧪 Starting Analysis Service Tests (Task 2.2)")
        print("=" * 60)
        print("🔧 Setting up test environment...")
        
        # Initialize services
        cls.analysis_service = AnalysisService()
        cls.db_service = DatabaseService()
        
        # Create test database
        asyncio.run(cls._setup_database())
        print("✅ Test environment setup complete")
    
    @classmethod
    async def _setup_database(cls):
        """Create test database tables"""
        await cls.db_service.initialize()
    
    @classmethod
    def teardown_class(cls):
        """Clean up test environment"""
        print("🧹 Cleaning up test environment...")
        
        # Remove test database
        try:
            if os.path.exists("test_analysis_service.db"):
                os.remove("test_analysis_service.db")
        except Exception as e:
            print(f"Warning: Could not remove test database: {e}")
        
        print("✅ Test environment cleanup complete")
    
    def test_basic_analysis_save(self):
        """Test basic analysis save functionality"""
        print("🧪 Testing basic analysis save")
        
        async def run_test():
            # Create test analysis data
            test_analysis = self._create_test_analysis()
            
            # Save analysis
            result = await self.analysis_service.save_analysis_results(
                "test-repo-1", test_analysis
            )
            
            # Verify result
            assert isinstance(result, AnalysisResultData)
            assert result.analysis_result.repository_id == "test-repo-1"
            assert result.analysis_result.metrics == test_analysis.metrics
            assert len(result.code_snippets) > 0
            assert not result.cached  # First save should not be cached
            
            print(f"✅ Analysis saved with {len(result.code_snippets)} code snippets")
        
        asyncio.run(run_test())
        print("✅ Basic analysis save test passed")
    
    def test_cache_first_retrieval(self):
        """Test cache-first retrieval strategy"""
        print("🧪 Testing cache-first retrieval strategy")
        
        async def run_test():
            # Save analysis first
            test_analysis = self._create_test_analysis()
            await self.analysis_service.save_analysis_results(
                "test-repo-cache", test_analysis
            )
            
            # Clear cache to test database retrieval
            cache_key = f"analysis:test-repo-cache_main"
            await self.analysis_service.cache_service.delete(cache_key)
            
            # First retrieval (should be from database, then cached)
            result1 = await self.analysis_service.get_analysis_results("test-repo-cache")
            assert result1 is not None
            assert not result1.cached  # First retrieval from database
            
            # Second retrieval (should be from cache)
            result2 = await self.analysis_service.get_analysis_results("test-repo-cache")
            assert result2 is not None
            assert result2.cached  # Second retrieval from cache
            
            # Verify data consistency
            assert result1.analysis_result.repository_id == result2.analysis_result.repository_id
            assert len(result1.code_snippets) == len(result2.code_snippets)
            
            print("✅ Cache-first strategy working correctly")
        
        asyncio.run(run_test())
        print("✅ Cache-first retrieval test passed")
    
    def test_code_snippet_extraction(self):
        """Test code snippet extraction for RAG context"""
        print("🧪 Testing code snippet extraction for RAG context")
        
        async def run_test():
            # Create analysis with rich code content
            test_analysis = self._create_rich_analysis()
            
            # Save analysis
            result = await self.analysis_service.save_analysis_results(
                "test-repo-snippets", test_analysis
            )
            
            # Verify code snippets
            snippets = result.code_snippets
            assert len(snippets) > 0
            
            # Check snippet types
            snippet_types = {snippet.snippet_type for snippet in snippets}
            expected_types = {"function", "class", "import"}
            assert snippet_types.intersection(expected_types), f"Expected snippet types, got {snippet_types}"
            
            # Check snippet content
            function_snippets = [s for s in snippets if s.snippet_type == "function"]
            assert len(function_snippets) > 0
            
            # Verify snippet metadata
            for snippet in function_snippets:
                assert snippet.file_path
                assert snippet.language
                assert snippet.start_line > 0
                assert snippet.content
                assert isinstance(snippet.metadata, dict)
            
            print(f"✅ Extracted {len(snippets)} snippets with types: {snippet_types}")
        
        asyncio.run(run_test())
        print("✅ Code snippet extraction test passed")
    
    def test_analysis_listing(self):
        """Test analysis listing functionality"""
        print("🧪 Testing analysis listing")
        
        async def run_test():
            # Save multiple analyses
            for i in range(3):
                test_analysis = self._create_test_analysis()
                await self.analysis_service.save_analysis_results(
                    f"test-repo-list-{i}", test_analysis
                )
            
            # List analyses
            analyses = await self.analysis_service.list_analysis_results()
            
            # Verify listing
            assert len(analyses) >= 3
            
            # Check analysis structure
            for analysis in analyses:
                assert "id" in analysis
                assert "repository_id" in analysis
                assert "generated_at" in analysis
                assert "frameworks_detected" in analysis
                assert "categories_used" in analysis
                assert "snippet_count" in analysis
            
            print(f"✅ Listed {len(analyses)} analysis results")
        
        asyncio.run(run_test())
        print("✅ Analysis listing test passed")
    
    def test_analysis_deletion(self):
        """Test analysis deletion"""
        print("🧪 Testing analysis deletion")
        
        async def run_test():
            # Save analysis
            test_analysis = self._create_test_analysis()
            await self.analysis_service.save_analysis_results(
                "test-repo-delete", test_analysis
            )
            
            # Verify it exists
            result = await self.analysis_service.get_analysis_results("test-repo-delete")
            assert result is not None
            
            # Delete analysis
            deleted = await self.analysis_service.delete_analysis_results("test-repo-delete")
            assert deleted
            
            # Verify it's gone
            result = await self.analysis_service.get_analysis_results("test-repo-delete")
            assert result is None
            
            print("✅ Analysis deletion working correctly")
        
        asyncio.run(run_test())
        print("✅ Analysis deletion test passed")
    
    def test_code_snippet_search(self):
        """Test code snippet search functionality"""
        print("🧪 Testing code snippet search")
        
        async def run_test():
            # Save analysis with searchable content
            test_analysis = self._create_rich_analysis()
            await self.analysis_service.save_analysis_results(
                "test-repo-search", test_analysis
            )
            
            # Search for function snippets
            function_snippets = await self.analysis_service.search_code_snippets(
                "calculate", snippet_type="function"
            )
            assert len(function_snippets) > 0
            
            # Search by file path
            file_snippets = await self.analysis_service.search_code_snippets(
                "main.py"
            )
            assert len(file_snippets) > 0
            
            # Search with repository filter
            repo_snippets = await self.analysis_service.search_code_snippets(
                "def", repository_id="test-repo-search"
            )
            assert len(repo_snippets) > 0
            
            print(f"✅ Search found {len(function_snippets)} function snippets")
        
        asyncio.run(run_test())
        print("✅ Code snippet search test passed")
    
    def test_analysis_stats(self):
        """Test analysis statistics"""
        print("🧪 Testing analysis statistics")
        
        async def run_test():
            # Get stats
            stats = await self.analysis_service.get_analysis_stats()
            
            # Verify stats structure
            assert "total_analysis_results" in stats
            assert "vector_indexed_results" in stats
            assert "vector_indexing_percentage" in stats
            assert "average_snippets_per_analysis" in stats
            assert "cache_stats" in stats
            assert "analysis_cache_entries" in stats
            
            # Verify numeric values
            assert isinstance(stats["total_analysis_results"], int)
            assert isinstance(stats["vector_indexing_percentage"], (int, float))
            assert stats["total_analysis_results"] >= 0
            
            print(f"✅ Stats: {stats['total_analysis_results']} analyses, "
                  f"{stats['vector_indexing_percentage']:.1f}% vector indexed")
        
        asyncio.run(run_test())
        print("✅ Analysis statistics test passed")
    
    def test_error_handling(self):
        """Test error handling and edge cases"""
        print("🧪 Testing error handling")
        
        async def run_test():
            # Test retrieval of non-existent analysis
            result = await self.analysis_service.get_analysis_results("non-existent-repo")
            assert result is None
            
            # Test deletion of non-existent analysis
            deleted = await self.analysis_service.delete_analysis_results("non-existent-repo")
            assert deleted  # Should return True even if nothing to delete
            
            # Test search with no results
            snippets = await self.analysis_service.search_code_snippets("non-existent-code")
            assert len(snippets) == 0
            
            print("✅ Error handling working correctly")
        
        asyncio.run(run_test())
        print("✅ Error handling test passed")
    
    def _create_test_analysis(self) -> RepositoryAnalysis:
        """Create a test RepositoryAnalysis object"""
        repository = Repository(
            id="test-repo",
            name="Test Repository",
            url="https://github.com/test/repo",
            local_path="/tmp/test-repo",
            language="python",
            description="Test repository for analysis"
        )
        
        # Create test code element
        code_element = CodeElement(
            id="test-repo-test_function",
            repository_id="test-repo",
            file_path="test.py",
            element_type="function",
            name="test_function",
            full_name="test_function",
            code_snippet="def test_function():\n    return 'Hello World'",
            start_line=1,
            end_line=2,
            description="Test function"
        )
        
        # Create test file
        parsed_file = ParsedFile(
            file_path="test.py",
            language="python",
            elements=[code_element],
            imports=[],
            line_count=2,
            size_bytes=42,
            parse_errors=[]
        )
        
        # Create dependency graph
        dependency_graph = DependencyGraph(
            repository_id="test-repo",
            nodes=[],
            edges=[],
            circular_dependencies=[]
        )
        
        return RepositoryAnalysis(
            repository=repository,
            files=[parsed_file],
            dependency_graph=dependency_graph,
            metrics={
                "total_files": 1,
                "total_lines": 2,
                "complexity_score": 1,
                "test_coverage": 0.8
            },
            categories_used=["backend", "api"],
            frameworks_detected=["fastapi", "pytest"]
        )
    
    def _create_rich_analysis(self) -> RepositoryAnalysis:
        """Create a rich RepositoryAnalysis with multiple code elements"""
        repository = Repository(
            id="rich-test-repo",
            name="Rich Test Repository",
            url="https://github.com/test/rich-repo",
            local_path="/tmp/rich-test-repo",
            language="python",
            description="Rich test repository with multiple code elements"
        )
        
        # Create multiple code elements
        function_element = CodeElement(
            id="rich-test-repo-calculate_sum",
            repository_id="rich-test-repo",
            file_path="calculator.py",
            name="calculate_sum",
            full_name="calculate_sum",
            element_type="function",
            code_snippet="def calculate_sum(a, b):\n    \"\"\"Calculate sum of two numbers\"\"\"\n    return a + b",
            start_line=5,
            end_line=7,
            complexity_score=1,
            dependencies=[],
            description="Calculate sum of two numbers"
        )
        
        class_element = CodeElement(
            id="rich-test-repo-Calculator",
            repository_id="rich-test-repo",
            file_path="calculator.py",
            name="Calculator",
            full_name="Calculator",
            element_type="class",
            code_snippet="class Calculator:\n    def __init__(self):\n        self.result = 0",
            start_line=10,
            end_line=12,
            complexity_score=2,
            dependencies=[],
            description="Calculator class"
        )
        
        # Create test file with imports
        file_content = """import os
import sys
from typing import Dict, List

def calculate_sum(a, b):
    \"\"\"Calculate sum of two numbers\"\"\"
    return a + b

class Calculator:
    def __init__(self):
        self.result = 0
"""
        
        # Create ImportInfo objects
        imports = [
            ImportInfo(module="os", is_local=False, import_type="import"),
            ImportInfo(module="sys", is_local=False, import_type="import"),
            ImportInfo(module="typing", is_local=False, import_type="from")
        ]
        
        parsed_file = ParsedFile(
            file_path="main.py",
            language="python",
            elements=[function_element, class_element],
            imports=imports,
            line_count=15,
            size_bytes=len(file_content),
            parse_errors=[]
        )
        
        dependency_graph = DependencyGraph(
            repository_id="rich-test-repo",
            nodes=["main.py"],
            edges=[],
            circular_dependencies=[]
        )
        
        return RepositoryAnalysis(
            repository=repository,
            files=[parsed_file],
            dependency_graph=dependency_graph,
            metrics={
                "total_files": 1,
                "total_lines": 12,
                "complexity_score": 3,
                "test_coverage": 0.9,
                "function_count": 1,
                "class_count": 1
            },
            categories_used=["backend", "api", "utils"],
            frameworks_detected=["fastapi", "pytest", "typing"]
        )


def main():
    """Run all tests"""
    test_suite = TestAnalysisService()
    
    # Set up test environment
    test_suite.setup_class()
    
    try:
        # Run all tests
        test_suite.test_basic_analysis_save()
        test_suite.test_cache_first_retrieval()
        test_suite.test_code_snippet_extraction()
        test_suite.test_analysis_listing()
        test_suite.test_analysis_deletion()
        test_suite.test_code_snippet_search()
        test_suite.test_analysis_stats()
        test_suite.test_error_handling()
        
        print("=" * 60)
        print("🎉 All Analysis Service Tests Passed!")
        print("✅ Analysis save with database persistence")
        print("✅ Cache-first retrieval strategy")
        print("✅ Code snippet extraction for RAG context")
        print("✅ Analysis listing and management")
        print("✅ Analysis deletion")
        print("✅ Code snippet search functionality")
        print("✅ Analysis statistics and monitoring")
        print("✅ Error handling and edge cases")
        
    finally:
        # Clean up test environment
        test_suite.teardown_class()


if __name__ == "__main__":
    main()