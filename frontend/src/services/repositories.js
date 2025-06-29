import api from './api';

// Utility function to clean up repository paths by removing temp folder prefixes
export const cleanRepositoryPath = (path) => {
  if (!path) return path;
  
  // Common temp directory patterns to remove
  const tempPrefixes = [
    '/tmp/kenobi/',
    '/tmp/kenobi_repos/',
    '/tmp/kenobi_repositories/',
    '/var/tmp/kenobi/',
    '/private/tmp/kenobi/',
    '/private/tmp/kenobi_repos/',
  ];
  
  // Remove temp prefixes
  for (const prefix of tempPrefixes) {
    if (path.startsWith(prefix)) {
      return path.substring(prefix.length);
    }
  }
  
  // If no temp prefix found, return original path
  return path;
};

/* 
Test examples:
cleanRepositoryPath('/tmp/kenobi_repos/my-repo') → 'my-repo'
cleanRepositoryPath('/tmp/kenobi/astropy') → 'astropy'
cleanRepositoryPath('/home/user/project') → '/home/user/project' (unchanged)
cleanRepositoryPath('https://github.com/user/repo') → 'https://github.com/user/repo' (unchanged)
*/

export const repositoryService = {
  // Get all repositories
  getRepositories: () => api.get('/kenobi/repositories'),
  
  // Add remote repository with extended timeout
  addRepository: (repositoryData) => 
    api.post('/kenobi/repositories/index', repositoryData, {
      timeout: 300000, // 5 minutes timeout for repository operations
      onUploadProgress: (progressEvent) => {
        // This won't show actual progress but prevents timeout during large uploads
        console.log('Repository operation in progress...');
      }
    }),
  
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