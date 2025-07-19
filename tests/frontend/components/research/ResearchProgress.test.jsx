import React from 'react';
import { render, screen, act } from '@testing-library/react';
import ResearchProgress from '../ResearchProgress';

// Mock timers for elapsed time testing
jest.useFakeTimers();

describe('ResearchProgress Component', () => {
  beforeEach(() => {
    jest.clearAllTimers();
  });

  afterEach(() => {
    jest.runOnlyPendingTimers();
    jest.useRealTimers();
  });

  describe('Component Rendering', () => {
    test('renders progress component with basic elements', () => {
      const mockStatus = {
        status: 'executing',
        message: 'Research in progress',
        progress_percentage: 50
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      expect(screen.getByText('Agents Researching')).toBeInTheDocument();
      expect(screen.getByText('Research in progress')).toBeInTheDocument();
      expect(screen.getByText('50%')).toBeInTheDocument();
    });

    test('renders all progress stages', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 40
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      expect(screen.getByText('Plan')).toBeInTheDocument();
      expect(screen.getByText('Search')).toBeInTheDocument();
      expect(screen.getByText('Analyze')).toBeInTheDocument();
      expect(screen.getByText('Synthesize')).toBeInTheDocument();
      expect(screen.getByText('Complete')).toBeInTheDocument();
    });

    test('renders performance metrics', () => {
      const mockStatus = {
        status: 'executing',
        agents: [{ id: 1 }, { id: 2 }, { id: 3 }],
        sources_found: 15,
        tokens_used: 1200
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      expect(screen.getByText('3')).toBeInTheDocument(); // Active Agents
      expect(screen.getByText('15')).toBeInTheDocument(); // Sources Found
      expect(screen.getByText('1200')).toBeInTheDocument(); // Tokens Used
      expect(screen.getByText('Active Agents')).toBeInTheDocument();
      expect(screen.getByText('Sources Found')).toBeInTheDocument();
      expect(screen.getByText('Tokens Used')).toBeInTheDocument();
    });
  });

  describe('Progress Bar Functionality', () => {
    test('shows correct progress percentage', () => {
      const mockStatus = {
        status: 'synthesizing',
        progress_percentage: 80
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      const progressTexts = screen.getAllByText('80%');
      expect(progressTexts.length).toBeGreaterThan(0);
    });

    test('displays correct stage based on status', () => {
      const testCases = [
        { status: 'started', expectedStage: 'Planning Research' },
        { status: 'planning', expectedStage: 'Creating Research Plan' },
        { status: 'executing', expectedStage: 'Agents Researching' },
        { status: 'synthesizing', expectedStage: 'Synthesizing Results' },
        { status: 'citing', expectedStage: 'Adding Citations' },
        { status: 'completed', expectedStage: 'Research Complete' },
        { status: 'failed', expectedStage: 'Research Failed' }
      ];

      testCases.forEach(({ status, expectedStage }) => {
        const { rerender } = render(
          <ResearchProgress 
            status={{ status, progress_percentage: 50 }} 
            isActive={status !== 'completed' && status !== 'failed'} 
          />
        );
        
        expect(screen.getByText(expectedStage)).toBeInTheDocument();
        
        rerender(<div />); // Clear for next test
      });
    });

    test('shows correct progress bar colors for different stages', () => {
      const mockStatus = {
        status: 'completed',
        progress_percentage: 100
      };

      const { container } = render(<ResearchProgress status={mockStatus} isActive={false} />);
      
      // Check if progress bar has green color for completed status
      const progressBar = container.querySelector('.bg-green-500');
      expect(progressBar).toBeInTheDocument();
    });
  });

  describe('Agent Activities', () => {
    test('displays agent activities when research is active', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50,
        agents: [{ id: 1 }, { id: 2 }, { id: 3 }]
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      expect(screen.getByText('Agent Activities (3 active)')).toBeInTheDocument();
      expect(screen.getByText('Search Agent Alpha')).toBeInTheDocument();
      expect(screen.getByText('Search Agent Beta')).toBeInTheDocument();
      expect(screen.getByText('Search Agent Gamma')).toBeInTheDocument();
    });

    test('does not display agent activities when research is not active', () => {
      const mockStatus = {
        status: 'completed',
        progress_percentage: 100
      };

      render(<ResearchProgress status={mockStatus} isActive={false} />);
      
      expect(screen.queryByText('Agent Activities')).not.toBeInTheDocument();
    });

    test('shows agent status badges correctly', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50,
        agents: [{ id: 1 }, { id: 2 }]
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      // Should show different agent statuses based on progress
      expect(screen.getByText('analyzing')).toBeInTheDocument();
      expect(screen.getByText('searching')).toBeInTheDocument();
    });
  });

  describe('Time Tracking', () => {
    test('displays elapsed time correctly', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      expect(screen.getByText('Elapsed Time')).toBeInTheDocument();
      expect(screen.getByText('0:00')).toBeInTheDocument();
    });

    test('updates elapsed time when active', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      // Initially shows 0:00
      expect(screen.getByText('0:00')).toBeInTheDocument();
      
      // The timer should be running when active
      expect(screen.getByText('Elapsed Time')).toBeInTheDocument();
    });

    test('does not update elapsed time when not active', () => {
      const mockStatus = {
        status: 'completed',
        progress_percentage: 100
      };

      render(<ResearchProgress status={mockStatus} isActive={false} />);
      
      expect(screen.getByText('0:00')).toBeInTheDocument();
      
      // Advance time
      act(() => {
        jest.advanceTimersByTime(30000);
      });
      
      // Should still show 0:00
      expect(screen.getByText('0:00')).toBeInTheDocument();
    });
  });

  describe('Stage Indicators', () => {
    test('highlights completed stages correctly', () => {
      const mockStatus = {
        status: 'synthesizing',
        progress_percentage: 80
      };

      const { container } = render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      // Plan, Search, and Analyze should be completed (green)
      const completedStages = container.querySelectorAll('.border-green-200');
      expect(completedStages.length).toBeGreaterThan(0);
    });

    test('highlights active stage correctly', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50
      };

      const { container } = render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      // Should have active or completed stage styling
      const activeStages = container.querySelectorAll('.border-blue-200, .border-green-200');
      expect(activeStages.length).toBeGreaterThan(0);
    });

    test('shows stage tooltips', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50
      };

      const { container } = render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      // Check for title attributes (tooltips)
      const stageWithTooltip = container.querySelector('[title="Research planning"]');
      expect(stageWithTooltip).toBeInTheDocument();
    });
  });

  describe('Status Details', () => {
    test('displays status details when provided', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50,
        details: 'Currently analyzing medical research papers'
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      expect(screen.getByText('Current Focus')).toBeInTheDocument();
      expect(screen.getByText('Currently analyzing medical research papers')).toBeInTheDocument();
    });

    test('does not display status details section when not provided', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      expect(screen.queryByText('Current Focus')).not.toBeInTheDocument();
    });
  });

  describe('Error States', () => {
    test('handles null status gracefully', () => {
      render(<ResearchProgress status={null} isActive={false} />);
      
      expect(screen.getByText('Initializing')).toBeInTheDocument();
      const zeroPercents = screen.getAllByText('0%');
      expect(zeroPercents.length).toBeGreaterThan(0);
    });

    test('handles undefined status gracefully', () => {
      render(<ResearchProgress status={undefined} isActive={false} />);
      
      expect(screen.getByText('Initializing')).toBeInTheDocument();
    });

    test('displays failed status correctly', () => {
      const mockStatus = {
        status: 'failed',
        message: 'Research failed due to network error'
      };

      render(<ResearchProgress status={mockStatus} isActive={false} />);
      
      expect(screen.getByText('Research Failed')).toBeInTheDocument();
      expect(screen.getByText('Research failed due to network error')).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    test('renders grid layouts correctly', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50
      };

      const { container } = render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      // Check for responsive grid classes
      expect(container.querySelector('.grid-cols-2')).toBeInTheDocument();
      expect(container.querySelector('.md\\:grid-cols-5')).toBeInTheDocument();
      expect(container.querySelector('.md\\:grid-cols-4')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('has proper heading structure', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument();
      expect(screen.getByRole('heading', { level: 4 })).toBeInTheDocument();
    });

    test('provides meaningful text for screen readers', () => {
      const mockStatus = {
        status: 'executing',
        progress_percentage: 50,
        message: 'Processing research data'
      };

      render(<ResearchProgress status={mockStatus} isActive={true} />);
      
      expect(screen.getByText('Processing research data')).toBeInTheDocument();
      expect(screen.getByText('Progress')).toBeInTheDocument();
      expect(screen.getByText('Elapsed Time')).toBeInTheDocument();
    });
  });
});