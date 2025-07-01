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
  }
];

describe('ResearchHistory Component - Core Functionality', () => {
  const mockOnSelectQuery = jest.fn();
  const mockOnLoadHistory = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(JSON.stringify(mockHistoryData));
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders history component with header', async () => {
    render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
    
    expect(screen.getByText('Research History')).toBeInTheDocument();
    expect(screen.getByTitle('Refresh history')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
    });
  });

  test('displays history items when loaded', async () => {
    render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
    
    await waitFor(() => {
      expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
      expect(screen.getByText('Climate change impact on agriculture')).toBeInTheDocument();
    });
  });

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
      expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
    });
    
    const statusFilter = screen.getByDisplayValue('All Status');
    await user.selectOptions(statusFilter, 'completed');
    
    // Both items should still be visible since they're both completed
    expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
    expect(screen.getByText('Climate change impact on agriculture')).toBeInTheDocument();
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

  test('displays empty state when no history', async () => {
    localStorageMock.getItem.mockReturnValue(null);
    
    render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
    
    await waitFor(() => {
      expect(screen.getByText('No Research History')).toBeInTheDocument();
      expect(screen.getByText('Start your first research query to see results here.')).toBeInTheDocument();
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

  test('displays tags correctly', async () => {
    render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
    
    await waitFor(() => {
      expect(screen.getByText('AI')).toBeInTheDocument();
      expect(screen.getByText('Technology')).toBeInTheDocument();
      expect(screen.getByText('Climate')).toBeInTheDocument();
      expect(screen.getByText('Agriculture')).toBeInTheDocument();
    });
  });

  test('displays status badges correctly', async () => {
    render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
    
    await waitFor(() => {
      expect(screen.getAllByText('Completed')).toHaveLength(2);
    });
  });

  test('bulk selection works', async () => {
    const user = userEvent.setup();
    render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
    
    await waitFor(() => {
      expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
    });
    
    const selectAllButton = screen.getByText('Select All');
    await user.click(selectAllButton);
    
    expect(screen.getByText('2 selected')).toBeInTheDocument();
    expect(screen.getByText('Delete Selected')).toBeInTheDocument();
  });

  test('sorting functionality works', async () => {
    const user = userEvent.setup();
    render(<ResearchHistory onSelectQuery={mockOnSelectQuery} />);
    
    await waitFor(() => {
      expect(screen.getByText('What are the latest developments in AI?')).toBeInTheDocument();
    });
    
    const sortSelect = screen.getByDisplayValue('Newest First');
    await user.selectOptions(sortSelect, 'duration-desc');
    
    expect(screen.getByDisplayValue('Longest Duration')).toBeInTheDocument();
  });

  test('refresh functionality works', async () => {
    const user = userEvent.setup();
    render(<ResearchHistory onSelectQuery={mockOnSelectQuery} onLoadHistory={mockOnLoadHistory} />);
    
    const refreshButton = screen.getByTitle('Refresh history');
    await user.click(refreshButton);
    
    expect(mockOnLoadHistory).toHaveBeenCalled();
  });

  test('handles component integration', async () => {
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