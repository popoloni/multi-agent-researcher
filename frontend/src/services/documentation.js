import api from './api';

class DocumentationService {
  constructor() {
    this.cache = new Map();
  }

  // Get documentation generation status
  async getDocumentationStatus(repositoryId, taskId) {
    return api.get(`/kenobi/repositories/${repositoryId}/documentation/status/${taskId}`);
  }

  // Poll documentation status until complete
  async pollDocumentationStatus(repositoryId, taskId, progressCallback) {
    let retries = 0;
    const maxRetries = 60; // 5 minutes with 5-second intervals
    
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
        
        await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
        retries++;
      } catch (error) {
        console.error('Error polling documentation status:', error);
        throw error;
      }
    }
    
    throw new Error('Documentation generation timed out');
  }

  // Search documentation
  async searchDocumentation(repositoryId, query, branch = 'main') {
    return api.get(`/kenobi/repositories/${repositoryId}/documentation/search`, {
      params: { query, branch }
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

    // Get from API
    try {
      console.log('Fetching from API');
      const response = await api.get(`/kenobi/repositories/${repositoryId}/documentation?branch=${branch}`);
      
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

  // Generate documentation
  async generateDocumentation(repositoryId, options = {}) {
    try {
      const response = await api.post(`/kenobi/repositories/${repositoryId}/documentation`, options);
      return response;
    } catch (error) {
      console.error('Error generating documentation:', error);
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