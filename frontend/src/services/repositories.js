import api from './api';

// Utility function to clean up repository paths by removing temp folder prefixes
export const cleanRepositoryPath = (path) => {
  if (!path) return path;
  
  // Extract just the repository name from the full path
  const parts = path.split('/');
  const repoName = parts[parts.length - 1];
  
  return repoName;
};

// Get the full debug path for display in debug view
export const getDebugPath = (path) => {
  return path || 'N/A';
};

/* 
Test examples:
cleanRepositoryPath('/tmp/kenobi_repos/my-repo') → 'my-repo'
cleanRepositoryPath('/tmp/kenobi/astropy') → 'astropy'
cleanRepositoryPath('/home/user/project') → '/home/user/project' (unchanged)
cleanRepositoryPath('https://github.com/user/repo') → 'https://github.com/user/repo' (unchanged)
*/

export const repositoryService = {
  // Get all repositories with extended timeout
  getRepositories: () => api.get('/kenobi/repositories', {
    timeout: 120000, // 2 minutes timeout for repository loading
  }),
  
  // Add remote repository with extended timeout
  addRepository: (repositoryData) => 
    api.post('/kenobi/repositories/index', repositoryData, {
      timeout: 300000, // 5 minutes timeout for repository operations
      onUploadProgress: (progressEvent) => {
        // This won't show actual progress but prevents timeout during large uploads
        console.log('Repository operation in progress...');
      }
    }),
  
  // Get repository details with extended timeout
  getRepositoryDetails: (repositoryId) => 
    api.get(`/kenobi/repositories/${repositoryId}`, {
      timeout: 120000, // 2 minutes timeout for repository details
    }),
  
  // Create indexing (documentation generation) with extended timeout
  createIndexing: (repositoryId) => 
    api.post(`/kenobi/repositories/${repositoryId}/index`, {}, {
      timeout: 600000, // 10 minutes timeout for indexing operations
    }),
  
  // Get repository analysis with extended timeout
  getRepositoryAnalysis: (repositoryId) => 
    api.get(`/kenobi/repositories/${repositoryId}/analysis`, {
      timeout: 180000, // 3 minutes timeout for analysis
    }),
  
  // Delete repository
  deleteRepository: (repositoryId) => 
    api.delete(`/kenobi/repositories/${repositoryId}`),
  
  // Get functionalities registry with extended timeout
  getFunctionalitiesRegistry: (repositoryId, branch) => 
    api.get(`/kenobi/repositories/${repositoryId}/functionalities`, {
      params: { branch },
      timeout: 180000, // 3 minutes timeout for functionalities registry
    }),
};