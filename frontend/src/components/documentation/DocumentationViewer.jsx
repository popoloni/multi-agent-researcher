import React, { useState, useEffect, useRef } from 'react';
import { Printer, Download, Copy, Search, ChevronDown, ChevronUp, X } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

const DocumentationViewer = ({ 
  content, 
  title, 
  docType = 'overview',
  isLoading = false,
  onPrint,
  onDownload
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [showToc, setShowToc] = useState(true);
  const [toc, setToc] = useState([]);
  const [searchResults, setSearchResults] = useState([]);
  const [currentMatchIndex, setCurrentMatchIndex] = useState(0);
  const [highlightedContent, setHighlightedContent] = useState('');
  const contentRef = useRef(null);

  // Use highlighted content or original content
  const displayContent = highlightedContent || content;

  // Extract table of contents from markdown content
  useEffect(() => {
    if (content) {
      const headingRegex = /^(#{1,3})\s+(.+)$/gm;
      const matches = [...content.matchAll(headingRegex)];
      
      const extractedToc = matches.map((match, index) => {
        const level = match[1].length;
        const text = match[2];
        const id = (text || '').toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-');
        
        return { id, text, level, index };
      });
      
      setToc(extractedToc);
    }
  }, [content]);

  // Perform client-side search
  const performSearch = (term) => {
    if (!term || !content) {
      setSearchResults([]);
      setHighlightedContent('');
      setCurrentMatchIndex(0);
      return;
    }

    // Find all matches (case-insensitive)
    const regex = new RegExp(term.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'), 'gi');
    const matches = [...content.matchAll(regex)];
    
    if (matches.length === 0) {
      setSearchResults([]);
      setHighlightedContent('');
      setCurrentMatchIndex(0);
      return;
    }

    // Create search results with context
    const results = matches.map((match, index) => {
      const start = Math.max(0, match.index - 50);
      const end = Math.min(content.length, match.index + match[0].length + 50);
      const context = content.slice(start, end);
      
      return {
        index,
        match: match[0],
        position: match.index,
        context: context,
        beforeMatch: content.slice(start, match.index),
        afterMatch: content.slice(match.index + match[0].length, end)
      };
    });

    setSearchResults(results);
    setCurrentMatchIndex(0);

    // Highlight matches in content
    let highlightedText = content;
    let offset = 0;
    
    matches.forEach((match, index) => {
      const position = match.index + offset;
      const beforeMatch = highlightedText.slice(0, position);
      const matchText = match[0];
      const afterMatch = highlightedText.slice(position + matchText.length);
      
      const highlightedMatch = `<mark class="bg-yellow-200 px-1 rounded" id="search-match-${index}">${matchText}</mark>`;
      highlightedText = beforeMatch + highlightedMatch + afterMatch;
      offset += highlightedMatch.length - matchText.length;
    });

    setHighlightedContent(highlightedText);
    
    // Scroll to first match
    setTimeout(() => {
      const firstMatch = document.getElementById('search-match-0');
      if (firstMatch) {
        firstMatch.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }, 100);
  };

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    performSearch(searchTerm);
  };

  // Clear search
  const clearSearch = () => {
    setSearchTerm('');
    setSearchResults([]);
    setHighlightedContent('');
    setCurrentMatchIndex(0);
  };

  // Navigate to next/previous match
  const navigateMatch = (direction) => {
    if (searchResults.length === 0) return;
    
    let newIndex;
    if (direction === 'next') {
      newIndex = (currentMatchIndex + 1) % searchResults.length;
    } else {
      newIndex = currentMatchIndex === 0 ? searchResults.length - 1 : currentMatchIndex - 1;
    }
    
    setCurrentMatchIndex(newIndex);
    
    const matchElement = document.getElementById(`search-match-${newIndex}`);
    if (matchElement) {
      matchElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };

  // Handle print
  const handlePrint = () => {
    if (onPrint) {
      onPrint();
    } else {
      window.print();
    }
  };

  // Handle download
  const handleDownload = () => {
    if (onDownload) {
      onDownload();
    } else {
      const element = document.createElement('a');
      const file = new Blob([content], { type: 'text/markdown' });
      element.href = URL.createObjectURL(file);
      element.download = `${title || 'documentation'}.md`;
      document.body.appendChild(element);
      element.click();
      document.body.removeChild(element);
    }
  };

  // Handle copy to clipboard
  const handleCopy = () => {
    navigator.clipboard.writeText(content);
  };

  // Scroll to heading
  const scrollToHeading = (id) => {
    const element = document.getElementById(id);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Custom components for ReactMarkdown
  const components = {
    h1: ({ node, ...props }) => {
      const id = (props.children?.[0] || '').toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-');
      return <h1 id={id} className="text-3xl font-bold mt-8 mb-4 pb-2 border-b border-gray-200" {...props} />;
    },
    h2: ({ node, ...props }) => {
      const id = (props.children?.[0] || '').toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-');
      return <h2 id={id} className="text-2xl font-bold mt-6 mb-3" {...props} />;
    },
    h3: ({ node, ...props }) => {
      const id = (props.children?.[0] || '').toLowerCase().replace(/[^\w\s]/g, '').replace(/\s+/g, '-');
      return <h3 id={id} className="text-xl font-semibold mt-4 mb-2" {...props} />;
    },
    code: ({ node, inline, className, children, ...props }) => {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <SyntaxHighlighter
          style={vscDarkPlus}
          language={match[1]}
          PreTag="div"
          className="rounded-md my-4"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className="bg-gray-100 px-1 py-0.5 rounded text-red-600 font-mono text-sm" {...props}>
          {children}
        </code>
      );
    },
    table: ({ node, ...props }) => (
      <div className="overflow-x-auto my-4">
        <table className="min-w-full divide-y divide-gray-300 border border-gray-300" {...props} />
      </div>
    ),
    thead: ({ node, ...props }) => <thead className="bg-gray-50" {...props} />,
    th: ({ node, ...props }) => <th className="px-3 py-2 text-left text-sm font-semibold text-gray-900 border-b" {...props} />,
    td: ({ node, ...props }) => <td className="px-3 py-2 text-sm text-gray-500 border-b border-gray-200" {...props} />,
    a: ({ node, ...props }) => <a className="text-primary-600 hover:text-primary-800 hover:underline" {...props} />,
    ul: ({ node, ...props }) => <ul className="list-disc pl-6 my-4 space-y-2" {...props} />,
    ol: ({ node, ...props }) => <ol className="list-decimal pl-6 my-4 space-y-2" {...props} />,
    li: ({ node, ...props }) => <li className="pl-1" {...props} />,
    blockquote: ({ node, ...props }) => (
      <blockquote className="border-l-4 border-gray-300 pl-4 py-1 my-4 text-gray-700 italic" {...props} />
    ),
    hr: ({ node, ...props }) => <hr className="my-6 border-gray-300" {...props} />,
  };

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow p-6 min-h-[400px] flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        <span className="ml-3 text-gray-600">Loading documentation...</span>
      </div>
    );
  }

  if (!content) {
    return (
      <div className="bg-white rounded-lg shadow p-6 min-h-[400px] flex flex-col items-center justify-center">
        <div className="text-gray-400 mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-700">No documentation available</h3>
        <p className="text-gray-500 mt-2 text-center">
          Documentation for this repository has not been generated yet.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow">
      {/* Documentation Header */}
      <div className="border-b border-gray-200 px-6 py-4 flex justify-between items-center">
        <div>
          <h2 className="text-xl font-bold text-gray-800">{title || 'Documentation'}</h2>
          <div className="text-sm text-gray-500 mt-1">
            {docType === 'overview' && 'Repository Overview'}
            {docType === 'api' && 'API Documentation'}
            {docType === 'architecture' && 'Architecture Documentation'}
            {docType === 'usage' && 'Usage Guide'}
          </div>
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={handlePrint}
            className="text-gray-600 hover:text-gray-800 p-2 rounded-full hover:bg-gray-100"
            title="Print documentation"
          >
            <Printer className="w-5 h-5" />
          </button>
          <button 
            onClick={handleDownload}
            className="text-gray-600 hover:text-gray-800 p-2 rounded-full hover:bg-gray-100"
            title="Download as Markdown"
          >
            <Download className="w-5 h-5" />
          </button>
          <button 
            onClick={handleCopy}
            className="text-gray-600 hover:text-gray-800 p-2 rounded-full hover:bg-gray-100"
            title="Copy to clipboard"
          >
            <Copy className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Search Bar */}
      <div className="border-b border-gray-200 px-6 py-3">
        <form onSubmit={handleSearch} className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search in documentation..."
            className="w-full pl-10 pr-32 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          
          {/* Search Controls */}
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2 flex items-center space-x-1">
            {searchResults.length > 0 && (
              <>
                <span className="text-xs text-gray-500">
                  {currentMatchIndex + 1} of {searchResults.length}
                </span>
                <button
                  type="button"
                  onClick={() => navigateMatch('previous')}
                  className="p-1 text-gray-400 hover:text-gray-600"
                  title="Previous match"
                >
                  <ChevronUp className="w-3 h-3" />
                </button>
                <button
                  type="button"
                  onClick={() => navigateMatch('next')}
                  className="p-1 text-gray-400 hover:text-gray-600"
                  title="Next match"
                >
                  <ChevronDown className="w-3 h-3" />
                </button>
              </>
            )}
            
            {searchTerm && (
              <button
                type="button"
                onClick={clearSearch}
                className="p-1 text-gray-400 hover:text-gray-600"
                title="Clear search"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>
        </form>
        
        {/* Search Results Summary */}
        {searchTerm && (
          <div className="mt-2 text-sm text-gray-500">
            {searchResults.length > 0 ? (
              <>Found {searchResults.length} {searchResults.length === 1 ? 'match' : 'matches'} for "{searchTerm}"</>
            ) : (
              <>No matches found for "{searchTerm}"</>
            )}
          </div>
        )}
      </div>

      <div className="flex flex-col md:flex-row">
        {/* Table of Contents */}
        {toc.length > 0 && (
          <div className="w-full md:w-64 border-b md:border-b-0 md:border-r border-gray-200 p-4">
            <div className="flex justify-between items-center mb-3">
              <h3 className="font-medium text-gray-700">Table of Contents</h3>
              <button 
                onClick={() => setShowToc(!showToc)}
                className="text-gray-500 hover:text-gray-700"
              >
                {showToc ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
              </button>
            </div>
            
            {showToc && (
              <nav className="space-y-1 max-h-[400px] overflow-y-auto">
                {toc.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToHeading(item.id)}
                    className={`block w-full text-left px-2 py-1 rounded hover:bg-gray-100 text-sm ${
                      item.level === 1 ? 'font-medium' : 'pl-4'
                    } ${item.level === 3 ? 'pl-6 text-xs' : ''}`}
                  >
                    {item.text}
                  </button>
                ))}
              </nav>
            )}
          </div>
        )}

        {/* Documentation Content */}
        <div 
          ref={contentRef}
          className="flex-1 p-6 overflow-auto prose prose-sm md:prose max-w-none"
        >
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            rehypePlugins={[rehypeRaw]}
            components={components}
          >
            {displayContent}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default DocumentationViewer;