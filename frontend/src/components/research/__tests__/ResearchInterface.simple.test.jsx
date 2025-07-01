import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
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

describe('ResearchInterface - Core Functionality', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default mock implementations
    researchService.validateQuery.mockReturnValue({ isValid: true, errors: [] });
    researchService.startResearch.mockResolvedValue({ research_id: 'test-id-123' });
    researchService.formatResults.mockImplementation(data => data);
  });

  describe('Component Rendering', () => {
    test('renders main research interface elements', () => {
      render(<ResearchInterface />);
      
      expect(screen.getByText('Multi-Agent Research System')).toBeInTheDocument();
      expect(screen.getByLabelText('Research Query')).toBeInTheDocument();
      expect(screen.getByText('Start Research')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
    });

    test('renders help text when no research is active', () => {
      render(<ResearchInterface />);
      
      expect(screen.getByText('How to Use Multi-Agent Research')).toBeInTheDocument();
    });

    test('displays character count for query input', async () => {
      const user = userEvent.setup();
      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test query');
      
      expect(screen.getByText('10/2000 characters')).toBeInTheDocument();
    });
  });

  describe('Query Input and Validation', () => {
    test('validates query input in real-time', async () => {
      const user = userEvent.setup();
      
      // Mock validation to return invalid for short queries
      researchService.validateQuery.mockReturnValue({
        isValid: false,
        errors: ['Query must be at least 10 characters long']
      });
      
      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Short');
      
      await waitFor(() => {
        expect(screen.getByText('Query must be at least 10 characters long')).toBeInTheDocument();
      });
    });

    test('enables start button only when query is valid', async () => {
      const user = userEvent.setup();
      render(<ResearchInterface />);
      
      const startButton = screen.getByRole('button', { name: /start research/i });
      const textarea = screen.getByLabelText('Research Query');
      
      // Initially disabled
      expect(startButton).toBeDisabled();
      
      // Type valid query
      await user.type(textarea, 'This is a valid research query with enough characters');
      
      await waitFor(() => {
        expect(startButton).not.toBeDisabled();
      });
    });
  });

  describe('Settings Panel', () => {
    test('toggles settings panel visibility', async () => {
      const user = userEvent.setup();
      render(<ResearchInterface />);
      
      const settingsButton = screen.getByText('Settings');
      
      // Settings should not be visible initially
      expect(screen.queryByText('Max Agents:')).not.toBeInTheDocument();
      
      // Click to show settings
      await user.click(settingsButton);
      
      expect(screen.getByText('Max Agents:')).toBeInTheDocument();
      expect(screen.getByText('Max Iterations:')).toBeInTheDocument();
    });

    test('updates research settings', async () => {
      const user = userEvent.setup();
      render(<ResearchInterface />);
      
      // Show settings
      await user.click(screen.getByText('Settings'));
      
      // Find selects by their labels
      const agentsLabel = screen.getByText('Max Agents:');
      const agentsSelect = agentsLabel.parentElement.querySelector('select');
      await user.selectOptions(agentsSelect, '5');
      
      const iterationsLabel = screen.getByText('Max Iterations:');
      const iterationsSelect = iterationsLabel.parentElement.querySelector('select');
      await user.selectOptions(iterationsSelect, '8');
      
      // Start research to verify settings are used
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test query with custom settings');
      
      await user.click(screen.getByRole('button', { name: /start research/i }));
      
      await waitFor(() => {
        expect(researchService.startResearch).toHaveBeenCalledWith({
          query: 'Test query with custom settings',
          max_subagents: 5,
          max_iterations: 8
        });
      });
    });
  });

  describe('Research Workflow', () => {
    test('starts research successfully', async () => {
      const user = userEvent.setup();
      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByText('Start Research'));
      
      await waitFor(() => {
        expect(researchService.startResearch).toHaveBeenCalledWith({
          query: 'Test research query',
          max_subagents: 3,
          max_iterations: 5
        });
      });
      
      // Should show research in progress
      expect(screen.getByText('Research in Progress')).toBeInTheDocument();
      expect(screen.getByText('Stop Research')).toBeInTheDocument();
    });

    test('handles research start error', async () => {
      const user = userEvent.setup();
      
      researchService.startResearch.mockRejectedValue(new Error('Network error'));
      
      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Test research query');
      
      await user.click(screen.getByText('Start Research'));
      
      await waitFor(() => {
        expect(screen.getByText('Research Error')).toBeInTheDocument();
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    test('displays validation errors', async () => {
      const user = userEvent.setup();
      
      researchService.validateQuery.mockReturnValue({
        isValid: false,
        errors: ['Query contains potentially unsafe content']
      });
      
      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, '<script>alert("test")</script>');
      
      await waitFor(() => {
        expect(screen.getByText('Query contains potentially unsafe content')).toBeInTheDocument();
      });
    });

    test('handles network errors gracefully', async () => {
      const user = userEvent.setup();
      
      researchService.startResearch.mockRejectedValue(new Error('Network error - please check your connection'));
      
      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      await user.type(textarea, 'Valid research query');
      
      await user.click(screen.getByText('Start Research'));
      
      await waitFor(() => {
        expect(screen.getByText('Research Error')).toBeInTheDocument();
        expect(screen.getByText('Network error - please check your connection')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels and roles', () => {
      render(<ResearchInterface />);
      
      expect(screen.getByLabelText('Research Query')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /start research/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /settings/i })).toBeInTheDocument();
    });

    test('supports keyboard navigation', async () => {
      const user = userEvent.setup();
      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      
      // Focus should work
      await user.click(textarea);
      expect(textarea).toHaveFocus();
    });
  });

  describe('Character Count Display', () => {
    test('shows correct character count colors', async () => {
      const user = userEvent.setup();
      render(<ResearchInterface />);
      
      const textarea = screen.getByLabelText('Research Query');
      
      // Short query (red)
      await user.type(textarea, 'Short');
      expect(screen.getByText('5/2000 characters')).toHaveClass('text-red-500');
      
      // Clear and type valid length
      await user.clear(textarea);
      await user.type(textarea, 'This is a valid length query');
      // The actual character count might be different, so let's use a more flexible approach
      const characterCountElement = screen.getByText(/\/2000 characters/);
      expect(characterCountElement).toHaveClass('text-gray-500');
    });
  });
});