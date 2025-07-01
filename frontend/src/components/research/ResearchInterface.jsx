import React, { useState, useEffect, useRef } from 'react';
import { 
  Search, 
  Play, 
  Pause, 
  RefreshCw, 
  CheckCircle, 
  Clock, 
  AlertCircle,
  FileText,
  Download,
  Settings,
  Loader2
} from 'lucide-react';
import { researchService } from '../../services/research';
import ResearchProgress from './ResearchProgress';
import ResearchResults from './ResearchResults';

const ResearchInterface = () => {
  // Main state management
  const [query, setQuery] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  const [currentResearchId, setCurrentResearchId] = useState(null);
  const [researchStatus, setResearchStatus] = useState(null);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [settings, setSettings] = useState({
    maxSubagents: 3,
    maxIterations: 5
  });

  // UI state
  const [queryValidation, setQueryValidation] = useState({ isValid: true, errors: [] });
  const [showSettings, setShowSettings] = useState(false);

  const pollIntervalRef = useRef(null);

  // Query validation effect
  useEffect(() => {
    if (query) {
      const validation = researchService.validateQuery(query);
      setQueryValidation(validation);
    } else {
      setQueryValidation({ isValid: true, errors: [] });
    }
  }, [query]);

  // Enhanced polling mechanism with retry logic and connection management
  useEffect(() => {
    let retryCount = 0;
    const maxRetries = 3;
    let pollInterval = 2000; // Start with 2 seconds
    
    const pollForStatus = async () => {
      if (!currentResearchId || !isResearching) return;
      
      try {
        const statusData = await researchService.getResearchStatus(currentResearchId);
        setResearchStatus(statusData);
        
        // Reset retry count on successful poll
        retryCount = 0;
        pollInterval = 2000; // Reset to normal interval
        
        if (statusData.status === 'completed') {
          // Fetch final results
          try {
            const resultData = await researchService.getResearchResult(currentResearchId);
            setResults(researchService.formatResults(resultData));
            setIsResearching(false);
            clearInterval(pollIntervalRef.current);
          } catch (resultErr) {
            console.error('Error fetching research results:', resultErr);
            setError('Failed to fetch research results: ' + resultErr.message);
            setIsResearching(false);
            clearInterval(pollIntervalRef.current);
          }
        } else if (statusData.status === 'failed') {
          setError(statusData.message || 'Research failed');
          setIsResearching(false);
          clearInterval(pollIntervalRef.current);
        }
      } catch (err) {
        console.error('Error polling research status:', err);
        retryCount++;
        
        if (retryCount >= maxRetries) {
          setError('Connection lost. Failed to get research status after multiple attempts.');
          setIsResearching(false);
          clearInterval(pollIntervalRef.current);
        } else {
          // Exponential backoff for retries
          pollInterval = Math.min(pollInterval * 1.5, 10000); // Max 10 seconds
          console.log(`Retrying in ${pollInterval}ms (attempt ${retryCount}/${maxRetries})`);
        }
      }
    };

    if (currentResearchId && isResearching) {
      // Initial poll
      pollForStatus();
      
      // Set up interval polling
      pollIntervalRef.current = setInterval(pollForStatus, pollInterval);
    }

    return () => {
      if (pollIntervalRef.current) {
        clearInterval(pollIntervalRef.current);
      }
    };
  }, [currentResearchId, isResearching]);

  const startResearch = async () => {
    if (!query.trim() || !queryValidation.isValid) return;

    setIsResearching(true);
    setError(null);
    setResults(null);
    setResearchStatus(null);

    try {
      const response = await researchService.startResearch({
        query: query.trim(),
        max_subagents: settings.maxSubagents,
        max_iterations: settings.maxIterations
      });

      setCurrentResearchId(response.research_id);
      setResearchStatus({
        status: 'started',
        message: 'Research initiated...',
        progress_percentage: 0
      });
    } catch (err) {
      setError(err.message);
      setIsResearching(false);
    }
  };

  const stopResearch = async () => {
    if (currentResearchId) {
      try {
        await researchService.cancelResearch(currentResearchId);
      } catch (err) {
        console.error('Error cancelling research:', err);
      }
    }
    
    setIsResearching(false);
    setCurrentResearchId(null);
    setResearchStatus(null);
    if (pollIntervalRef.current) {
      clearInterval(pollIntervalRef.current);
    }
  };

  const clearResults = () => {
    setResults(null);
    setError(null);
    setResearchStatus(null);
    setCurrentResearchId(null);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey && !isResearching && queryValidation.isValid) {
      e.preventDefault();
      startResearch();
    }
  };

  const getCharacterCount = () => {
    return query.length;
  };

  const getCharacterCountColor = () => {
    const count = getCharacterCount();
    if (count < 10) return 'text-red-500';
    if (count > 1800) return 'text-orange-500';
    if (count > 2000) return 'text-red-500';
    return 'text-gray-500';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Multi-Agent Research System
          </h1>
          <p className="text-gray-600">
            Conduct comprehensive research using AI agents that work in parallel to gather and analyze information.
          </p>
        </div>

        {/* Research Input */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          <div className="flex flex-col space-y-4">
            {/* Query Input */}
            <div className="flex-1">
              <label htmlFor="research-query" className="block text-sm font-medium text-gray-700 mb-2">
                Research Query
              </label>
              <div className="relative">
                <textarea
                  id="research-query"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Enter your research question (e.g., 'What are the latest breakthroughs in AI-powered medical diagnosis in 2025?')"
                  className={`w-full px-4 py-3 pr-12 border rounded-lg focus:ring-2 focus:ring-blue-500 resize-none ${
                    queryValidation.isValid ? 'border-gray-300 focus:border-blue-500' : 'border-red-300 focus:border-red-500'
                  }`}
                  rows={3}
                  disabled={isResearching}
                />
                <Search className="absolute right-4 top-4 w-5 h-5 text-gray-400" />
              </div>
              
              {/* Character count and validation */}
              <div className="flex justify-between items-center mt-2">
                <div className="flex flex-col">
                  {!queryValidation.isValid && (
                    <div className="text-red-600 text-sm">
                      {queryValidation.errors.map((error, index) => (
                        <div key={index} className="flex items-center space-x-1">
                          <AlertCircle className="w-4 h-4" />
                          <span>{error}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <span className={`text-sm ${getCharacterCountColor()}`}>
                  {getCharacterCount()}/2000 characters
                </span>
              </div>
            </div>

            {/* Settings and Controls */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-4 sm:space-y-0">
              {/* Research Settings */}
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => setShowSettings(!showSettings)}
                  className="flex items-center space-x-2 text-gray-600 hover:text-gray-800"
                  disabled={isResearching}
                >
                  <Settings className="w-4 h-4" />
                  <span className="text-sm">Settings</span>
                </button>

                {showSettings && (
                  <div className="flex items-center space-x-4">
                    <div className="flex items-center space-x-2">
                      <label className="text-sm text-gray-700">Max Agents:</label>
                      <select
                        value={settings.maxSubagents}
                        onChange={(e) => setSettings(prev => ({ ...prev, maxSubagents: parseInt(e.target.value) }))}
                        disabled={isResearching}
                        className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value={1}>1</option>
                        <option value={2}>2</option>
                        <option value={3}>3</option>
                        <option value={4}>4</option>
                        <option value={5}>5</option>
                      </select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <label className="text-sm text-gray-700">Max Iterations:</label>
                      <select
                        value={settings.maxIterations}
                        onChange={(e) => setSettings(prev => ({ ...prev, maxIterations: parseInt(e.target.value) }))}
                        disabled={isResearching}
                        className="px-2 py-1 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      >
                        <option value={2}>2</option>
                        <option value={3}>3</option>
                        <option value={5}>5</option>
                        <option value={8}>8</option>
                        <option value={10}>10</option>
                      </select>
                    </div>
                  </div>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex items-center space-x-3">
                {results && (
                  <button
                    onClick={clearResults}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    Clear
                  </button>
                )}
                
                {isResearching ? (
                  <button
                    onClick={stopResearch}
                    className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center space-x-2"
                  >
                    <Pause className="w-4 h-4" />
                    <span>Stop Research</span>
                  </button>
                ) : (
                  <button
                    onClick={startResearch}
                    disabled={!query.trim() || !queryValidation.isValid}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                  >
                    <Play className="w-4 h-4" />
                    <span>Start Research</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-5 h-5 text-red-600" />
              <span className="text-red-800 font-medium">Research Error</span>
            </div>
            <p className="text-red-700 mt-1">{error}</p>
          </div>
        )}

        {/* Progress Display */}
        {(isResearching || researchStatus) && (
          <ResearchProgress 
            status={researchStatus}
            isActive={isResearching}
          />
        )}

        {/* Results Display */}
        {results && (
          <ResearchResults 
            results={results}
            query={query}
          />
        )}

        {/* Help Text */}
        {!isResearching && !results && !error && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center space-x-3">
              <Search className="w-6 h-6 text-blue-600" />
              <div>
                <h3 className="font-medium text-blue-900">How to Use Multi-Agent Research</h3>
                <p className="text-blue-700 text-sm mt-1">
                  Enter a detailed research question above. Our AI agents will work together to gather information, 
                  analyze sources, and provide you with a comprehensive research report with citations.
                </p>
                <div className="mt-2 text-blue-700 text-sm">
                  <strong>Tips:</strong> Be specific in your query, use at least 10 characters, and consider adjusting 
                  the number of agents and iterations in settings for different research depths.
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResearchInterface;