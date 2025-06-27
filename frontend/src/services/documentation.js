import api from './api';

export const documentationService = {
  // Get repository documentation
  getDocumentation: (repositoryId, branch = 'main') => 
    api.get(`/kenobi/repositories/${repositoryId}/documentation`, {
      params: { branch }
    }),
  
  // Generate documentation for repository
  generateDocumentation: (repositoryId, options = {}) => 
    api.post(`/kenobi/repositories/${repositoryId}/documentation`, options),
  
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