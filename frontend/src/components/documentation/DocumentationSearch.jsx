import React, { useState, useEffect } from 'react';
import { Search, X, FileText, Code, Box, BookOpen } from 'lucide-react';
import { documentationService } from '../../services/documentation';

const DocumentationSearch = ({ 
  repository, 
  onResultClick,
  initialQuery = ''
}) => {
  const [searchQuery, setSearchQuery] = useState(initialQuery);
  const [searchResults, setSearchResults] = useState([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState(null);
  const [selectedDocType, setSelectedDocType] = useState('all');
  const [searchHistory, setSearchHistory] = useState([]);

  // Document type filter options
  const docTypes = [
    { id: 'all', name: 'All', icon: <FileText className="w-4 h-4" /> },
    { id: 'overview', name: 'Overview', icon: <FileText className="w-4 h-4" /> },
    { id: 'api', name: 'API', icon: <Code className="w-4 h-4" /> },
    { id: 'architecture', name: 'Architecture', icon: <Box className="w-4 h-4" /> },
    { id: 'usage', name: 'Usage', icon: <BookOpen className="w-4 h-4" /> }
  ];

  // Load search history from localStorage
  useEffect(() => {
    const history = localStorage.getItem('docSearchHistory');
    if (history) {
      try {
        setSearchHistory(JSON.parse(history));
      } catch (e) {
        console.error('Error parsing search history:', e);
      }
    }
  }, []);

  // Save search history to localStorage
  const saveSearchHistory = (query) => {
    if (!query || query.trim() === '') return;
    
    const newHistory = [
      query,
      ...searchHistory.filter(item => item !== query).slice(0, 9)
    ];
    
    setSearchHistory(newHistory);
    localStorage.setItem('docSearchHistory', JSON.stringify(newHistory));
  };

  // Handle search submission
  const handleSearch = async (e) => {
    if (e) e.preventDefault();
    if (!repository || !repository.id || !searchQuery.trim()) return;
    
    setIsSearching(true);
    setError(null);
    
    try {
      const response = await documentationService.searchDocumentation(
        repository.id, 
        searchQuery
      );
      
      setSearchResults(response.data.results || []);
      saveSearchHistory(searchQuery);
    } catch (err) {
      console.error('Error searching documentation:', err);
      setError(err.message || 'Failed to search documentation');
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  // Clear search
  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
  };

  // Filter results by doc type
  const filteredResults = selectedDocType === 'all'
    ? searchResults
    : searchResults.filter(result => result.doc_type === selectedDocType);

  // Handle result click
  const handleResultClick = (result) => {
    if (onResultClick) {
      onResultClick(result);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-lg font-bold text-gray-800">Documentation Search</h2>
        <p className="text-sm text-gray-500 mt-1">
          Search across all documentation for this repository
        </p>
      </div>

      {/* Search Form */}
      <div className="px-6 py-4 border-b border-gray-200">
        <form onSubmit={handleSearch} className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search in documentation..."
            className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
          {searchQuery && (
            <button
              type="button"
              onClick={clearSearch}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </form>

        {/* Search History */}
        {searchHistory.length > 0 && !searchResults.length && (
          <div className="mt-3">
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
              Recent Searches
            </h3>
            <div className="flex flex-wrap gap-2">
              {searchHistory.map((query, index) => (
                <button
                  key={index}
                  onClick={() => {
                    setSearchQuery(query);
                    handleSearch();
                  }}
                  className="px-3 py-1 bg-gray-100 hover:bg-gray-200 rounded-full text-sm text-gray-700"
                >
                  {query}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Filters */}
      {searchResults.length > 0 && (
        <div className="px-6 py-3 border-b border-gray-200 bg-gray-50">
          <div className="flex items-center justify-between">
            <div className="text-sm text-gray-500">
              {filteredResults.length} {filteredResults.length === 1 ? 'result' : 'results'} found
            </div>
            <div className="flex space-x-2">
              {docTypes.map((type) => (
                <button
                  key={type.id}
                  onClick={() => setSelectedDocType(type.id)}
                  className={`flex items-center px-2 py-1 rounded text-xs ${
                    selectedDocType === type.id
                      ? 'bg-primary-100 text-primary-700 font-medium'
                      : 'text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <span className="mr-1">{type.icon}</span>
                  {type.name}
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Search Results */}
      <div className="divide-y divide-gray-200">
        {isSearching ? (
          <div className="px-6 py-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500 mx-auto"></div>
            <p className="mt-2 text-gray-600">Searching...</p>
          </div>
        ) : error ? (
          <div className="px-6 py-8 text-center">
            <div className="text-red-500 mb-2">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-700">Search Error</h3>
            <p className="text-gray-500 mt-1">{error}</p>
          </div>
        ) : filteredResults.length === 0 ? (
          searchQuery && !isSearching ? (
            <div className="px-6 py-8 text-center">
              <div className="text-gray-400 mb-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-700">No Results Found</h3>
              <p className="text-gray-500 mt-1">
                No documentation matches your search query.
              </p>
            </div>
          ) : null
        ) : (
          filteredResults.map((result, index) => (
            <div 
              key={index}
              className="px-6 py-4 hover:bg-gray-50 cursor-pointer"
              onClick={() => handleResultClick(result)}
            >
              <div className="flex items-start">
                <div className="flex-shrink-0 mt-1">
                  {result.doc_type === 'overview' && <FileText className="w-5 h-5 text-blue-500" />}
                  {result.doc_type === 'api' && <Code className="w-5 h-5 text-green-500" />}
                  {result.doc_type === 'architecture' && <Box className="w-5 h-5 text-purple-500" />}
                  {result.doc_type === 'usage' && <BookOpen className="w-5 h-5 text-orange-500" />}
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-gray-800">
                    {result.title || 'Documentation Match'}
                  </h3>
                  <div className="mt-1 text-sm text-gray-600">
                    <p dangerouslySetInnerHTML={{ 
                      __html: result.snippet || result.content?.substring(0, 150) + '...' 
                    }} />
                  </div>
                  <div className="mt-1 flex items-center text-xs text-gray-500">
                    <span className="capitalize">{result.doc_type}</span>
                    {result.section && (
                      <>
                        <span className="mx-1">•</span>
                        <span>{result.section}</span>
                      </>
                    )}
                    {result.relevance && (
                      <>
                        <span className="mx-1">•</span>
                        <span>Relevance: {Math.round(result.relevance * 100)}%</span>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default DocumentationSearch;