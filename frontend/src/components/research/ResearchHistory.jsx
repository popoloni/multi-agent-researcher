import React, { useState, useEffect } from 'react';
import { 
  Clock, 
  Search, 
  FileText, 
  ExternalLink,
  Trash2,
  RefreshCw,
  History,
  TrendingUp,
  Users,
  Calendar,
  Filter,
  SortAsc,
  SortDesc,
  MoreVertical,
  Star,
  StarOff,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

const ResearchHistory = React.forwardRef(({ onSelectQuery, onLoadHistory }, ref) => {
  const [history, setHistory] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('timestamp'); // timestamp, duration, sources
  const [sortOrder, setSortOrder] = useState('desc'); // asc, desc
  const [filterStatus, setFilterStatus] = useState('all'); // all, completed, failed
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedItems, setSelectedItems] = useState(new Set());
  const [showBulkActions, setShowBulkActions] = useState(false);

  useEffect(() => {
    loadHistory();
  }, []);

  const loadHistory = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Try to load from localStorage first
      let loadedHistory = [];
      
      try {
        const localHistory = localStorage.getItem('research_history');
        if (localHistory) {
          loadedHistory = JSON.parse(localHistory);
        }
      } catch (storageError) {
        console.warn('localStorage error:', storageError);
      }

      // Try to load from API if available
      if (onLoadHistory) {
        try {
          const apiHistory = await onLoadHistory();
          if (apiHistory && apiHistory.length > 0) {
            loadedHistory = apiHistory;
            // Update localStorage with API data
            try {
              localStorage.setItem('research_history', JSON.stringify(apiHistory));
            } catch (storageError) {
              console.warn('localStorage save error:', storageError);
            }
          }
        } catch (apiError) {
          console.error('API error:', apiError);
          // Continue with localStorage data if API fails
        }
      }

      // If no history exists and no API call was made, create some sample data for demonstration
      if (loadedHistory.length === 0 && !onLoadHistory) {
        const sampleHistory = [
          {
            id: 'sample-1',
            query: 'What are the latest breakthroughs in AI-powered medical diagnosis in 2025?',
            timestamp: new Date(Date.now() - 86400000).toISOString(),
            status: 'completed',
            sources_count: 15,
            duration: 180,
            tokens_used: 4500,
            subagent_count: 3,
            favorite: false,
            tags: ['AI', 'Medical', 'Diagnosis']
          },
          {
            id: 'sample-2',
            query: 'How is quantum computing affecting financial modeling and risk assessment?',
            timestamp: new Date(Date.now() - 172800000).toISOString(),
            status: 'completed',
            sources_count: 23,
            duration: 240,
            tokens_used: 6200,
            subagent_count: 4,
            favorite: true,
            tags: ['Quantum Computing', 'Finance', 'Risk Assessment']
          },
          {
            id: 'sample-3',
            query: 'Latest developments in renewable energy storage technologies',
            timestamp: new Date(Date.now() - 259200000).toISOString(),
            status: 'completed',
            sources_count: 18,
            duration: 195,
            tokens_used: 3800,
            subagent_count: 3,
            favorite: false,
            tags: ['Renewable Energy', 'Storage', 'Technology']
          },
          {
            id: 'sample-4',
            query: 'Impact of climate change on global food security',
            timestamp: new Date(Date.now() - 345600000).toISOString(),
            status: 'failed',
            sources_count: 0,
            duration: 45,
            tokens_used: 1200,
            subagent_count: 2,
            favorite: false,
            tags: ['Climate Change', 'Food Security']
          }
        ];
        loadedHistory = sampleHistory;
        try {
          localStorage.setItem('research_history', JSON.stringify(sampleHistory));
        } catch (storageError) {
          console.warn('localStorage save error:', storageError);
        }
      }
      
      setHistory(loadedHistory);
    } catch (error) {
      console.error('Error loading history:', error);
      setError('Failed to load research history');
      setHistory([]); // Clear any partial data
    } finally {
      setIsLoading(false);
    }
  };

  const saveHistoryToStorage = (updatedHistory) => {
    localStorage.setItem('research_history', JSON.stringify(updatedHistory));
    setHistory(updatedHistory);
  };

  const addToHistory = (researchData) => {
    const newEntry = {
      id: researchData.research_id || `research-${Date.now()}`,
      query: researchData.query,
      timestamp: new Date().toISOString(),
      status: researchData.status || 'completed',
      sources_count: researchData.sources_used?.length || 0,
      duration: researchData.execution_time || 0,
      tokens_used: researchData.total_tokens_used || 0,
      subagent_count: researchData.subagent_count || 0,
      favorite: false,
      tags: extractTagsFromQuery(researchData.query)
    };

    const updatedHistory = [newEntry, ...history];
    saveHistoryToStorage(updatedHistory);
  };

  const extractTagsFromQuery = (query) => {
    // Simple tag extraction based on common keywords
    const keywords = query.toLowerCase().split(/\s+/);
    const commonTags = [
      'AI', 'Machine Learning', 'Technology', 'Science', 'Medical', 'Healthcare',
      'Finance', 'Economics', 'Climate', 'Environment', 'Energy', 'Research',
      'Innovation', 'Development', 'Analysis', 'Security', 'Data', 'Computing'
    ];
    
    return commonTags.filter(tag => 
      keywords.some(keyword => tag.toLowerCase().includes(keyword) || keyword.includes(tag.toLowerCase()))
    ).slice(0, 3);
  };

  const deleteHistoryItem = (id) => {
    const updatedHistory = history.filter(item => item.id !== id);
    saveHistoryToStorage(updatedHistory);
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      newSet.delete(id);
      return newSet;
    });
  };

  const toggleFavorite = (id) => {
    const updatedHistory = history.map(item =>
      item.id === id ? { ...item, favorite: !item.favorite } : item
    );
    saveHistoryToStorage(updatedHistory);
  };

  const handleBulkDelete = () => {
    const updatedHistory = history.filter(item => !selectedItems.has(item.id));
    saveHistoryToStorage(updatedHistory);
    setSelectedItems(new Set());
    setShowBulkActions(false);
  };

  const handleSelectItem = (id) => {
    setSelectedItems(prev => {
      const newSet = new Set(prev);
      if (newSet.has(id)) {
        newSet.delete(id);
      } else {
        newSet.add(id);
      }
      setShowBulkActions(newSet.size > 0);
      return newSet;
    });
  };

  const handleSelectAll = () => {
    if (selectedItems.size === filteredAndSortedHistory.length) {
      setSelectedItems(new Set());
      setShowBulkActions(false);
    } else {
      setSelectedItems(new Set(filteredAndSortedHistory.map(item => item.id)));
      setShowBulkActions(true);
    }
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 48) return 'Yesterday';
    if (diffInHours < 168) return `${Math.floor(diffInHours / 24)}d ago`;
    return date.toLocaleDateString();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'running':
        return 'bg-blue-100 text-blue-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-3 h-3" />;
      case 'failed':
        return <AlertCircle className="w-3 h-3" />;
      case 'running':
        return <Clock className="w-3 h-3" />;
      default:
        return <Clock className="w-3 h-3" />;
    }
  };

  // Filter and sort history
  const filteredAndSortedHistory = history
    .filter(item => {
      // Status filter
      if (filterStatus !== 'all' && item.status !== filterStatus) return false;
      
      // Search filter
      if (searchTerm && !item.query.toLowerCase().includes(searchTerm.toLowerCase())) return false;
      
      return true;
    })
    .sort((a, b) => {
      let aValue, bValue;
      
      switch (sortBy) {
        case 'timestamp':
          aValue = new Date(a.timestamp);
          bValue = new Date(b.timestamp);
          break;
        case 'duration':
          aValue = a.duration;
          bValue = b.duration;
          break;
        case 'sources':
          aValue = a.sources_count;
          bValue = b.sources_count;
          break;
        case 'query':
          aValue = a.query.toLowerCase();
          bValue = b.query.toLowerCase();
          break;
        default:
          aValue = new Date(a.timestamp);
          bValue = new Date(b.timestamp);
      }
      
      if (sortOrder === 'asc') {
        return aValue > bValue ? 1 : -1;
      } else {
        return aValue < bValue ? 1 : -1;
      }
    });

  // Expose addToHistory method for parent component
  React.useImperativeHandle(ref, () => ({
    addToHistory
  }));

  if (isLoading) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center py-8">
          <RefreshCw className="w-6 h-6 text-gray-400 animate-spin" />
          <span className="ml-2 text-gray-600">Loading research history...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-center py-8">
          <AlertCircle className="w-6 h-6 text-red-500" />
          <span className="ml-2 text-red-600">{error}</span>
          <button
            onClick={loadHistory}
            className="ml-4 px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <History className="w-5 h-5 mr-2" />
            Research History
            {filteredAndSortedHistory.length > 0 && (
              <span className="ml-2 text-sm font-normal text-gray-500">
                ({filteredAndSortedHistory.length} {filteredAndSortedHistory.length === 1 ? 'item' : 'items'})
              </span>
            )}
          </h3>
          <div className="flex items-center space-x-2">
            {showBulkActions && (
              <div className="flex items-center space-x-2 mr-4">
                <span className="text-sm text-gray-600">
                  {selectedItems.size} selected
                </span>
                <button
                  onClick={handleBulkDelete}
                  className="px-3 py-1 bg-red-100 text-red-700 rounded hover:bg-red-200 transition-colors text-sm"
                >
                  Delete Selected
                </button>
              </div>
            )}
            <button
              onClick={loadHistory}
              className="text-gray-600 hover:text-gray-800 p-2 hover:bg-gray-100 rounded-lg transition-colors"
              title="Refresh history"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        {history.length > 0 && (
          <div className="mt-4 flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0 sm:space-x-4">
            {/* Search */}
            <div className="relative flex-1 max-w-md">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search research history..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            {/* Filters and Sort */}
            <div className="flex items-center space-x-3">
              {/* Status Filter */}
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="failed">Failed</option>
                <option value="running">Running</option>
              </select>

              {/* Sort */}
              <select
                value={`${sortBy}-${sortOrder}`}
                onChange={(e) => {
                  const [field, order] = e.target.value.split('-');
                  setSortBy(field);
                  setSortOrder(order);
                }}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm"
              >
                <option value="timestamp-desc">Newest First</option>
                <option value="timestamp-asc">Oldest First</option>
                <option value="duration-desc">Longest Duration</option>
                <option value="duration-asc">Shortest Duration</option>
                <option value="sources-desc">Most Sources</option>
                <option value="sources-asc">Fewest Sources</option>
                <option value="query-asc">Query A-Z</option>
                <option value="query-desc">Query Z-A</option>
              </select>

              {/* Select All */}
              {filteredAndSortedHistory.length > 0 && (
                <button
                  onClick={handleSelectAll}
                  className="px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                >
                  {selectedItems.size === filteredAndSortedHistory.length ? 'Deselect All' : 'Select All'}
                </button>
              )}
            </div>
          </div>
        )}
      </div>

      {/* History List */}
      {filteredAndSortedHistory.length === 0 ? (
        <div className="p-8 text-center">
          {history.length === 0 ? (
            <>
              <Search className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">No Research History</h4>
              <p className="text-gray-600">
                Start your first research query to see results here.
              </p>
            </>
          ) : (
            <>
              <Filter className="w-12 h-12 text-gray-300 mx-auto mb-4" />
              <h4 className="text-lg font-medium text-gray-900 mb-2">No Results Found</h4>
              <p className="text-gray-600">
                Try adjusting your search or filter criteria.
              </p>
            </>
          )}
        </div>
      ) : (
        <div className="divide-y divide-gray-200">
          {filteredAndSortedHistory.map((item) => (
            <div 
              key={item.id}
              className={`p-6 hover:bg-gray-50 transition-colors ${
                selectedItems.has(item.id) ? 'bg-blue-50' : ''
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-start space-x-3 flex-1 min-w-0">
                  {/* Selection Checkbox */}
                  <input
                    type="checkbox"
                    checked={selectedItems.has(item.id)}
                    onChange={() => handleSelectItem(item.id)}
                    className="mt-1 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <button
                      onClick={() => onSelectQuery(item.query)}
                      className="text-left w-full group"
                    >
                      <h4 className="text-base font-medium text-gray-900 group-hover:text-blue-600 transition-colors line-clamp-2 mb-2">
                        {item.query}
                      </h4>
                    </button>
                    
                    {/* Tags */}
                    {item.tags && item.tags.length > 0 && (
                      <div className="flex flex-wrap gap-1 mb-2">
                        {item.tags.map((tag, index) => (
                          <span
                            key={index}
                            className="inline-flex px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700"
                          >
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}

                    {/* Metadata */}
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                      <span className="flex items-center">
                        <Calendar className="w-3 h-3 mr-1" />
                        {formatDate(item.timestamp)}
                      </span>
                      <span className="flex items-center">
                        <Clock className="w-3 h-3 mr-1" />
                        {formatTime(item.duration)}
                      </span>
                      <span className="flex items-center">
                        <FileText className="w-3 h-3 mr-1" />
                        {item.sources_count} sources
                      </span>
                      <span className="flex items-center">
                        <Users className="w-3 h-3 mr-1" />
                        {item.subagent_count} agents
                      </span>
                      {item.tokens_used > 0 && (
                        <span className="flex items-center">
                          <TrendingUp className="w-3 h-3 mr-1" />
                          {item.tokens_used.toLocaleString()} tokens
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Actions */}
                <div className="flex items-center space-x-2 ml-4">
                  {/* Status Badge */}
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(item.status)}`}>
                    {getStatusIcon(item.status)}
                    <span className="ml-1 capitalize">{item.status}</span>
                  </span>
                  
                  {/* Favorite Button */}
                  <button
                    onClick={() => toggleFavorite(item.id)}
                    className={`p-1 rounded transition-colors ${
                      item.favorite 
                        ? 'text-yellow-500 hover:text-yellow-600' 
                        : 'text-gray-400 hover:text-yellow-500'
                    }`}
                    title={item.favorite ? 'Remove from favorites' : 'Add to favorites'}
                  >
                    {item.favorite ? <Star className="w-4 h-4 fill-current" /> : <StarOff className="w-4 h-4" />}
                  </button>
                  
                  {/* Delete Button */}
                  <button
                    onClick={() => deleteHistoryItem(item.id)}
                    className="p-1 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded transition-colors"
                    title="Delete from history"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                  
                  {/* View Details Button */}
                  <button 
                    onClick={() => onSelectQuery(item.query)}
                    className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors"
                    title="Rerun this research"
                  >
                    <ExternalLink className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
});

export default ResearchHistory;