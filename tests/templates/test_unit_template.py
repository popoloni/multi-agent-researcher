"""
Unit test template for individual functions and classes.

This template provides a standard structure for unit tests that:
- Test individual functions/classes in isolation
- Use mocks for external dependencies
- Follow consistent naming and organization patterns
- Include proper setup, execution, and assertion patterns

Usage:
1. Copy this template to tests/unit/test_<module>_<functionality>.py
2. Replace placeholder content with actual test logic
3. Follow the naming conventions and patterns established here

NOTE: This is a TEMPLATE file and should not be run as actual tests.
All tests in this file are skipped as they are examples only.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Any, Dict, List

# Import the module/class/function being tested
# from app.services.example_service import ExampleService
# from app.utils.example_utils import example_function


@pytest.mark.skip(reason="Template test - not meant to test actual application code")
class TestExampleService:
    """Test suite for ExampleService class."""
    
    @pytest.fixture
    def example_service(self):
        """Create an instance of ExampleService for testing."""
        # return ExampleService()
        pass
    
    @pytest.fixture
    def mock_dependency(self):
        """Mock external dependency."""
        with patch('app.services.example_service.ExternalService') as mock:
            yield mock
    
    def test_example_method_success(self, example_service, mock_dependency):
        """Test successful execution of example method."""
        # Arrange
        input_data = {"key": "value"}
        expected_result = {"result": "success"}
        mock_dependency.return_value.process.return_value = expected_result
        
        # Act
        result = example_service.example_method(input_data)
        
        # Assert
        assert result == expected_result
        mock_dependency.return_value.process.assert_called_once_with(input_data)
    
    def test_example_method_with_invalid_input(self, example_service):
        """Test method behavior with invalid input."""
        # Arrange
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Input cannot be None"):
            example_service.example_method(invalid_input)
    
    @pytest.mark.parametrize("input_value,expected_output", [
        ("test1", "processed_test1"),
        ("test2", "processed_test2"),
        ("", "processed_empty"),
    ])
    def test_example_method_with_different_inputs(self, example_service, input_value, expected_output):
        """Test method with various input values."""
        # Arrange
        # Setup any necessary mocks
        
        # Act
        result = example_service.example_method(input_value)
        
        # Assert
        assert result == expected_output


@pytest.mark.skip(reason="Template test - not meant to test actual application code")
class TestExampleFunction:
    """Test suite for example_function."""
    
    def test_example_function_basic(self):
        """Test basic functionality of example_function."""
        # Arrange
        input_data = "test_input"
        expected_output = "test_output"
        
        # Act
        result = example_function(input_data)
        
        # Assert
        assert result == expected_output
    
    def test_example_function_with_mock(self):
        """Test function that uses external dependencies."""
        # Arrange
        with patch('app.utils.example_utils.external_call') as mock_external:
            mock_external.return_value = "mocked_result"
            input_data = "test_input"
            expected_output = "mocked_result_processed"
            
            # Act
            result = example_function(input_data)
            
            # Assert
            assert result == expected_output
            mock_external.assert_called_once_with(input_data)


# Async test examples
@pytest.mark.skip(reason="Template test - not meant to test actual application code")
@pytest.mark.asyncio
class TestAsyncExampleService:
    """Test suite for async service methods."""
    
    @pytest.fixture
    async def async_service(self):
        """Create an instance of async service for testing."""
        # return AsyncExampleService()
        pass
    
    async def test_async_method_success(self, async_service):
        """Test successful execution of async method."""
        # Arrange
        input_data = {"key": "value"}
        expected_result = {"result": "async_success"}
        
        # Act
        result = await async_service.async_method(input_data)
        
        # Assert
        assert result == expected_result
    
    async def test_async_method_with_exception(self, async_service):
        """Test async method exception handling."""
        # Arrange
        with patch('app.services.async_example_service.external_async_call') as mock:
            mock.side_effect = Exception("External service error")
            
            # Act & Assert
            with pytest.raises(Exception, match="External service error"):
                await async_service.async_method({"key": "value"})


# Integration test examples (for reference)
@pytest.mark.skip(reason="Template test - not meant to test actual application code")
@pytest.mark.integration
class TestExampleIntegration:
    """Integration tests for example functionality."""
    
    async def test_example_integration_with_database(self, db_session):
        """Test integration with database."""
        # Arrange
        # Create test data in database
        
        # Act
        # Perform integration operation
        
        # Assert
        # Verify database state and results
        pass


# Performance test examples (for reference)
@pytest.mark.skip(reason="Template test - not meant to test actual application code")
@pytest.mark.slow
class TestExamplePerformance:
    """Performance tests for example functionality."""
    
    def test_example_performance_benchmark(self, benchmark):
        """Benchmark test for performance critical function."""
        # Arrange
        input_data = "performance_test_input"
        
        # Act & Assert
        result = benchmark(example_function, input_data)
        assert result is not None 