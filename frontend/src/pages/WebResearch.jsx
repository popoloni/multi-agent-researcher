import React, { useState } from 'react';
import { Search, Globe, BookOpen, ExternalLink, ArrowRight } from 'lucide-react';
import Layout from '../components/layout/Layout';

const WebResearch = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState([]);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    // TODO: Implement actual web research functionality
    // For now, simulate search results
    setTimeout(() => {
      setSearchResults([
        {
          id: 1,
          title: 'Multi-Agent Systems in Software Development',
          url: 'https://example.com/multi-agent-systems',
          snippet: 'An overview of how multi-agent systems are revolutionizing software development practices...',
          source: 'Research Paper'
        },
        {
          id: 2,
          title: 'AI-Powered Code Analysis Tools',
          url: 'https://example.com/ai-code-analysis',
          snippet: 'Exploring the latest advancements in AI-powered code analysis and documentation generation...',
          source: 'Technical Blog'
        },
        {
          id: 3,
          title: 'Repository Management Best Practices',
          url: 'https://example.com/repo-management',
          snippet: 'Best practices for managing large-scale code repositories with intelligent automation...',
          source: 'Developer Guide'
        }
      ]);
      setIsSearching(false);
    }, 2000);
  };

  const handleResultClick = (url) => {
    window.open(url, '_blank');
  };

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Web Research</h1>
          <p className="text-gray-600 max-w-2xl mx-auto">
            Discover the latest research, articles, and resources related to multi-agent systems, 
            AI-powered development tools, and software engineering best practices.
          </p>
        </div>

        {/* Search Section */}
        <div className="bg-white rounded-lg shadow p-8">
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
            <div className="relative">
              <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search for research papers, articles, or technical resources..."
                className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-lg"
              />
              <button
                type="submit"
                disabled={isSearching || !searchQuery.trim()}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 bg-primary-500 text-white px-4 py-2 rounded-md hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSearching ? 'Searching...' : 'Search'}
              </button>
            </div>
          </form>
        </div>

        {/* Search Results */}
        {searchResults.length > 0 && (
          <div className="bg-white rounded-lg shadow">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold">Search Results</h2>
              <p className="text-sm text-gray-600 mt-1">
                Found {searchResults.length} results for "{searchQuery}"
              </p>
            </div>
            
            <div className="divide-y divide-gray-200">
              {searchResults.map((result) => (
                <div 
                  key={result.id} 
                  className="p-6 hover:bg-gray-50 cursor-pointer transition-colors"
                  onClick={() => handleResultClick(result.url)}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <Globe className="w-4 h-4 text-gray-400" />
                        <span className="text-sm text-gray-500">{result.source}</span>
                      </div>
                      <h3 className="text-lg font-medium text-primary-600 hover:text-primary-700 mb-2">
                        {result.title}
                      </h3>
                      <p className="text-gray-600 mb-3">{result.snippet}</p>
                      <div className="flex items-center space-x-2 text-sm text-gray-500">
                        <ExternalLink className="w-4 h-4" />
                        <span>{result.url}</span>
                      </div>
                    </div>
                    <ArrowRight className="w-5 h-5 text-gray-400" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Research Categories */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Research Categories</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors cursor-pointer">
              <BookOpen className="w-8 h-8 text-primary-500 mb-2" />
              <h3 className="font-medium">Multi-Agent Systems</h3>
              <p className="text-sm text-gray-600">Research papers and articles on multi-agent architectures</p>
            </div>
            
            <div className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors cursor-pointer">
              <Globe className="w-8 h-8 text-primary-500 mb-2" />
              <h3 className="font-medium">AI in Software Development</h3>
              <p className="text-sm text-gray-600">Latest developments in AI-powered development tools</p>
            </div>
            
            <div className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors cursor-pointer">
              <Search className="w-8 h-8 text-primary-500 mb-2" />
              <h3 className="font-medium">Code Analysis</h3>
              <p className="text-sm text-gray-600">Advanced code analysis and documentation techniques</p>
            </div>
          </div>
        </div>

        {/* Coming Soon */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <div className="flex items-center space-x-3">
            <Globe className="w-6 h-6 text-blue-600" />
            <div>
              <h3 className="font-medium text-blue-900">Enhanced Research Features Coming Soon</h3>
              <p className="text-blue-700 text-sm mt-1">
                We're working on integrating with research databases, academic APIs, and advanced search capabilities 
                to provide you with the most relevant and up-to-date research materials.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default WebResearch; 