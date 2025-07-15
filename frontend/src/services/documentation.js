import api from './api';

class DocumentationService {
  constructor() {
    this.cache = new Map();
  }

  // Get documentation generation status with extended timeout
  async getDocumentationStatus(repositoryId, taskId) {
    return api.get(`/kenobi/repositories/${repositoryId}/documentation/status/${taskId}`, {
      timeout: 30000, // 30 seconds timeout for status checks
    });
  }

  // Poll documentation status until complete
  async pollDocumentationStatus(repositoryId, taskId, progressCallback) {
    let retries = 0;
    let lastProgress = 0;
    let stagnantCount = 0;
    
    // Get adaptive timeout based on model (try to get from API or use default)
    let maxRetries = 180; // Default 15 minutes
    try {
      const settingsResponse = await api.get('/api/settings/all');
      const settings = settingsResponse.data;
      if (settings.DOCUMENTATION_MODEL) {
        // Calculate timeout based on model type
        const model = settings.DOCUMENTATION_MODEL.value;
        maxRetries = this.calculateTimeoutForModel(model);
      }
    } catch (error) {
      console.warn('Could not get model settings, using default timeout');
    }
    
    const startTime = Date.now();
    
    while (retries < maxRetries) {
      try {
        const response = await this.getDocumentationStatus(repositoryId, taskId);
        const status = response.data;
        
        if (progressCallback) {
          progressCallback(status);
        }
        
        if (status.status === 'completed') {
          return status;
        } else if (status.status === 'failed') {
          throw new Error(status.error || 'Documentation generation failed');
        }
        
        // Check for progress stagnation
        if (status.progress === lastProgress) {
          stagnantCount++;
          if (stagnantCount > 24) { // 2 minutes of no progress
            console.warn('Documentation generation appears stagnant, but continuing...');
          }
        } else {
          stagnantCount = 0;
          lastProgress = status.progress;
        }
        
        // Progressive timeout strategy - extend timeout if making progress
        const elapsedMinutes = (Date.now() - startTime) / 60000;
        if (elapsedMinutes > 10 && status.progress > 0) {
          // If we're making progress after 10 minutes, extend timeout by 50%
          if (retries > maxRetries * 0.8) {
            maxRetries = Math.min(maxRetries * 1.5, 360); // Max 30 minutes
          }
        }
        
        // Adaptive polling interval based on progress and stage
        let pollInterval = 5000; // Default 5 seconds
        if (status.progress > 80) {
          pollInterval = 2000; // Faster polling near completion
        } else if (status.progress < 10) {
          pollInterval = 7000; // Slower polling at start
        }
        
        await new Promise(resolve => setTimeout(resolve, pollInterval));
        retries++;
      } catch (error) {
        console.error('Error polling documentation status:', error);
        throw error;
      }
    }
    
    const timeoutMinutes = Math.round(maxRetries * 5 / 60);
    throw new Error(`Documentation generation timed out after ${timeoutMinutes} minutes. This may be due to using a larger AI model that requires more processing time. Try using a smaller model or contact support.`);
  }
  
  // Calculate timeout based on model type
  calculateTimeoutForModel(model) {
    const modelTimeouts = {
      // Small models (fast)
      'llama3.2:1b': 120,    // 10 minutes
      'llama3.2:3b': 144,    // 12 minutes
      'phi3:3.8b': 132,      // 11 minutes
      
      // Medium models
      'llama3.1:8b': 180,    // 15 minutes
      'mistral:7b': 156,     // 13 minutes
      'gemma2:9b': 168,      // 14 minutes
      'qwen2.5:7b': 168,     // 14 minutes
      
      // Large models (slow)
      'llama3.1:70b': 360,   // 30 minutes
      'mixtral:8x7b': 300,   // 25 minutes
      
      // Anthropic models (API-based, usually faster)
      'claude-3-5-haiku-20241022': 96,      // 8 minutes
      'claude-3-5-sonnet-20241022': 120,    // 10 minutes
      'claude-4-sonnet-20241120': 144,      // 12 minutes
      'claude-4-opus-20241120': 180,        // 15 minutes
    };
    
    return modelTimeouts[model] || 180; // Default 15 minutes
  }

  // Search documentation with extended timeout
  async searchDocumentation(repositoryId, query, branch = 'main') {
    return api.get(`/kenobi/repositories/${repositoryId}/documentation/search`, {
      params: { query, branch },
      timeout: 60000, // 1 minute timeout for search operations
    });
  }

