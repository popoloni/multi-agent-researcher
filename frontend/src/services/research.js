import api from './api';

/**
 * Research API Service
 * Provides all research-related API operations with error handling and retry logic
 */
export const researchService = {
  /**
   * Start a new research task
   * @param {Object} researchData - Research configuration
   * @param {string} researchData.query - Research query
   * @param {number} researchData.max_subagents - Maximum number of subagents (1-5)
   * @param {number} researchData.max_iterations - Maximum iterations (2-10)
   * @returns {Promise<Object>} Research task information with research_id
   */
  startResearch: async (researchData) => {
    // Validate input data
    if (!researchData.query || typeof researchData.query !== 'string') {
      throw new Error('Query is required and must be a string');
    }
    
    if (researchData.query.trim().length < 10) {
      throw new Error('Query must be at least 10 characters long');
    }
    
    if (researchData.max_subagents && (researchData.max_subagents < 1 || researchData.max_subagents > 5)) {
      throw new Error('max_subagents must be between 1 and 5');
    }
    
    if (researchData.max_iterations && (researchData.max_iterations < 2 || researchData.max_iterations > 10)) {
      throw new Error('max_iterations must be between 2 and 10');
    }

    try {
      const response = await api.post('/research/start', {
        query: researchData.query.trim(),
        max_subagents: researchData.max_subagents || 3,
        max_iterations: researchData.max_iterations || 5
      });
      
      // Validate response structure
      if (!response.data || !response.data.research_id) {
        throw new Error('Invalid response: missing research_id');
      }
      
      return response.data;
    } catch (error) {
      // Re-throw validation errors as-is
      if (error.message === 'Invalid response: missing research_id') {
        throw error;
      }
      
      if (error.response?.status === 400) {
        throw new Error(error.response.data?.detail || 'Invalid request parameters');
      } else if (error.response?.status === 500) {
        throw new Error('Server error occurred while starting research');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout - please try again');
      } else if (!error.response) {
        throw new Error('Network error - please check your connection');
      }
      throw error;
    }
  },

  /**
   * Get research status with progress information
   * @param {string} researchId - Research task ID
   * @returns {Promise<Object>} Research status and progress information
   */
  getResearchStatus: async (researchId) => {
    if (!researchId || typeof researchId !== 'string') {
      throw new Error('Research ID is required and must be a string');
    }

    try {
      const response = await api.get(`/research/${researchId}/status`);
      
      // Validate response structure
      if (!response.data) {
        throw new Error('Invalid response: missing status data');
      }
      
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        throw new Error('Research task not found');
      } else if (error.response?.status === 500) {
        throw new Error('Server error occurred while getting research status');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout - please try again');
      } else if (!error.response) {
        throw new Error('Network error - please check your connection');
      }
      throw error;
    }
  },

  /**
   * Get research results
   * @param {string} researchId - Research task ID
   * @returns {Promise<Object>} Complete research results
   */
  getResearchResult: async (researchId) => {
    if (!researchId || typeof researchId !== 'string') {
      throw new Error('Research ID is required and must be a string');
    }

    try {
      const response = await api.get(`/research/${researchId}/result`);
      
      // Validate response structure
      if (!response.data) {
        throw new Error('Invalid response: missing result data');
      }
      
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        throw new Error('Research results not found');
      } else if (error.response?.status === 400) {
        throw new Error('Research not completed yet');
      } else if (error.response?.status === 500) {
        throw new Error('Server error occurred while getting research results');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout - please try again');
      } else if (!error.response) {
        throw new Error('Network error - please check your connection');
      }
      throw error;
    }
  },

  /**
   * Get research history with filtering and pagination
   * @param {Object} options - Query options
   * @param {number} options.limit - Maximum number of results (default: 50)
   * @param {number} options.offset - Offset for pagination (default: 0)
   * @param {string} options.status_filter - Filter by status (optional)
   * @returns {Promise<Array>} Array of research history items
   */
  getResearchHistory: async (options = {}) => {
    const { limit = 50, offset = 0, status_filter } = options;
    
    if (limit < 1 || limit > 100) {
      throw new Error('Limit must be between 1 and 100');
    }
    
    if (offset < 0) {
      throw new Error('Offset must be non-negative');
    }

    try {
      const params = { limit, offset };
      if (status_filter) {
        params.status_filter = status_filter;
      }
      
      const response = await api.get('/research/history', { params });
      
      // Validate response structure
      if (!Array.isArray(response.data)) {
        throw new Error('Invalid response: expected array of history items');
      }
      
      return response.data;
    } catch (error) {
      if (error.response?.status === 500) {
        throw new Error('Server error occurred while getting research history');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout - please try again');
      } else if (!error.response) {
        throw new Error('Network error - please check your connection');
      }
      throw error;
    }
  },

  /**
   * Get research analytics
   * @returns {Promise<Object>} Research analytics data
   */
  getResearchAnalytics: async () => {
    try {
      const response = await api.get('/research/analytics');
      
      // Validate response structure
      if (!response.data) {
        throw new Error('Invalid response: missing analytics data');
      }
      
      return response.data;
    } catch (error) {
      if (error.response?.status === 500) {
        throw new Error('Server error occurred while getting research analytics');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout - please try again');
      } else if (!error.response) {
        throw new Error('Network error - please check your connection');
      }
      throw error;
    }
  },

  /**
   * Cancel a running research task
   * @param {string} researchId - Research task ID
   * @returns {Promise<Object>} Cancellation confirmation
   */
  cancelResearch: async (researchId) => {
    if (!researchId || typeof researchId !== 'string') {
      throw new Error('Research ID is required and must be a string');
    }

    try {
      const response = await api.post(`/research/${researchId}/cancel`);
      return response.data;
    } catch (error) {
      if (error.response?.status === 404) {
        throw new Error('Research task not found');
      } else if (error.response?.status === 400) {
        throw new Error('Research task cannot be cancelled');
      } else if (error.response?.status === 500) {
        throw new Error('Server error occurred while cancelling research');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout - please try again');
      } else if (!error.response) {
        throw new Error('Network error - please check your connection');
      }
      throw error;
    }
  },

  /**
   * Run demo research (for testing purposes)
   * @returns {Promise<Object>} Demo research result
   */
  runDemo: async () => {
    try {
      const response = await api.post('/research/demo');
      return response.data;
    } catch (error) {
      if (error.response?.status === 500) {
        throw new Error('Server error occurred while running demo');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout - please try again');
      } else if (!error.response) {
        throw new Error('Network error - please check your connection');
      }
      throw error;
    }
  },

  /**
   * Test citations functionality
   * @returns {Promise<Object>} Citation test result
   */
  testCitations: async () => {
    try {
      const response = await api.post('/research/test-citations');
      return response.data;
    } catch (error) {
      if (error.response?.status === 500) {
        throw new Error('Server error occurred while testing citations');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('Request timeout - please try again');
      } else if (!error.response) {
        throw new Error('Network error - please check your connection');
      }
      throw error;
    }
  },

  /**
   * Utility function to validate query
   * @param {string} query - Research query to validate
   * @returns {Object} Validation result with isValid and errors
   */
  validateQuery: (query) => {
    const errors = [];
    
    if (!query || typeof query !== 'string') {
      errors.push('Query is required and must be a string');
    } else {
      const trimmedQuery = query.trim();
      
      if (trimmedQuery.length < 10) {
        errors.push('Query must be at least 10 characters long');
      }
      
      if (trimmedQuery.length > 2000) {
        errors.push('Query must be less than 2000 characters');
      }
      
      // Check for potentially malicious content
      if (/<script|javascript:|data:/i.test(trimmedQuery)) {
        errors.push('Query contains potentially unsafe content');
      }
      
      // Check if query has meaningful content
      if (!/\w+/.test(trimmedQuery)) {
        errors.push('Query must contain meaningful text');
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors
    };
  },

  /**
   * Utility function to format research results for display
   * @param {Object} rawResults - Raw research results from API
   * @returns {Object} Formatted results for UI consumption
   */
  formatResults: (rawResults) => {
    if (!rawResults) {
      return null;
    }

    return {
      ...rawResults,
      // Format dates
      created_at: rawResults.created_at ? new Date(rawResults.created_at) : null,
      completed_at: rawResults.completed_at ? new Date(rawResults.completed_at) : null,
      
      // Format execution time
      execution_time_formatted: rawResults.execution_time 
        ? `${Math.floor(rawResults.execution_time / 60)}m ${Math.floor(rawResults.execution_time % 60)}s`
        : null,
      
      // Format token count
      tokens_formatted: rawResults.total_tokens_used 
        ? rawResults.total_tokens_used.toLocaleString()
        : null,
      
      // Ensure arrays exist
      sources_used: rawResults.sources_used || [],
      citations: rawResults.citations || [],
      report_sections: rawResults.report_sections || []
    };
  },

  /**
   * Utility function to retry failed requests
   * @param {Function} apiCall - API call function to retry
   * @param {number} maxRetries - Maximum number of retries (default: 3)
   * @param {number} delay - Delay between retries in ms (default: 1000)
   * @returns {Promise} Result of successful API call
   */
  retryRequest: async (apiCall, maxRetries = 3, delay = 1000) => {
    let lastError;
    
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await apiCall();
      } catch (error) {
        lastError = error;
        
        // Don't retry on client errors (4xx) except for timeouts
        if (error.response?.status >= 400 && error.response?.status < 500 && error.code !== 'ECONNABORTED') {
          throw error;
        }
        
        // Don't retry on the last attempt
        if (attempt === maxRetries) {
          break;
        }
        
        // Wait before retrying
        await new Promise(resolve => setTimeout(resolve, delay * attempt));
      }
    }
    
    throw lastError;
  }
};

export default researchService;