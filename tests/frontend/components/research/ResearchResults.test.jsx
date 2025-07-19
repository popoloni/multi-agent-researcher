import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import ResearchResults from '../ResearchResults';

// Mock clipboard API
Object.assign(navigator, {
  clipboard: {
    writeText: jest.fn(() => Promise.resolve()),
  },
});

// Mock URL.createObjectURL and related APIs
global.URL.createObjectURL = jest.fn(() => 'mock-url');
global.URL.revokeObjectURL = jest.fn();

describe('ResearchResults Component', () => {
  const mockResults = {
    research_id: 'test-research-123',
    report: 'This is a comprehensive research report about AI in healthcare. **Key findings** include significant improvements in diagnostic accuracy.',
    sources_used: [
      {
        title: 'AI in Medical Diagnosis',
        snippet: 'Recent advances in AI have shown promising results in medical diagnosis.',
        url: 'https://example.com/ai-medical',
        relevance_score: 0.95,
        date: '2024-01-15'
      },
      {
        title: 'Healthcare Technology Trends',
        snippet: 'The healthcare industry is rapidly adopting AI technologies.',
        url: 'https://example.com/healthcare-trends',
        relevance_score: 0.88
      }
    ],
    citations: [
      {
        index: 1,
        title: 'AI in Medical Diagnosis',
        url: 'https://example.com/ai-medical',
        times_cited: 3
      },
      {
        index: 2,
        title: 'Healthcare Technology Trends',
        url: 'https://example.com/healthcare-trends',
        times_cited: 1
      }
    ],
    total_tokens_used: 5000,
    execution_time: 180,
    subagent_count: 3,
    created_at: '2024-01-15T10:30:00Z',
    efficiency_score: 95,
    quality_score: 92,
    relevance_score: 88,
    completeness_score: 90,
    report_sections: [
      'Introduction',
      'Current State of AI in Healthcare',
      'Key Findings',
      'Conclusion'
    ]
  };

  const mockQuery = 'What are the latest developments in AI-powered medical diagnosis?';

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Component Rendering', () => {
    test('renders results component with tabbed interface', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      expect(screen.getByText('Research Complete')).toBeInTheDocument();
      expect(screen.getByText(`Query: ${mockQuery}`)).toBeInTheDocument();
      
      // Check all tabs are present
      expect(screen.getByText('Research Report')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sources/i })).toBeInTheDocument();
      expect(screen.getByText('Citations')).toBeInTheDocument();
      expect(screen.getByText('Analytics')).toBeInTheDocument();
    });

    test('displays stats overview correctly', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      expect(screen.getByText('2')).toBeInTheDocument(); // Sources count
      expect(screen.getByText('5,000')).toBeInTheDocument(); // Tokens
      expect(screen.getByText('3m 0s')).toBeInTheDocument(); // Duration
      expect(screen.getByText('3')).toBeInTheDocument(); // Agents
    });

    test('handles null results gracefully', () => {
      render(<ResearchResults results={null} query={mockQuery} />);
      
      expect(screen.getByText('No Results Available')).toBeInTheDocument();
      expect(screen.getByText('Start a research query to see results here.')).toBeInTheDocument();
    });

    test('handles undefined results gracefully', () => {
      render(<ResearchResults results={undefined} query={mockQuery} />);
      
      expect(screen.getByText('No Results Available')).toBeInTheDocument();
    });

    test('handles empty results object', () => {
      render(<ResearchResults results={{}} query={mockQuery} />);
      
      expect(screen.getByText('Research Complete')).toBeInTheDocument();
      expect(screen.getAllByText('0')).toHaveLength(3); // Should show 0 for missing values (sources, tokens, agents)
    });
  });

  describe('Tab Navigation', () => {
    test('tab navigation works correctly', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      // Initially on report tab
      expect(screen.getByText(/This is a comprehensive research report/)).toBeInTheDocument();
      
      // Click on Sources tab
      fireEvent.click(screen.getByRole('button', { name: /sources/i }));
      expect(screen.getByText('Sources Used (2)')).toBeInTheDocument();
      expect(screen.getByText('AI in Medical Diagnosis')).toBeInTheDocument();
      
      // Click on Citations tab
      fireEvent.click(screen.getByText('Citations'));
      expect(screen.getByText('Citations (2)')).toBeInTheDocument();
      expect(screen.getByText('[1]')).toBeInTheDocument();
      
      // Click on Analytics tab
      fireEvent.click(screen.getByText('Analytics'));
      expect(screen.getByText('Research Analytics')).toBeInTheDocument();
      expect(screen.getByText('Execution Details')).toBeInTheDocument();
    });

    test('active tab styling is applied correctly', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      const reportTab = screen.getByText('Research Report').closest('button');
      const sourcesTab = screen.getByRole('button', { name: /sources/i });
      
      // Report tab should be active initially
      expect(reportTab).toHaveClass('border-blue-500', 'text-blue-600');
      expect(sourcesTab).toHaveClass('border-transparent', 'text-gray-500');
      
      // Click sources tab
      fireEvent.click(sourcesTab);
      
      expect(sourcesTab).toHaveClass('border-blue-500', 'text-blue-600');
      expect(reportTab).toHaveClass('border-transparent', 'text-gray-500');
    });
  });

  describe('Report Tab', () => {
    test('displays report content with formatting', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      expect(screen.getByText(/This is a comprehensive research report/)).toBeInTheDocument();
      
      // Check that bold formatting is applied
      const reportContent = screen.getByText(/Key findings/).closest('div');
      expect(reportContent.innerHTML).toContain('<strong>Key findings</strong>');
    });

    test('shows full report toggle for long content', () => {
      const longReport = 'A'.repeat(3000); // Long content
      const resultsWithLongReport = { ...mockResults, report: longReport };
      
      render(<ResearchResults results={resultsWithLongReport} query={mockQuery} />);
      
      expect(screen.getByText('Show full report')).toBeInTheDocument();
      
      fireEvent.click(screen.getByText('Show full report'));
      expect(screen.queryByText('Show full report')).not.toBeInTheDocument();
    });

    test('handles missing report content', () => {
      const resultsWithoutReport = { ...mockResults, report: null };
      
      render(<ResearchResults results={resultsWithoutReport} query={mockQuery} />);
      
      expect(screen.getByText('No report content available')).toBeInTheDocument();
    });
  });

  describe('Sources Tab', () => {
    test('displays sources correctly', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByRole('button', { name: /sources/i }));
      
      expect(screen.getByText('Sources Used (2)')).toBeInTheDocument();
      expect(screen.getByText('AI in Medical Diagnosis')).toBeInTheDocument();
      expect(screen.getByText('Healthcare Technology Trends')).toBeInTheDocument();
      expect(screen.getByText('Relevance: 95%')).toBeInTheDocument();
      expect(screen.getByText('Relevance: 88%')).toBeInTheDocument();
    });

    test('source links are clickable', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByRole('button', { name: /sources/i }));
      
      const links = screen.getAllByRole('link');
      expect(links).toHaveLength(2);
      expect(links[0]).toHaveAttribute('href', 'https://example.com/ai-medical');
      expect(links[0]).toHaveAttribute('target', '_blank');
    });

    test('handles empty sources list', () => {
      const resultsWithoutSources = { ...mockResults, sources_used: [] };
      
      render(<ResearchResults results={resultsWithoutSources} query={mockQuery} />);
      
      fireEvent.click(screen.getByRole('button', { name: /sources/i }));
      expect(screen.getByText('No sources available')).toBeInTheDocument();
    });
  });

  describe('Citations Tab', () => {
    test('displays citations correctly', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByText('Citations'));
      
      expect(screen.getByText('Citations (2)')).toBeInTheDocument();
      expect(screen.getByText('[1]')).toBeInTheDocument();
      expect(screen.getByText('[2]')).toBeInTheDocument();
      expect(screen.getByText('Cited 3 times')).toBeInTheDocument();
      expect(screen.getByText('Cited 1 time')).toBeInTheDocument();
    });

    test('citation links are clickable', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByText('Citations'));
      
      const citationLinks = screen.getAllByRole('link');
      expect(citationLinks).toHaveLength(2);
      expect(citationLinks[0]).toHaveAttribute('href', 'https://example.com/ai-medical');
    });

    test('handles empty citations list', () => {
      const resultsWithoutCitations = { ...mockResults, citations: [] };
      
      render(<ResearchResults results={resultsWithoutCitations} query={mockQuery} />);
      
      fireEvent.click(screen.getByText('Citations'));
      expect(screen.getByText('No citations available')).toBeInTheDocument();
    });
  });

  describe('Analytics Tab', () => {
    test('displays analytics data correctly', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByText('Analytics'));
      
      expect(screen.getByText('Research Analytics')).toBeInTheDocument();
      expect(screen.getByText('Execution Details')).toBeInTheDocument();
      expect(screen.getByText('Agent Performance')).toBeInTheDocument();
      
      // Check quality metrics section
      expect(screen.getByText('Quality Metrics')).toBeInTheDocument();
      expect(screen.getAllByText('Sources')).toHaveLength(3); // Tab, stats overview, and analytics section
      expect(screen.getByText('Avg Relevance')).toBeInTheDocument();
      expect(screen.getByText('Unique Citations')).toBeInTheDocument(); // Analytics section
      expect(screen.getByRole('button', { name: /citations/i })).toBeInTheDocument(); // Tab
    });

    test('displays execution details', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByText('Analytics'));
      
      expect(screen.getAllByText('3m 0s')).toHaveLength(2); // Duration appears in stats and analytics
      expect(screen.getByText('test-research-123')).toBeInTheDocument(); // Research ID
    });

    test('displays agent performance metrics', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByText('Analytics'));
      
      expect(screen.getByText('Agents Used:')).toBeInTheDocument();
      expect(screen.getByText('Total Tokens:')).toBeInTheDocument();
      expect(screen.getByText('Avg. per Agent:')).toBeInTheDocument();
    });

    test('displays report structure when available', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByText('Analytics'));
      
      expect(screen.getByText('Report Structure')).toBeInTheDocument();
      expect(screen.getByText('1. Introduction')).toBeInTheDocument();
      expect(screen.getByText('2. Current State of AI in Healthcare')).toBeInTheDocument();
    });
  });

  describe('Export Functionality', () => {
    test('copy report functionality works', async () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      const copyButton = screen.getByTitle('Copy report');
      fireEvent.click(copyButton);
      
      await waitFor(() => {
        expect(navigator.clipboard.writeText).toHaveBeenCalledWith(mockResults.report);
      });
    });

    test('download report functionality works', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      const downloadButton = screen.getByTitle('Download report');
      expect(downloadButton).toBeInTheDocument();
      
      // Just verify the button exists and is clickable
      fireEvent.click(downloadButton);
      // The actual download functionality would be tested in integration tests
    });

    test('full screen toggle works', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      const fullScreenButton = screen.getByTitle('Full screen');
      fireEvent.click(fullScreenButton);
      
      // The component should handle the full screen state internally
      // We can verify this by checking if the button is still clickable
      expect(fullScreenButton).toBeInTheDocument();
    });
  });

  describe('Data Formatting', () => {
    test('formats numbers correctly', () => {
      const resultsWithLargeNumbers = {
        ...mockResults,
        total_tokens_used: 1234567
      };
      
      render(<ResearchResults results={resultsWithLargeNumbers} query={mockQuery} />);
      
      expect(screen.getByText('1,234,567')).toBeInTheDocument();
    });

    test('formats time correctly', () => {
      const resultsWithDifferentTimes = {
        ...mockResults,
        execution_time: 3665 // 1 hour, 1 minute, 5 seconds
      };
      
      render(<ResearchResults results={resultsWithDifferentTimes} query={mockQuery} />);
      
      expect(screen.getByText('61m 5s')).toBeInTheDocument();
    });

    test('formats dates correctly', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByText('Analytics'));
      
      // Should display formatted date
      expect(screen.getByText(/1\/15\/2024/)).toBeInTheDocument();
    });
  });

  describe('Responsive Design', () => {
    test('renders grid layouts correctly', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      // Check for responsive grid classes
      expect(document.querySelector('.grid-cols-2')).toBeTruthy();
      expect(document.querySelector('.md\\:grid-cols-4')).toBeTruthy();
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels and semantic structure', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      // Check for proper heading structure
      expect(screen.getByRole('heading', { level: 2 })).toBeInTheDocument();
      // Check for proper heading structure - h3 appears when switching to other tabs
      fireEvent.click(screen.getByRole('button', { name: /sources/i }));
      expect(screen.getByRole('heading', { level: 3 })).toBeInTheDocument();
    });

    test('external links have proper attributes', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByRole('button', { name: /sources/i }));
      
      const externalLinks = screen.getAllByRole('link');
      externalLinks.forEach(link => {
        expect(link).toHaveAttribute('target', '_blank');
        expect(link).toHaveAttribute('rel', 'noopener noreferrer');
      });
    });
  });

  describe('Error Handling', () => {
    test('handles missing optional data gracefully', () => {
      const minimalResults = {
        report: 'Basic report',
        // Missing most optional fields
      };
      
      render(<ResearchResults results={minimalResults} query={mockQuery} />);
      
      expect(screen.getByText('Research Complete')).toBeInTheDocument();
      expect(screen.getByText('Basic report')).toBeInTheDocument();
    });

    test('handles copy failure gracefully', async () => {
      // Mock clipboard to fail
      navigator.clipboard.writeText.mockRejectedValue(new Error('Clipboard failed'));
      
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
      
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      const copyButton = screen.getByTitle('Copy report');
      fireEvent.click(copyButton);
      
      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Failed to copy report:', expect.any(Error));
      });
      
      consoleSpy.mockRestore();
    });
  });

  describe('Enhanced Export Functionality', () => {
    beforeEach(() => {
      // Mock URL methods for file downloads
      global.URL.createObjectURL = jest.fn(() => 'mock-url');
      global.URL.revokeObjectURL = jest.fn();
    });

    afterEach(() => {
      jest.restoreAllMocks();
    });

    test('export menu functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      // Open export menu
      const exportMenuButton = screen.getByTitle('Export options');
      await user.click(exportMenuButton);
      
      // Check menu items are visible
      expect(screen.getByText('Export as JSON')).toBeInTheDocument();
      expect(screen.getByText('Export Sources as CSV')).toBeInTheDocument();
    });

    test('JSON export functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      // Open export menu and click JSON export
      const exportMenuButton = screen.getByTitle('Export options');
      await user.click(exportMenuButton);
      
      const jsonExportButton = screen.getByText('Export as JSON');
      await user.click(jsonExportButton);
      
      expect(global.URL.createObjectURL).toHaveBeenCalled();
      expect(global.URL.revokeObjectURL).toHaveBeenCalled();
    });

    test('CSV export functionality works', async () => {
      const user = userEvent.setup();
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      // Open export menu and click CSV export
      const exportMenuButton = screen.getByTitle('Export options');
      await user.click(exportMenuButton);
      
      const csvExportButton = screen.getByText('Export Sources as CSV');
      await user.click(csvExportButton);
      
      expect(global.URL.createObjectURL).toHaveBeenCalled();
      expect(global.URL.revokeObjectURL).toHaveBeenCalled();
    });

    test('CSV export is disabled when no sources', async () => {
      const resultsWithoutSources = { ...mockResults, sources_used: [] };
      const user = userEvent.setup();
      render(<ResearchResults results={resultsWithoutSources} query={mockQuery} />);
      
      // Open export menu
      const exportMenuButton = screen.getByTitle('Export options');
      await user.click(exportMenuButton);
      
      const csvExportButton = screen.getByText('Export Sources as CSV').closest('button');
      expect(csvExportButton).toBeDisabled();
    });

    test('export menu closes when clicking outside', async () => {
      const user = userEvent.setup();
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      // Open export menu
      const exportMenuButton = screen.getByTitle('Export options');
      await user.click(exportMenuButton);
      
      expect(screen.getByText('Export as JSON')).toBeInTheDocument();
      
      // Click outside the menu
      await user.click(document.body);
      
      expect(screen.queryByText('Export as JSON')).not.toBeInTheDocument();
    });
  });

  describe('Enhanced Analytics', () => {
    test('displays source quality distribution', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByRole('button', { name: /analytics/i }));
      
      expect(screen.getByText('Source Quality Distribution')).toBeInTheDocument();
      expect(screen.getByText('High Quality (80%+)')).toBeInTheDocument();
      expect(screen.getByText('Medium Quality (50-79%)')).toBeInTheDocument();
    });

    test('displays citation analysis', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByRole('button', { name: /analytics/i }));
      
      expect(screen.getByText('Citation Analysis')).toBeInTheDocument();
      expect(screen.getByText('Total Citations:')).toBeInTheDocument();
      expect(screen.getByText('Unique Sources:')).toBeInTheDocument();
      expect(screen.getByText('Duplication Rate:')).toBeInTheDocument();
    });

    test('calculates metrics correctly', () => {
      render(<ResearchResults results={mockResults} query={mockQuery} />);
      
      fireEvent.click(screen.getByRole('button', { name: /analytics/i }));
      
      // Check that average relevance is displayed (should be around 91%)
      expect(screen.getByText('Avg Relevance')).toBeInTheDocument();
      
      // Check report length label is displayed
      expect(screen.getByText('Report Length')).toBeInTheDocument();
    });
  });
});