  // Simple cache set
  setCache(repositoryId, data) {
    console.log('Setting cache for:', repositoryId);
    this.cache.set(repositoryId, data);
    
    // Also save to localStorage
    try {
      localStorage.setItem(`doc_${repositoryId}`, JSON.stringify(data));
    } catch (e) {
      console.warn('Failed to save to localStorage:', e);
    }
  }

  // Simple cache get
  getCache(repositoryId) {
    console.log('Getting cache for:', repositoryId);
    
    // Try memory cache first
    const memoryData = this.cache.get(repositoryId);
    if (memoryData) {
      console.log('Found in memory cache');
      return memoryData;
    }
    
    // Try localStorage
    try {
      const stored = localStorage.getItem(`doc_${repositoryId}`);
      if (stored) {
        const data = JSON.parse(stored);
        this.cache.set(repositoryId, data); // Update memory cache
        console.log('Found in localStorage cache');
        return data;
      }
    } catch (e) {
      console.warn('Failed to get from localStorage:', e);
    }
    
    console.log('No cache found');
    return null;
  }

  // Clear cache
  clearCache(repositoryId) {
    this.cache.delete(repositoryId);
    try {
      localStorage.removeItem(`doc_${repositoryId}`);
    } catch (e) {
      console.warn('Failed to clear localStorage:', e);
    }
  }

  // Get documentation - SIMPLE AND RELIABLE
  async getDocumentation(repositoryId, branch = 'main') {
    console.log('Getting documentation for:', repositoryId);
    
    // Check cache first
    const cached = this.getCache(repositoryId);
    if (cached) {
      console.log('Returning cached documentation');
      return {
        data: { documentation: cached },
        cached: true
      };
    }

    // Get from API with extended timeout
    try {
      console.log('Fetching from API');
      const response = await api.get(`/kenobi/repositories/${repositoryId}/documentation?branch=${branch}`, {
        timeout: 120000, // 2 minutes timeout for fetching documentation
      });
      
      if (response.data && response.data.documentation) {
        const docString = response.data.documentation;
        
        // Parse JSON string if needed
        let docData;
        if (typeof docString === 'string') {
          try {
            docData = JSON.parse(docString);
            console.log('Successfully parsed documentation');
          } catch (e) {
            console.error('Failed to parse documentation:', e);
            throw new Error('Invalid documentation format');
          }
        } else {
          docData = docString;
        }
        
        // Cache the parsed data
        if (docData && Object.keys(docData).length > 0) {
          this.setCache(repositoryId, docData);
          console.log('Documentation cached');
        }
        
        // Return response with parsed documentation
        return {
          ...response,
          data: {
            ...response.data,
            documentation: docData
          }
        };
      }
      
      return response;
    } catch (error) {
      console.error('Error fetching documentation:', error);
      throw error;
    }
  }

  // Generate documentation with extended timeout
  async generateDocumentation(repositoryId, options = {}) {
    try {
      const response = await api.post(`/kenobi/repositories/${repositoryId}/documentation`, options, {
        timeout: 180000, // 3 minutes timeout for documentation generation start
      });
      return response;
    } catch (error) {
      console.error('Error generating documentation:', error);
      if (error.code === 'ECONNABORTED') {
        throw new Error('Documentation generation request timed out. The process may still be running in the background.');
      }
      throw error;
    }
  }

  // Get API endpoints documentation
  async getApiDocumentation(repositoryId, branch = 'main') {
    return api.get(`/kenobi/repositories/${repositoryId}/api-docs`, {
      params: { branch }
    });
  }
  
  // Get code analysis
  async getCodeAnalysis(repositoryId, branch = 'main') {
    return api.get(`/kenobi/repositories/${repositoryId}/analysis`, {
      params: { branch }
    });
  }

  // Delete documentation
  async deleteDocumentation(repositoryId, branch = 'main') {
    console.log('Deleting documentation for:', repositoryId);
    
    try {
      const response = await api.delete(`/kenobi/repositories/${repositoryId}/documentation?branch=${branch}`);
      
      // Clear cache
      this.clearCache(repositoryId);
      
      console.log('Documentation deleted successfully');
      return response.data;
    } catch (error) {
      console.error('Error deleting documentation:', error);
      throw error;
    }
  }
}

// Export a singleton instance
export const documentationService = new DocumentationService();