import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import CodeBlock from '../CodeBlock';
import SourceReference from '../SourceReference';

// Mock the chat service
jest.mock('../../../services/chat', () => ({
  chatService: {
    getRepositoryContext: jest.fn(),
    getChatHistory: jest.fn(),
    createChatSession: jest.fn(),
    clearChatHistory: jest.fn(),
  }
}));

describe('Enhanced Chat Components', () => {
  describe('CodeBlock', () => {
    test('renders code block component', () => {
      const code = 'function hello() {\n  console.log("Hello, World!");\n}';
      render(<CodeBlock code={code} language="javascript" />);
      
      expect(screen.getByText('javascript')).toBeInTheDocument();
    });

    test('shows copy button', () => {
      const code = 'const x = 42;';
      
      // Mock clipboard API
      Object.assign(navigator, {
        clipboard: {
          writeText: jest.fn().mockImplementation(() => Promise.resolve()),
        },
      });

      render(<CodeBlock code={code} language="javascript" />);
      
      const copyButton = screen.getByTitle('Copy code');
      expect(copyButton).toBeInTheDocument();
    });

    test('displays filename when provided', () => {
      const code = 'print("Hello")';
      render(<CodeBlock code={code} fileName="hello.py" />);
      
      expect(screen.getByText('hello.py')).toBeInTheDocument();
    });
  });

  describe('SourceReference', () => {
    const mockSources = [
      {
        file_path: '/src/components/Button.jsx',
        line_number: 15,
        source_type: 'code',
        relevance: 'high'
      }
    ];

    test('renders source references', () => {
      render(<SourceReference sources={mockSources} onViewSource={jest.fn()} />);
      
      expect(screen.getByText('1 source')).toBeInTheDocument();
    });

    test('returns null when no sources provided', () => {
      const { container } = render(<SourceReference sources={[]} onViewSource={jest.fn()} />);
      expect(container.firstChild).toBeNull();
    });
  });
});