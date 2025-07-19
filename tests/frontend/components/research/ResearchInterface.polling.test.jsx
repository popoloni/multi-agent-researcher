import React from 'react';
import { render, screen, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ResearchInterface from '../ResearchInterface';
import { researchService } from '../../../services/research';

// Mock the research service
jest.mock('../../../services/research', () => ({
  researchService: {
    validateQuery: jest.fn(),
    startResearch: jest.fn(),
    getResearchStatus: jest.fn(),
    getResearchResult: jest.fn(),
    cancelResearch: jest.fn(),
    formatResults: jest.fn()
  }
}));

// Mock timers for polling tests
jest.useFakeTimers();

describe('ResearchInterface - Polling Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.clearAllTimers();
    
    // Default mock implementations
    researchService.validateQuery.mockReturnValue({ isValid: true, errors: [] });
    researchService.startResearch.mockResolvedValue({ research_id: 'test-id-123' });
    researchService.formatResults.mockImplementation(data => data);
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Real-time Polling Mechanism', () => {
    test('polls for status updates at correct intervals', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
      
      researchService.getResearchStatus.mockResolvedValue({
        status: 'executing',
        message: 'Research in progress',
        progress_percentage: 50
      });

      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByRole('button', { name: /start research/i }));
      
      // Wait for research to start
      await waitFor(() => {
        expect(screen.getByText('Research in progress...')).toBeInTheDocument();
      });
      
      // Verify initial status call
      expect(researchService.getResearchStatus).toHaveBeenCalledWith('test-id-123');
      
      // Advance time by 2 seconds to trigger next poll
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      await waitFor(() => {
        expect(researchService.getResearchStatus).toHaveBeenCalledTimes(2);
      });
      
      // Advance time again
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      await waitFor(() => {
        expect(researchService.getResearchStatus).toHaveBeenCalledTimes(3);
      });
    });

    test('stops polling when research completes', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
      
      // Mock status progression
      let callCount = 0;
      researchService.getResearchStatus.mockImplementation(() => {
        callCount++;
        if (callCount <= 2) {
          return Promise.resolve({
            status: 'executing',
            message: 'Research in progress',
            progress_percentage: 50
          });
        } else {
          return Promise.resolve({
            status: 'completed',
            message: 'Research completed successfully'
          });
        }
      });
      
      researchService.getResearchResult.mockResolvedValue({
        report: 'Test research report',
        sources_used: [],
        citations: []
      });

      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByRole('button', { name: /start research/i }));
      
      // Wait for research to start
      await waitFor(() => {
        expect(screen.getByText('Research in progress...')).toBeInTheDocument();
      });
      
      // Advance time to trigger polls until completion
      act(() => {
        jest.advanceTimersByTime(6000); // 3 polls at 2-second intervals
      });
      
      await waitFor(() => {
        expect(screen.getByText('Research Complete')).toBeInTheDocument();
      });
      
      // Advance time further to ensure polling has stopped
      const statusCallsBefore = researchService.getResearchStatus.mock.calls.length;
      
      act(() => {
        jest.advanceTimersByTime(10000);
      });
      
      // Should not have made additional status calls
      expect(researchService.getResearchStatus.mock.calls.length).toBe(statusCallsBefore);
    });

    test('handles connection errors with retry logic', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
      
      // Mock network errors for first few calls, then success
      let callCount = 0;
      researchService.getResearchStatus.mockImplementation(() => {
        callCount++;
        if (callCount <= 2) {
          return Promise.reject(new Error('Network error'));
        } else {
          return Promise.resolve({
            status: 'executing',
            message: 'Research in progress',
            progress_percentage: 50
          });
        }
      });

      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByRole('button', { name: /start research/i }));
      
      // Wait for research to start
      await waitFor(() => {
        expect(screen.getByText('Research in progress...')).toBeInTheDocument();
      });
      
      // Advance time to trigger retries
      act(() => {
        jest.advanceTimersByTime(10000);
      });
      
      // Should have retried and eventually succeeded
      await waitFor(() => {
        expect(researchService.getResearchStatus).toHaveBeenCalledTimes(3);
      });
      
      // Should still be researching (not failed)
      expect(screen.getByText('Research in progress...')).toBeInTheDocument();
    });

    test('fails after maximum retry attempts', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
      
      // Mock persistent network errors
      researchService.getResearchStatus.mockRejectedValue(new Error('Network error'));

      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByRole('button', { name: /start research/i }));
      
      // Wait for research to start
      await waitFor(() => {
        expect(screen.getByText('Research in progress...')).toBeInTheDocument();
      });
      
      // Advance time to trigger maximum retries
      act(() => {
        jest.advanceTimersByTime(30000); // Enough time for all retries
      });
      
      // Should show connection error
      await waitFor(() => {
        expect(screen.getByText('Research Error')).toBeInTheDocument();
        expect(screen.getByText(/Connection lost/)).toBeInTheDocument();
      });
    });

    test('updates progress in real-time', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
      
      // Mock progressive status updates
      let callCount = 0;
      researchService.getResearchStatus.mockImplementation(() => {
        callCount++;
        return Promise.resolve({
          status: 'executing',
          message: 'Research in progress',
          progress_percentage: callCount * 25 // 25%, 50%, 75%, etc.
        });
      });

      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByRole('button', { name: /start research/i }));
      
      // Wait for research to start
      await waitFor(() => {
        expect(screen.getByText('Research in progress...')).toBeInTheDocument();
      });
      
      // Advance time to trigger first update
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      await waitFor(() => {
        expect(screen.getByText('50%')).toBeInTheDocument();
      });
      
      // Advance time to trigger second update
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      await waitFor(() => {
        expect(screen.getByText('75%')).toBeInTheDocument();
      });
    });

    test('handles research failure during polling', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
      
      // Mock status that changes to failed
      let callCount = 0;
      researchService.getResearchStatus.mockImplementation(() => {
        callCount++;
        if (callCount <= 1) {
          return Promise.resolve({
            status: 'executing',
            message: 'Research in progress',
            progress_percentage: 30
          });
        } else {
          return Promise.resolve({
            status: 'failed',
            message: 'Research failed due to insufficient data'
          });
        }
      });

      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByRole('button', { name: /start research/i }));
      
      // Wait for research to start
      await waitFor(() => {
        expect(screen.getByText('Research in progress...')).toBeInTheDocument();
      });
      
      // Advance time to trigger status update that shows failure
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      await waitFor(() => {
        expect(screen.getByText('Research Error')).toBeInTheDocument();
        expect(screen.getByText('Research failed due to insufficient data')).toBeInTheDocument();
      });
    });

    test('cleans up polling interval on component unmount', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
      
      researchService.getResearchStatus.mockResolvedValue({
        status: 'executing',
        message: 'Research in progress',
        progress_percentage: 50
      });

      const { unmount } = render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByRole('button', { name: /start research/i }));
      
      // Wait for research to start
      await waitFor(() => {
        expect(screen.getByText('Research in progress...')).toBeInTheDocument();
      });
      
      // Verify polling is active
      expect(researchService.getResearchStatus).toHaveBeenCalled();
      
      // Unmount component
      unmount();
      
      // Advance time - should not trigger more calls
      const callsBefore = researchService.getResearchStatus.mock.calls.length;
      
      act(() => {
        jest.advanceTimersByTime(10000);
      });
      
      // Should not have made additional calls after unmount
      expect(researchService.getResearchStatus.mock.calls.length).toBe(callsBefore);
    });

    test('stops polling when user manually stops research', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
      
      researchService.getResearchStatus.mockResolvedValue({
        status: 'executing',
        message: 'Research in progress',
        progress_percentage: 50
      });

      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByRole('button', { name: /start research/i }));
      
      // Wait for research to start
      await waitFor(() => {
        expect(screen.getByText('Stop Research')).toBeInTheDocument();
      });
      
      // Stop the research
      await user.click(screen.getByText('Stop Research'));
      
      // Verify polling stops
      const callsBefore = researchService.getResearchStatus.mock.calls.length;
      
      act(() => {
        jest.advanceTimersByTime(10000);
      });
      
      // Should not have made additional calls after stopping
      expect(researchService.getResearchStatus.mock.calls.length).toBe(callsBefore);
    });
  });

  describe('Performance Optimization', () => {
    test('does not poll when research is not active', async () => {
      render(<ResearchInterface />);
      
      // Advance time without starting research
      act(() => {
        jest.advanceTimersByTime(10000);
      });
      
      // Should not have made any status calls
      expect(researchService.getResearchStatus).not.toHaveBeenCalled();
    });

    test('handles rapid status changes efficiently', async () => {
      const user = userEvent.setup({ advanceTimers: jest.advanceTimersByTime });
      
      // Mock rapid status changes
      const statuses = ['started', 'planning', 'executing', 'synthesizing', 'completed'];
      let callCount = 0;
      
      researchService.getResearchStatus.mockImplementation(() => {
        const status = statuses[Math.min(callCount, statuses.length - 1)];
        callCount++;
        
        if (status === 'completed') {
          return Promise.resolve({ status, message: 'Research completed' });
        }
        
        return Promise.resolve({
          status,
          message: `Research ${status}`,
          progress_percentage: callCount * 20
        });
      });
      
      researchService.getResearchResult.mockResolvedValue({
        report: 'Test research report',
        sources_used: [],
        citations: []
      });

      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByRole('button', { name: /start research/i }));
      
      // Advance time rapidly
      act(() => {
        jest.advanceTimersByTime(10000);
      });
      
      // Should handle all status changes and complete
      await waitFor(() => {
        expect(screen.getByText('Research Complete')).toBeInTheDocument();
      });
    });
  });
});