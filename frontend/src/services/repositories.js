import api from './api';

export const repositoryService = {
  // Get all repositories
  getRepositories: () => api.get('/kenobi/repositories'),
  
  // Add remote repository
  addRepository: (repositoryData) => 
    api.post('/kenobi/repositories/index', repositoryData),
  
  // Get repository details
  getRepositoryDetails: (repositoryId) => 
    api.get(`/kenobi/repositories/${repositoryId}`),
  
  // Create indexing (documentation generation)
  createIndexing: (repositoryId) => 
    api.post(`/kenobi/repositories/${repositoryId}/index`),
  
  // Get repository analysis
  getRepositoryAnalysis: (repositoryId) => 
    api.get(`/kenobi/repositories/${repositoryId}/analysis`),
  
  // Delete repository
  deleteRepository: (repositoryId) => 
    api.delete(`/kenobi/repositories/${repositoryId}`),
  
  // Get functionalities registry
  getFunctionalitiesRegistry: (repositoryId, branch) => 
    api.get(`/kenobi/repositories/${repositoryId}/functionalities`, {
      params: { branch }
    }),
};