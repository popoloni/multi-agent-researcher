/**
 * Frontend component test template for React components.
 * 
 * This template provides a standard structure for frontend tests that:
 * - Test component rendering and user interactions
 * - Use React Testing Library for component testing
 * - Follow consistent naming and organization patterns
 * - Include proper setup, execution, and assertion patterns
 * 
 * Usage:
 * 1. Copy this template to tests/frontend/test_<Component>.<functionality>.test.jsx
 * 2. Replace placeholder content with actual component test logic
 * 3. Follow the naming conventions and patterns established here
 */

import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';

// Import the component being tested
// import ExampleComponent from '../../src/components/ExampleComponent';

// Mock external dependencies
jest.mock('../../src/services/api', () => ({
  fetchData: jest.fn(),
  postData: jest.fn(),
}));

// Test utilities
const renderWithProviders = (component, options = {}) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {component}
      </BrowserRouter>
    </QueryClientProvider>,
    options
  );
};

const renderWithRouter = (component, options = {}) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>,
    options
  );
};

describe('ExampleComponent', () => {
  // Setup and teardown
  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterEach(() => {
    jest.resetAllMocks();
  });

  describe('Rendering', () => {
    test('renders component with default props', () => {
      // Arrange
      const defaultProps = {
        title: 'Test Title',
        description: 'Test Description',
      };

      // Act
      renderWithProviders(<ExampleComponent {...defaultProps} />);

      // Assert
      expect(screen.getByText('Test Title')).toBeInTheDocument();
      expect(screen.getByText('Test Description')).toBeInTheDocument();
    });

    test('renders loading state when data is loading', () => {
      // Arrange
      const props = {
        isLoading: true,
        title: 'Test Title',
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);

      // Assert
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
      expect(screen.queryByText('Test Title')).not.toBeInTheDocument();
    });

    test('renders error state when there is an error', () => {
      // Arrange
      const props = {
        error: 'Something went wrong',
        title: 'Test Title',
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);

      // Assert
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByTestId('error-message')).toBeInTheDocument();
    });

    test('renders empty state when no data is available', () => {
      // Arrange
      const props = {
        items: [],
        title: 'Test Title',
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);

      // Assert
      expect(screen.getByText('No items found')).toBeInTheDocument();
      expect(screen.getByTestId('empty-state')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    test('handles button click correctly', async () => {
      // Arrange
      const mockOnClick = jest.fn();
      const props = {
        title: 'Test Title',
        onButtonClick: mockOnClick,
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);
      const button = screen.getByRole('button', { name: /click me/i });
      await userEvent.click(button);

      // Assert
      expect(mockOnClick).toHaveBeenCalledTimes(1);
    });

    test('handles form submission correctly', async () => {
      // Arrange
      const mockOnSubmit = jest.fn();
      const props = {
        onSubmit: mockOnSubmit,
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);
      
      const nameInput = screen.getByLabelText(/name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      await userEvent.type(nameInput, 'John Doe');
      await userEvent.type(emailInput, 'john@example.com');
      await userEvent.click(submitButton);

      // Assert
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: 'John Doe',
        email: 'john@example.com',
      });
    });

    test('handles input changes correctly', async () => {
      // Arrange
      const mockOnChange = jest.fn();
      const props = {
        onChange: mockOnChange,
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);
      
      const input = screen.getByLabelText(/search/i);
      await userEvent.type(input, 'test search');

      // Assert
      expect(input).toHaveValue('test search');
      expect(mockOnChange).toHaveBeenCalledWith('test search');
    });

    test('handles keyboard navigation', async () => {
      // Arrange
      const props = {
        items: ['Item 1', 'Item 2', 'Item 3'],
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);
      
      const list = screen.getByRole('list');
      const firstItem = screen.getByText('Item 1');
      
      firstItem.focus();
      fireEvent.keyDown(firstItem, { key: 'ArrowDown' });

      // Assert
      expect(screen.getByText('Item 2')).toHaveFocus();
    });
  });

  describe('API Integration', () => {
    test('fetches data on component mount', async () => {
      // Arrange
      const mockData = [{ id: 1, name: 'Test Item' }];
      const { fetchData } = require('../../src/services/api');
      fetchData.mockResolvedValue(mockData);

      // Act
      renderWithProviders(<ExampleComponent />);

      // Assert
      await waitFor(() => {
        expect(fetchData).toHaveBeenCalledTimes(1);
        expect(screen.getByText('Test Item')).toBeInTheDocument();
      });
    });

    test('handles API error gracefully', async () => {
      // Arrange
      const { fetchData } = require('../../src/services/api');
      fetchData.mockRejectedValue(new Error('API Error'));

      // Act
      renderWithProviders(<ExampleComponent />);

      // Assert
      await waitFor(() => {
        expect(screen.getByText(/error/i)).toBeInTheDocument();
        expect(screen.getByText(/api error/i)).toBeInTheDocument();
      });
    });

    test('submits form data to API', async () => {
      // Arrange
      const mockResponse = { success: true, id: 123 };
      const { postData } = require('../../src/services/api');
      postData.mockResolvedValue(mockResponse);

      const mockOnSuccess = jest.fn();
      const props = {
        onSuccess: mockOnSuccess,
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);
      
      const form = screen.getByRole('form');
      const nameInput = screen.getByLabelText(/name/i);
      const emailInput = screen.getByLabelText(/email/i);
      const submitButton = screen.getByRole('button', { name: /submit/i });

      await userEvent.type(nameInput, 'John Doe');
      await userEvent.type(emailInput, 'john@example.com');
      await userEvent.click(submitButton);

      // Assert
      await waitFor(() => {
        expect(postData).toHaveBeenCalledWith({
          name: 'John Doe',
          email: 'john@example.com',
        });
        expect(mockOnSuccess).toHaveBeenCalledWith(mockResponse);
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels', () => {
      // Arrange & Act
      renderWithProviders(<ExampleComponent />);

      // Assert
      expect(screen.getByLabelText(/search/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/name/i)).toBeInTheDocument();
      expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    });

    test('supports keyboard navigation', async () => {
      // Arrange
      const props = {
        items: ['Item 1', 'Item 2', 'Item 3'],
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);
      
      const list = screen.getByRole('list');
      const firstItem = screen.getByText('Item 1');
      
      firstItem.focus();
      fireEvent.keyDown(firstItem, { key: 'ArrowDown' });

      // Assert
      expect(screen.getByText('Item 2')).toHaveFocus();
    });

    test('has proper focus management', async () => {
      // Arrange
      const props = {
        onClose: jest.fn(),
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);
      
      const closeButton = screen.getByRole('button', { name: /close/i });
      closeButton.focus();
      fireEvent.keyDown(closeButton, { key: 'Enter' });

      // Assert
      expect(props.onClose).toHaveBeenCalled();
    });
  });

  describe('Edge Cases', () => {
    test('handles very long text content', () => {
      // Arrange
      const longText = 'A'.repeat(1000);
      const props = {
        content: longText,
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);

      // Assert
      expect(screen.getByText(longText)).toBeInTheDocument();
    });

    test('handles special characters in input', async () => {
      // Arrange
      const specialChars = '!@#$%^&*()_+-=[]{}|;:,.<>?';
      const mockOnChange = jest.fn();
      const props = {
        onChange: mockOnChange,
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);
      
      const input = screen.getByLabelText(/search/i);
      await userEvent.type(input, specialChars);

      // Assert
      expect(input).toHaveValue(specialChars);
      expect(mockOnChange).toHaveBeenCalledWith(specialChars);
    });

    test('handles rapid user interactions', async () => {
      // Arrange
      const mockOnClick = jest.fn();
      const props = {
        onButtonClick: mockOnClick,
      };

      // Act
      renderWithProviders(<ExampleComponent {...props} />);
      
      const button = screen.getByRole('button', { name: /click me/i });
      
      // Rapid clicks
      await userEvent.click(button);
      await userEvent.click(button);
      await userEvent.click(button);

      // Assert
      expect(mockOnClick).toHaveBeenCalledTimes(3);
    });
  });

  describe('Performance', () => {
    test('renders large lists efficiently', () => {
      // Arrange
      const largeList = Array.from({ length: 1000 }, (_, i) => `Item ${i}`);
      const props = {
        items: largeList,
      };

      // Act
      const startTime = performance.now();
      renderWithProviders(<ExampleComponent {...props} />);
      const endTime = performance.now();

      // Assert
      expect(endTime - startTime).toBeLessThan(100); // Should render in less than 100ms
      expect(screen.getByText('Item 999')).toBeInTheDocument();
    });
  });
});

// Integration test examples (for reference)
describe('ExampleComponent Integration', () => {
  test('integrates with parent component correctly', () => {
    // Arrange
    const mockParentCallback = jest.fn();
    const props = {
      onDataChange: mockParentCallback,
    };

    // Act
    renderWithProviders(<ExampleComponent {...props} />);
    
    const input = screen.getByLabelText(/search/i);
    fireEvent.change(input, { target: { value: 'test' } });

    // Assert
    expect(mockParentCallback).toHaveBeenCalledWith('test');
  });
});

// Snapshot test examples (for reference)
describe('ExampleComponent Snapshots', () => {
  test('matches snapshot with default props', () => {
    // Arrange & Act
    const { container } = renderWithProviders(<ExampleComponent />);

    // Assert
    expect(container).toMatchSnapshot();
  });

  test('matches snapshot with loading state', () => {
    // Arrange & Act
    const { container } = renderWithProviders(
      <ExampleComponent isLoading={true} />
    );

    // Assert
    expect(container).toMatchSnapshot();
  });
}); 