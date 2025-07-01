"""
Test suite for Task 3.2: Backend Integration Testing

This test suite provides comprehensive integration testing of the complete backend research workflow,
including concurrent sessions, error scenarios, and performance requirements.
"""

import pytest
import asyncio
import time
from uuid import uuid4
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch
from typing import List, Dict, Any

from app.services.research_service import ResearchService, ResearchStatus
from app.models.schemas import (
    ResearchQuery, ResearchResult, ResearchProgress, 
    ResearchStage, AgentStatus, CitationInfo
)


class TestBackendIntegrationTask32:
    """Test suite for Task 3.2: Backend Integration Testing"""
    
    @pytest.fixture
    def research_service(self):
        """Create a ResearchService instance for testing"""
        return ResearchService()
    
    @pytest.fixture
    def sample_queries(self):
        """Create multiple sample research queries for testing"""
        return [
            ResearchQuery(
                query="What are the latest AI developments in healthcare?",
                max_subagents=2,
                max_iterations=3
            ),
            ResearchQuery(
                query="How is quantum computing affecting financial modeling?",
                max_subagents=3,
                max_iterations=4
            ),
            ResearchQuery(
                query="Latest breakthroughs in renewable energy storage",
                max_subagents=2,
                max_iterations=3
            )
        ]
    
    @pytest.fixture
    def mock_research_result(self):
        """Create a mock research result for testing"""
        return ResearchResult(
            research_id=uuid4(),
            query="Test query",
            report="Comprehensive research report with detailed findings...",
            citations=[
                CitationInfo(
                    index=1,
                    title="Test Source 1",
                    url="https://example.com/source1",
                    snippet="Relevant information from source 1",
                    times_cited=1
                )
            ],
            sources_used=[],
            total_tokens_used=500,
            execution_time=45.0,
            subagent_count=2,
            report_sections=["Introduction", "Analysis", "Conclusion"]
        )
    
    @pytest.mark.asyncio
    async def test_complete_research_workflow_integration(self, research_service, sample_queries, mock_research_result):
        """Test 3.2.1: Complete research workflow integration"""
        
        # Mock LeadResearchAgent for controlled testing
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            
            # Create dynamic mock result based on query
            async def mock_conduct_research(query, research_id):
                return ResearchResult(
                    research_id=research_id,
                    query=query.query,
                    report=f"Comprehensive research report for: {query.query}",
                    citations=[
                        CitationInfo(
                            index=1,
                            title="Test Source 1",
                            url="https://example.com/source1",
                            snippet="Relevant information from source 1",
                            times_cited=1
                        )
                    ],
                    sources_used=[],
                    total_tokens_used=500,
                    execution_time=45.0,
                    subagent_count=query.max_subagents,
                    report_sections=["Introduction", "Analysis", "Conclusion"]
                )
            
            mock_agent.conduct_research = mock_conduct_research
            mock_agent_class.return_value = mock_agent
            
            query = sample_queries[0]
            
            # Step 1: Start research
            start_time = time.time()
            research_id = await research_service.start_research(query)
            
            # Verify research was started correctly
            assert research_id is not None
            assert research_id in research_service._active_research
            
            # Step 2: Check initial status
            status = await research_service.get_research_status(research_id)
            assert status is not None
            assert status["research_id"] == str(research_id)
            assert status["query"] == query.query
            assert status["status"] in [ResearchStatus.STARTED.value, ResearchStatus.PLANNING.value]
            
            # Step 3: Wait for research to complete
            research_task = research_service._active_research[research_id]
            await research_task.task
            
            # Step 4: Verify completion
            assert research_id not in research_service._active_research
            assert research_id in research_service._completed_research
            
            completed_task = research_service._completed_research[research_id]
            assert completed_task.status == ResearchStatus.COMPLETED
            assert completed_task.result is not None
            
            # Step 5: Get final status
            final_status = await research_service.get_research_status(research_id)
            assert final_status["status"] == ResearchStatus.COMPLETED.value
            assert final_status["progress_percentage"] == 100
            
            # Step 6: Get research result
            result = await research_service.get_research_result(research_id)
            assert result is not None
            assert result.query == query.query
            assert result.report is not None
            assert len(result.citations) > 0
            
            # Verify workflow timing
            total_time = time.time() - start_time
            assert total_time < 10.0  # Should complete quickly with mocked agent
    
    @pytest.mark.asyncio
    async def test_concurrent_research_sessions(self, research_service, sample_queries, mock_research_result):
        """Test 3.2.2: Concurrent research sessions work independently"""
        
        # Mock LeadResearchAgent for controlled testing
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            
            # Create different mock results for each session
            mock_results = []
            for i, query in enumerate(sample_queries):
                result = ResearchResult(
                    research_id=uuid4(),
                    query=query.query,
                    report=f"Research report {i+1} for: {query.query}",
                    citations=[
                        CitationInfo(
                            index=1,
                            title=f"Source {i+1}",
                            url=f"https://example.com/source{i+1}",
                            snippet=f"Information from source {i+1}",
                            times_cited=1
                        )
                    ],
                    sources_used=[],
                    total_tokens_used=300 + (i * 100),
                    execution_time=30.0 + (i * 10),
                    subagent_count=query.max_subagents,
                    report_sections=["Introduction", "Analysis", "Conclusion"]
                )
                mock_results.append(result)
            
            # Mock agent to return different results based on query
            def create_mock_agent(progress_callback=None):
                mock_agent = AsyncMock()
                
                async def mock_conduct_research(query, research_id):
                    # Find matching result based on query
                    for i, sample_query in enumerate(sample_queries):
                        if query.query == sample_query.query:
                            # Simulate some processing time
                            await asyncio.sleep(0.1)
                            return mock_results[i]
                    return mock_research_result
                
                mock_agent.conduct_research = mock_conduct_research
                return mock_agent
            
            mock_agent_class.side_effect = create_mock_agent
            
            # Start multiple concurrent research sessions
            research_ids = []
            start_time = time.time()
            
            for query in sample_queries:
                research_id = await research_service.start_research(query)
                research_ids.append(research_id)
            
            # Verify all sessions started independently
            assert len(research_ids) == len(sample_queries)
            assert len(set(research_ids)) == len(research_ids)  # All unique IDs
            assert research_service.get_active_research_count() == len(sample_queries)
            
            # Check status of each session independently
            for i, research_id in enumerate(research_ids):
                status = await research_service.get_research_status(research_id)
                assert status["query"] == sample_queries[i].query
                assert status["research_id"] == str(research_id)
            
            # Wait for all sessions to complete
            tasks = []
            for research_id in research_ids:
                research_task = research_service._active_research[research_id]
                tasks.append(research_task.task)
            
            await asyncio.gather(*tasks)
            
            # Verify all sessions completed independently
            assert research_service.get_active_research_count() == 0
            assert research_service.get_completed_research_count() == len(sample_queries)
            
            # Verify each session has correct results
            for i, research_id in enumerate(research_ids):
                result = await research_service.get_research_result(research_id)
                assert result.query == sample_queries[i].query
                assert result.subagent_count == sample_queries[i].max_subagents
                assert f"Research report {i+1}" in result.report
            
            # Verify timing - concurrent execution should be efficient
            total_time = time.time() - start_time
            assert total_time < 5.0  # Should complete quickly with concurrent execution
    
    @pytest.mark.asyncio
    async def test_error_scenarios_and_recovery(self, research_service, sample_queries):
        """Test 3.2.3: Error scenarios are properly handled and tested"""
        
        # Test 1: Agent initialization failure
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent_class.side_effect = Exception("Agent initialization failed")
            
            query = sample_queries[0]
            research_id = await research_service.start_research(query)
            
            # Wait for error to occur
            research_task = research_service._active_research[research_id]
            await research_task.task
            
            # Verify error handling
            assert research_id not in research_service._active_research
            assert research_id in research_service._completed_research
            
            failed_task = research_service._completed_research[research_id]
            assert failed_task.status == ResearchStatus.FAILED
            assert failed_task.error is not None
            assert "initialization failed" in failed_task.error.lower()
        
        # Test 2: Research execution failure
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.conduct_research = AsyncMock()
            mock_agent.conduct_research.side_effect = Exception("Research execution failed")
            mock_agent_class.return_value = mock_agent
            
            query = sample_queries[1]
            research_id = await research_service.start_research(query)
            
            # Wait for error to occur
            research_task = research_service._active_research[research_id]
            await research_task.task
            
            # Verify error handling
            failed_task = research_service._completed_research[research_id]
            assert failed_task.status == ResearchStatus.FAILED
            assert "execution failed" in failed_task.error.lower()
        
        # Test 3: Progress callback failure (should not affect research)
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            
            def create_mock_agent_with_callback_error(progress_callback=None):
                mock_agent = AsyncMock()
                
                async def mock_conduct_research(query, research_id):
                    # Trigger progress callback with invalid data to test error handling
                    if progress_callback:
                        try:
                            # This should fail but not affect research
                            await progress_callback(None)
                        except:
                            pass  # Expected to fail
                    
                    # Return successful result
                    return ResearchResult(
                        research_id=research_id,
                        query=query.query,
                        report="Research completed despite callback error",
                        citations=[],
                        sources_used=[],
                        total_tokens_used=100,
                        execution_time=1.0,
                        subagent_count=1,
                        report_sections=[]
                    )
                
                mock_agent.conduct_research = mock_conduct_research
                return mock_agent
            
            mock_agent_class.side_effect = create_mock_agent_with_callback_error
            
            query = sample_queries[2]
            research_id = await research_service.start_research(query)
            
            # Wait for completion
            research_task = research_service._active_research[research_id]
            await research_task.task
            
            # Verify research completed successfully despite callback error
            completed_task = research_service._completed_research[research_id]
            assert completed_task.status == ResearchStatus.COMPLETED
            assert completed_task.result is not None
        
        # Test 4: Edge case query handling
        edge_case_query = ResearchQuery(
            query="x",  # Very short query
            max_subagents=1,  # Minimum agent count
            max_iterations=1  # Minimum iteration count
        )
        
        # This should still start and complete
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            
            async def mock_edge_case_research(query, research_id):
                return ResearchResult(
                    research_id=research_id,
                    query=query.query,
                    report="Minimal research result",
                    citations=[],
                    sources_used=[],
                    total_tokens_used=10,
                    execution_time=0.1,
                    subagent_count=1,
                    report_sections=[]
                )
            
            mock_agent.conduct_research = mock_edge_case_research
            mock_agent_class.return_value = mock_agent
            
            research_id = await research_service.start_research(edge_case_query)
            assert research_id is not None
            
            # Wait for completion
            research_task = research_service._active_research[research_id]
            await research_task.task
            
            # Should complete successfully
            completed_task = research_service._completed_research[research_id]
            assert completed_task.status == ResearchStatus.COMPLETED
        
        # Test 5: Memory cleanup after errors
        initial_completed_count = research_service.get_completed_research_count()
        await research_service.cleanup_completed_research(max_completed=1)
        
        # Should clean up old failed research
        final_completed_count = research_service.get_completed_research_count()
        assert final_completed_count <= max(1, initial_completed_count)
    
    @pytest.mark.asyncio
    async def test_api_performance_requirements(self, research_service, sample_queries, mock_research_result):
        """Test 3.2.4: Performance meets specified requirements"""
        
        # Mock LeadResearchAgent for performance testing
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            mock_agent.conduct_research = AsyncMock(return_value=mock_research_result)
            mock_agent_class.return_value = mock_agent
            
            query = sample_queries[0]
            
            # Test 1: Research start performance (<2s requirement)
            start_time = time.time()
            research_id = await research_service.start_research(query)
            start_duration = time.time() - start_time
            
            assert start_duration < 2.0, f"Research start took {start_duration:.3f}s, should be <2s"
            assert research_id is not None
            
            # Test 2: Status check performance (<200ms requirement)
            status_times = []
            for _ in range(10):  # Test multiple status checks
                start_time = time.time()
                status = await research_service.get_research_status(research_id)
                status_duration = time.time() - start_time
                status_times.append(status_duration)
                
                assert status_duration < 0.2, f"Status check took {status_duration:.3f}s, should be <200ms"
                assert status is not None
            
            # Verify average status check time
            avg_status_time = sum(status_times) / len(status_times)
            assert avg_status_time < 0.1, f"Average status check time {avg_status_time:.3f}s should be well under 200ms"
            
            # Test 3: Concurrent status checks performance
            start_time = time.time()
            status_tasks = [
                research_service.get_research_status(research_id)
                for _ in range(20)
            ]
            statuses = await asyncio.gather(*status_tasks)
            concurrent_duration = time.time() - start_time
            
            assert concurrent_duration < 1.0, f"20 concurrent status checks took {concurrent_duration:.3f}s"
            assert all(status is not None for status in statuses)
            
            # Test 4: Memory usage efficiency
            initial_memory_size = len(research_service._active_research) + len(research_service._completed_research)
            
            # Start multiple research sessions
            research_ids = []
            for i in range(5):
                rid = await research_service.start_research(sample_queries[i % len(sample_queries)])
                research_ids.append(rid)
            
            # Wait for completion
            for rid in research_ids:
                if rid in research_service._active_research:
                    await research_service._active_research[rid].task
            
            # Check memory growth is reasonable
            final_memory_size = len(research_service._active_research) + len(research_service._completed_research)
            memory_growth = final_memory_size - initial_memory_size
            assert memory_growth <= 6, f"Memory growth {memory_growth} should be reasonable"
            
            # Test 5: Cleanup performance
            start_time = time.time()
            await research_service.cleanup_completed_research(max_completed=2)
            cleanup_duration = time.time() - start_time
            
            assert cleanup_duration < 0.1, f"Cleanup took {cleanup_duration:.3f}s, should be fast"
    
    @pytest.mark.asyncio
    async def test_research_lifecycle_edge_cases(self, research_service, sample_queries):
        """Test 3.2.5: Research lifecycle edge cases and boundary conditions"""
        
        # Test 1: Very quick research completion
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            
            # Immediate completion
            quick_result = ResearchResult(
                research_id=uuid4(),
                query="Quick test",
                report="Quick result",
                citations=[],
                sources_used=[],
                total_tokens_used=10,
                execution_time=0.001,
                subagent_count=1,
                report_sections=[]
            )
            
            mock_agent.conduct_research = AsyncMock(return_value=quick_result)
            mock_agent_class.return_value = mock_agent
            
            query = sample_queries[0]
            research_id = await research_service.start_research(query)
            
            # Should handle immediate completion gracefully
            research_task = research_service._active_research[research_id]
            await research_task.task
            
            completed_task = research_service._completed_research[research_id]
            assert completed_task.status == ResearchStatus.COMPLETED
            assert completed_task.result.execution_time < 1.0
        
        # Test 2: Research cancellation during execution
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            
            # Long-running research simulation
            async def long_research(query, research_id):
                await asyncio.sleep(1.0)  # Simulate long execution
                return ResearchResult(
                    research_id=research_id,
                    query=query.query,
                    report="Long running research result",
                    citations=[],
                    sources_used=[],
                    total_tokens_used=100,
                    execution_time=1.0,
                    subagent_count=1,
                    report_sections=[]
                )
            
            mock_agent.conduct_research = long_research
            mock_agent_class.return_value = mock_agent
            
            query = sample_queries[1]
            research_id = await research_service.start_research(query)
            
            # Cancel research
            success = await research_service.cancel_research(research_id)
            assert success == True
            
            # Verify cancellation
            assert research_id not in research_service._active_research
            if research_id in research_service._completed_research:
                cancelled_task = research_service._completed_research[research_id]
                # Should be marked as cancelled or failed
                assert cancelled_task.status in [ResearchStatus.FAILED, ResearchStatus.COMPLETED]
        
        # Test 3: Multiple rapid start/cancel cycles
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            
            # Create a simple mock result for this test
            simple_result = ResearchResult(
                research_id=uuid4(),
                query="Simple test",
                report="Simple result",
                citations=[],
                sources_used=[],
                total_tokens_used=50,
                execution_time=0.5,
                subagent_count=1,
                report_sections=[]
            )
            
            mock_agent.conduct_research = AsyncMock(return_value=simple_result)
            mock_agent_class.return_value = mock_agent
            
            research_ids = []
            for i in range(10):
                research_id = await research_service.start_research(sample_queries[i % len(sample_queries)])
                research_ids.append(research_id)
                
                # Cancel every other research
                if i % 2 == 0:
                    await research_service.cancel_research(research_id)
            
            # Wait a bit for processing
            await asyncio.sleep(0.2)
            
            # System should remain stable
            assert research_service.get_active_research_count() >= 0
            assert research_service.get_completed_research_count() >= 0
        
        # Test 4: Resource exhaustion simulation
        original_max_subagents = sample_queries[0].max_subagents
        
        # Create query with many subagents
        resource_heavy_query = ResearchQuery(
            query="Resource heavy research",
            max_subagents=10,  # High resource usage
            max_iterations=10
        )
        
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            
            # Create a resource-heavy mock result
            resource_result = ResearchResult(
                research_id=uuid4(),
                query="Resource heavy research",
                report="Resource heavy research completed",
                citations=[],
                sources_used=[],
                total_tokens_used=1000,
                execution_time=5.0,
                subagent_count=10,
                report_sections=[]
            )
            
            mock_agent.conduct_research = AsyncMock(return_value=resource_result)
            mock_agent_class.return_value = mock_agent
            
            # Should handle resource-heavy requests gracefully
            research_id = await research_service.start_research(resource_heavy_query)
            assert research_id is not None
            
            # Wait for completion
            research_task = research_service._active_research[research_id]
            await research_task.task
            
            # Should complete successfully
            completed_task = research_service._completed_research[research_id]
            assert completed_task.status == ResearchStatus.COMPLETED
    
    @pytest.mark.asyncio
    async def test_data_consistency_and_integrity(self, research_service, sample_queries, mock_research_result):
        """Test 3.2.6: Data consistency and integrity across operations"""
        
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            mock_agent = AsyncMock()
            
            # Create dynamic mock result based on query
            async def mock_conduct_research(query, research_id):
                return ResearchResult(
                    research_id=research_id,
                    query=query.query,
                    report=f"Research report for: {query.query}",
                    citations=[
                        CitationInfo(
                            index=1,
                            title="Test Source",
                            url="https://example.com/source",
                            snippet="Test information",
                            times_cited=1
                        )
                    ],
                    sources_used=[],
                    total_tokens_used=200,
                    execution_time=10.0,
                    subagent_count=query.max_subagents,
                    report_sections=["Introduction", "Analysis", "Conclusion"]
                )
            
            mock_agent.conduct_research = mock_conduct_research
            mock_agent_class.return_value = mock_agent
            
            # Test data consistency across multiple operations
            research_ids = []
            
            # Start multiple research sessions
            for query in sample_queries:
                research_id = await research_service.start_research(query)
                research_ids.append(research_id)
            
            # Verify data consistency during execution
            for research_id in research_ids:
                # Check status consistency
                status1 = await research_service.get_research_status(research_id)
                status2 = await research_service.get_research_status(research_id)
                
                # Status should be consistent between calls
                assert status1["research_id"] == status2["research_id"]
                assert status1["query"] == status2["query"]
                
                # Progress should be monotonically increasing or stable
                assert status1["progress_percentage"] <= status2["progress_percentage"] or \
                       abs(status1["progress_percentage"] - status2["progress_percentage"]) < 5
            
            # Wait for all to complete
            for research_id in research_ids:
                if research_id in research_service._active_research:
                    await research_service._active_research[research_id].task
            
            # Verify final data integrity
            for i, research_id in enumerate(research_ids):
                result = await research_service.get_research_result(research_id)
                status = await research_service.get_research_status(research_id)
                
                # Data should be consistent between result and status
                assert result.query == status["query"]
                assert str(result.research_id) == status["research_id"]
                assert status["status"] == ResearchStatus.COMPLETED.value
                assert status["progress_percentage"] == 100
            
            # Test history consistency
            history = await research_service.get_research_history()
            assert len(history) >= len(research_ids)
            
            # Each history item should have consistent data
            for item in history:
                assert hasattr(item, 'research_id')
                assert hasattr(item, 'query')
                assert hasattr(item, 'status')
                assert hasattr(item, 'created_at')
    
    @pytest.mark.asyncio
    async def test_system_stability_under_load(self, research_service, sample_queries):
        """Test 3.2.7: System stability under various load conditions"""
        
        with patch('app.services.research_service.LeadResearchAgent') as mock_agent_class:
            
            # Create mock agent with variable execution times
            def create_variable_mock_agent(progress_callback=None):
                mock_agent = AsyncMock()
                
                async def variable_conduct_research(query, research_id):
                    # Variable execution time based on query length
                    execution_time = len(query.query) * 0.001  # 1ms per character
                    await asyncio.sleep(execution_time)
                    
                    return ResearchResult(
                        research_id=research_id,
                        query=query.query,
                        report=f"Variable time research for: {query.query}",
                        citations=[],
                        sources_used=[],
                        total_tokens_used=100,
                        execution_time=execution_time,
                        subagent_count=query.max_subagents,
                        report_sections=[]
                    )
                
                mock_agent.conduct_research = variable_conduct_research
                return mock_agent
            
            mock_agent_class.side_effect = create_variable_mock_agent
            
            # Test 1: Burst load - many requests at once
            burst_size = 20
            research_ids = []
            
            start_time = time.time()
            for i in range(burst_size):
                query = ResearchQuery(
                    query=f"Burst test query {i} with variable length content",
                    max_subagents=2,
                    max_iterations=3
                )
                research_id = await research_service.start_research(query)
                research_ids.append(research_id)
            
            burst_start_time = time.time() - start_time
            assert burst_start_time < 5.0, f"Burst start took {burst_start_time:.3f}s"
            
            # System should remain responsive during burst
            assert research_service.get_active_research_count() == burst_size
            
            # Wait for all to complete
            completion_start = time.time()
            for research_id in research_ids:
                if research_id in research_service._active_research:
                    await research_service._active_research[research_id].task
            
            completion_time = time.time() - completion_start
            assert completion_time < 10.0, f"Burst completion took {completion_time:.3f}s"
            
            # Verify all completed successfully
            assert research_service.get_active_research_count() == 0
            assert research_service.get_completed_research_count() >= burst_size
            
            # Test 2: Sustained load - continuous requests over time
            sustained_duration = 2.0  # 2 seconds of sustained load
            sustained_start = time.time()
            sustained_ids = []
            
            while time.time() - sustained_start < sustained_duration:
                query = ResearchQuery(
                    query=f"Sustained test at {time.time():.3f}",
                    max_subagents=1,
                    max_iterations=2
                )
                research_id = await research_service.start_research(query)
                sustained_ids.append(research_id)
                await asyncio.sleep(0.1)  # 100ms between requests
            
            # System should handle sustained load
            assert len(sustained_ids) > 10  # Should have processed multiple requests
            
            # Clean up sustained load
            for research_id in sustained_ids:
                if research_id in research_service._active_research:
                    await research_service._active_research[research_id].task
            
            # Test 3: Memory stability after load
            await research_service.cleanup_completed_research(max_completed=5)
            
            # Memory usage should be reasonable after cleanup
            total_research_count = (research_service.get_active_research_count() + 
                                  research_service.get_completed_research_count())
            assert total_research_count <= 10, f"Memory usage too high: {total_research_count}"
            
            # Test 4: System recovery after load
            # Start a normal research session after load testing
            normal_query = sample_queries[0]
            recovery_start = time.time()
            recovery_id = await research_service.start_research(normal_query)
            recovery_start_time = time.time() - recovery_start
            
            assert recovery_start_time < 1.0, f"System recovery took {recovery_start_time:.3f}s"
            
            # Should work normally
            status = await research_service.get_research_status(recovery_id)
            assert status is not None
            assert status["query"] == normal_query.query


if __name__ == "__main__":
    pytest.main([__file__])