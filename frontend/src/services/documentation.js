import api from './api';

export const documentationService = {
  // Get repository documentation
  getDocumentation: (repositoryId, branch = 'main') => 
    api.get(`/kenobi/repositories/${repositoryId}/documentation`, {
      params: { branch }
    }),
  
  // Generate documentation for repository (Async)
  generateDocumentation: (repositoryId, options = {}) => 
    api.post(`/kenobi/repositories/${repositoryId}/documentation`, options),
  
  // Get documentation generation status
  getDocumentationStatus: (repositoryId, taskId) => 
    api.get(`/kenobi/repositories/${repositoryId}/documentation/status/${taskId}`),
  
  // Poll documentation generation status with progress callback
  pollDocumentationStatus: async (repositoryId, taskId, onProgress) => {
    const pollInterval = 2000; // Poll every 2 seconds
    const maxAttempts = 150; // Maximum 5 minutes (150 * 2 seconds)
    let attempts = 0;
    
    return new Promise((resolve, reject) => {
      const poll = async () => {
        try {
          attempts++;
          
          const response = await api.get(`/kenobi/repositories/${repositoryId}/documentation/status/${taskId}`);
          const status = response.data;
          
          // Call progress callback if provided
          if (onProgress) {
            onProgress(status);
          }
          
          // Check if completed
          if (status.status === 'completed') {
            resolve(status);
            return;
          }
          
          // Check if failed
          if (status.status === 'failed') {
            reject(new Error(status.error || 'Documentation generation failed'));
            return;
          }
          
          // Check if max attempts reached
          if (attempts >= maxAttempts) {
            reject(new Error('Documentation generation timed out'));
            return;
          }
          
          // Continue polling if still processing
          if (status.status === 'processing') {
            setTimeout(poll, pollInterval);
          } else {
            reject(new Error(`Unknown status: ${status.status}`));
          }
          
        } catch (error) {
          reject(error);
        }
      };
      
      // Start polling
      poll();
    });
  },
  
  // Get API endpoints documentation
  getApiDocumentation: (repositoryId, branch = 'main') => 
    api.get(`/kenobi/repositories/${repositoryId}/api-docs`, {
      params: { branch }
    }),
  
  // Get code analysis
  getCodeAnalysis: (repositoryId, branch = 'main') => 
    api.get(`/kenobi/repositories/${repositoryId}/analysis`, {
      params: { branch }
    }),
  
  // Search in documentation
  searchDocumentation: (repositoryId, query, branch = 'main') => 
    api.get(`/kenobi/repositories/${repositoryId}/documentation/search`, {
      params: { query, branch }
    }),
};