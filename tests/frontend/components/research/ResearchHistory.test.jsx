import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ResearchHistory from '../ResearchHistory';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock data
const mockHistoryData = [
  {
    id: 'test-1',
    query: 'What are the latest developments in AI?',
    timestamp: new Date(Date.now() - 86400000).toISOString(),
    status: 'completed',
    sources_count: 15,
    duration: 180,
    tokens_used: 4500,
    subagent_count: 3,
    favorite: false,
    tags: ['AI', 'Technology']
  },
  {
    id: 'test-2',
    query: 'Climate change impact on agriculture',
    timestamp: new Date(Date.now() - 172800000).toISOString(),
    status: 'completed',
    sources_count: 12,
    duration: 150,
    tokens_used: 3200,
    subagent_count: 2,
    favorite: true,
    tags: ['Climate', 'Agriculture']
  },
  {
    id: 'test-3',
    query: 'Failed research query',
    timestamp: new Date(Date.now() - 259200000).toISOString(),
    status: 'failed',
    sources_count: 0,
    duration: 30,
    tokens_used: 500,
    subagent_count: 1,
    favorite: false,
    tags: []
  }
];

describe('ResearchHistory Component', () => {
  const mockOnSelectQuery = jest.fn();
  const mockOnLoadHistory = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(JSON.stringify(mockHistoryData));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    test('renders history component with header', () => {
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      expect(screen.getByText('Research History')).toBeInTheDocument();
      expect(screen.getByTitle('Refresh history')).toBeInTheDocument();
    });

    test('displays loading state initially', () => {
      localStorageMock.getItem.mockReturnValue(null);
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      expect(screen.getByText('Loading research history...')).toBeInTheDocument();
    });

    test('displays history items when loaded', async () => {
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
        expect(screen.getByText('Climate change impact on agriculture')).toBeInTheDocument();
      });
    });

    test('displays empty state when no history', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      mockOnLoadHistory.mockResolvedValue([]);
      
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} onLoadHistory={mockOnLoadHistory} />);
      
      await waitFor(() => {
        expect(screen.getByText('No Research History')).toBeInTheDocument();
        expect(screen.getByText('Start your first research query to see results here.')).toBeInTheDocument();
      });
    });
  });

  describe('History Management', () => {
    test('query reuse functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      const queryButton = screen.getByText('What are the latest developments in AI?');
      await user.click(queryButton);
      
      expect(mockOnSelectQuery).toHaveBeenCalledWith('What are the latest developments in AI?');
    });

    test('delete functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      const deleteButtons = screen.getAllByTitle('Delete from history');
      await user.click(deleteButtons[0]);
      
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });

    test('favorite toggle functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      const favoriteButtons = screen.getAllByTitle(/favorites/);
      await user.click(favoriteButtons[0]);
      
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });

    test('refresh functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} onLoadHistory={mockOnLoadHistory} />);
      
      const refreshButton = screen.getByTitle('Refresh history');
      await user.click(refreshButton);
      
      expect(mockOnLoadHistory).toHaveBeenCalled();
    });
  });

  describe('Search and Filtering', () => {
    test('search functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      const searchInput = screen.getByPlaceholderText('Search research history...');
      await user.type(searchInput, 'AI');
      
      expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      expect(screen.queryByText('Climate change impact on agriculture')).not.toBeInTheDocument();
    });

    test('status filter works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('Failed research query')).toBeInTheDocument();
      });
      
      const statusFilter = screen.getByDisplayValue('All Status');
      await user.selectOptions(statusFilter, 'failed');
      
      expect(screen.getByText('Failed research query')).toBeInTheDocument();
      expect(screen.queryByText('What are the latest developments in AI?')).not.toBeInTheDocument();
    });

    test('sorting functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      const sortSelect = screen.getByDisplayValue('Newest First');
      await user.selectOptions(sortSelect, 'duration-desc');
      
      // Verify the sort option was selected
      expect(screen.getByDisplayValue('Longest Duration')).toBeInTheDocument();
    });

    test('displays no results when search has no matches', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      const searchInput = screen.getByPlaceholderText('Search research history...');
      await user.type(searchInput, 'nonexistent query');
      
      expect(screen.getByText('No Results Found')).toBeInTheDocument();
      expect(screen.getByText('Try adjusting your search or filter criteria.')).toBeInTheDocument();
    });
  });

  describe('Bulk Operations', () => {
    test('select all functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      const selectAllButton = screen.getByText('Select All');
      await user.click(selectAllButton);
      
      expect(screen.getByText('3 selected')).toBeInTheDocument();
      expect(screen.getByText('Delete Selected')).toBeInTheDocument();
    });

    test('bulk delete functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      // Select all items
      const selectAllButton = screen.getByText('Select All');
      await user.click(selectAllButton);
      
      // Delete selected
      const deleteSelectedButton = screen.getByText('Delete Selected');
      await user.click(deleteSelectedButton);
      
      expect(localStorageMock.setItem).toHaveBeenCalled();
    });

    test('individual item selection works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      const checkboxes = screen.getAllByRole('checkbox');
      await user.click(checkboxes[0]);
      
      expect(screen.getByText('1 selected')).toBeInTheDocument();
    });
  });

  describe('Data Formatting', () => {
    test('formats time correctly', async () => {
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('3m 0s')).toBeInTheDocument(); // 180 seconds
        expect(screen.getByText('2m 30s')).toBeInTheDocument(); // 150 seconds
      });
    });

    test('formats dates correctly', async () => {
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        // Should show relative dates like "1d ago", "2d ago", etc.
        expect(screen.getByText(/\d+d ago/)).toBeInTheDocument();
      });
    });

    test('displays status badges correctly', async () => {
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getAllByText('Completed')).toHaveLength(2);
        expect(screen.getByText('Failed')).toBeInTheDocument();
      });
    });

    test('displays metadata correctly', async () => {
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('15 sources')).toBeInTheDocument();
        expect(screen.getByText('3 agents')).toBeInTheDocument();
        expect(screen.getByText('4,500 tokens')).toBeInTheDocument();
      });
    });
  });

  describe('Tags and Categories', () => {
    test('displays tags correctly', async () => {
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('AI')).toBeInTheDocument();
        expect(screen.getByText('Technology')).toBeInTheDocument();
        expect(screen.getByText('Climate')).toBeInTheDocument();
        expect(screen.getByText('Agriculture')).toBeInTheDocument();
      });
    });

    test('handles items without tags', async () => {
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('Failed research query')).toBeInTheDocument();
      });
      
      // Should not crash when displaying item without tags
    });
  });

  describe('Error Handling', () => {
    test('handles localStorage errors gracefully', async () => {
      localStorageMock.getItem.mockImplementation(() => {
        throw new Error('localStorage error');
      });
      
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} onLoadHistory={mockOnLoadHistory} />);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load research history')).toBeInTheDocument();
      });
      
      consoleSpy.mockRestore();
    });

    test('handles API errors gracefully', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      mockOnLoadHistory.mockRejectedValue(new Error('API error'));
      
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} onLoadHistory={mockOnLoadHistory} />);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load research history')).toBeInTheDocument();
      });
      
      consoleSpy.mockRestore();
    });

    test('retry functionality works after error', async () => {
      localStorageMock.getItem.mockReturnValue(null);
      mockOnLoadHistory.mockRejectedValueOnce(new Error('API error'))
                      .mockResolvedValueOnce(mockHistoryData);
      
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      const user = userEvent.setup();
      
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} onLoadHistory={mockOnLoadHistory} />);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load research history')).toBeInTheDocument();
      });
      
      const retryButton = screen.getByText('Retry');
      await user.click(retryButton);
      
      expect(mockOnLoadHistory).toHaveBeenCalledTimes(2);
      
      consoleSpy.mockRestore();
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels and semantic structure', async () => {
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      // Check for proper heading structure
      expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument();
      
      // Check for proper button roles
      const buttons = screen.getAllByRole('button');
      expect(buttons.length).toBeGreaterThan(0);
      
      // Check for proper checkbox roles
      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes.length).toBeGreaterThan(0);
    });

    test('keyboard navigation works', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      // Tab through interactive elements
      await user.tab();
      // Should focus on search input
      expect(document.activeElement).toHaveAttribute('placeholder', 'Search research history...');
      
      await user.tab();
      // Should focus on status filter
      expect(document.activeElement.tagName).toBe('SELECT');
    });
  });

  describe('Performance', () => {
    test('handles large history datasets efficiently', async () => {
      const largeDataset = Array.from({ length: 100 }, (_, i) => ({
        id: `large-${i}`,
        query: `Research query ${i}`,
        timestamp: new Date(Date.now() - i * 86400000).toISOString(),
        status: 'completed',
        sources_count: 10,
        duration: 120,
        tokens_used: 3000,
        subagent_count: 2,
        favorite: false,
        tags: ['Test']
      }));
      
      localStorageMock.getItem.mockReturnValue(JSON.stringify(largeDataset));
      
      const startTime = performance.now();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
      
      await waitFor(() => {
        expect(screen.getByText('Research query 0')).toBeInTheDocument();
      }, { timeout: 3000 });
      
      const endTime = performance.now();
      expect(endTime - startTime).toBeLessThan(1000); // Should render within 1 second
    });
  });

  describe('Integration', () => {
    test('integrates with parent component callbacks', async () => {
      const user = userEvent.setup();
      render(<ResearchHistory onSelectQuery={mockOnSelectQuery} onLoadHistory={mockOnLoadHistory} />);
      
      await waitFor(() => {
        expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      });
      
      // Test query selection callback
      const queryButton = screen.getByText('What are the latest developments in AI?');
      await user.click(queryButton);
      
      expect(mockOnSelectQuery).toHaveBeenCalledWith('What are the latest developments in AI?');
      
      // Test load history callback
      expect(mockOnLoadHistory).toHaveBeenCalled();
    });
  });
});