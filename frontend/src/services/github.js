/**
 * GitHub API Service - Frontend client for GitHub operations
 */

import api from './api';

export const githubService = {
  /**
   * Search GitHub repositories
   * @param {string} query - Search query
   * @param {Object} filters - Search filters
   * @returns {Promise} Search results
   */
  searchRepositories: async (query, filters = {}) => {
    try {
      const params = {
        query,
        ...filters
      };
      
      const response = await api.get('/github/search', { params });
      return response.data;
    } catch (error) {
      console.error('GitHub search failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to search repositories');
    }
  },

  /**
   * Get detailed repository information
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @returns {Promise} Repository information
   */
  getRepositoryInfo: async (owner, repo) => {
    try {
      const response = await api.get(`/github/repositories/${owner}/${repo}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get repository info:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get repository information');
    }
  },

  /**
   * List repository branches
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @returns {Promise} List of branches
   */
  listBranches: async (owner, repo) => {
    try {
      const response = await api.get(`/github/repositories/${owner}/${repo}/branches`);
      return response.data;
    } catch (error) {
      console.error('Failed to list branches:', error);
      throw new Error(error.response?.data?.detail || 'Failed to list branches');
    }
  },

  /**
   * Clone a GitHub repository
   * @param {Object} repoData - Repository clone data
   * @returns {Promise} Clone result
   */
  cloneRepository: async (repoData) => {
    try {
      const response = await api.post('/github/repositories/clone', repoData);
      return response.data;
    } catch (error) {
      console.error('Repository clone failed:', error);
      throw new Error(error.response?.data?.detail || 'Failed to clone repository');
    }
  },

  /**
   * Get repository contents at a specific path
   * @param {string} owner - Repository owner
   * @param {string} repo - Repository name
   * @param {string} path - Path within repository
   * @param {string} branch - Branch name
   * @returns {Promise} Repository contents
   */
  getRepositoryContents: async (owner, repo, path = '', branch = 'main') => {
    try {
      const params = { path, branch };
      const response = await api.get(`/github/repositories/${owner}/${repo}/contents`, { params });
      return response.data;
    } catch (error) {
      console.error('Failed to get repository contents:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get repository contents');
    }
  },

  /**
   * Get user repositories
   * @param {string} username - GitHub username (optional)
   * @param {Object} options - Query options
   * @returns {Promise} List of repositories
   */
  getUserRepositories: async (username = null, options = {}) => {
    try {
      const params = {
        username,
        ...options
      };
      
      const response = await api.get('/github/user/repositories', { params });
      return response.data;
    } catch (error) {
      console.error('Failed to get user repositories:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get user repositories');
    }
  },

  /**
   * Get GitHub API rate limit status
   * @returns {Promise} Rate limit information
   */
  getRateLimit: async () => {
    try {
      const response = await api.get('/github/rate-limit');
      return response.data;
    } catch (error) {
      console.error('Failed to get rate limit:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get rate limit');
    }
  },

  /**
   * Get clone status for a repository
   * @param {string} repoId - Repository ID
   * @returns {Promise} Clone status
   */
  getCloneStatus: async (repoId) => {
    try {
      const response = await api.get(`/github/clone-status/${repoId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to get clone status:', error);
      throw new Error(error.response?.data?.detail || 'Failed to get clone status');
    }
  },

  /**
   * Cancel an ongoing clone operation
   * @param {string} repoId - Repository ID
   * @returns {Promise} Cancel result
   */
  cancelClone: async (repoId) => {
    try {
      const response = await api.post(`/github/clone-cancel/${repoId}`);
      return response.data;
    } catch (error) {
      console.error('Failed to cancel clone:', error);
      throw new Error(error.response?.data?.detail || 'Failed to cancel clone');
    }
  },

  /**
   * Parse GitHub URL to extract owner and repo
   * @param {string} url - GitHub repository URL
   * @returns {Object|null} Parsed owner and repo or null if invalid
   */
  parseGitHubUrl: (url) => {
    try {
      const patterns = [
        /github\.com\/([^\/]+)\/([^\/]+?)(?:\.git)?(?:\/.*)?$/,
        /^([^\/]+)\/([^\/]+)$/
      ];

      for (const pattern of patterns) {
        const match = url.match(pattern);
        if (match) {
          return {
            owner: match[1],
            repo: match[2].replace(/\.git$/, '')
          };
        }
      }

      return null;
    } catch (error) {
      console.error('Failed to parse GitHub URL:', error);
      return null;
    }
  },

  /**
   * Validate GitHub repository URL
   * @param {string} url - Repository URL
   * @returns {boolean} True if valid GitHub URL
   */
  isValidGitHubUrl: (url) => {
    const parsed = githubService.parseGitHubUrl(url);
    return parsed !== null;
  },

  /**
   * Format repository size in human-readable format
   * @param {number} sizeKB - Size in kilobytes
   * @returns {string} Formatted size
   */
  formatRepositorySize: (sizeKB) => {
    if (sizeKB < 1024) {
      return `${sizeKB} KB`;
    } else if (sizeKB < 1024 * 1024) {
      return `${(sizeKB / 1024).toFixed(1)} MB`;
    } else {
      return `${(sizeKB / (1024 * 1024)).toFixed(1)} GB`;
    }
  },

  /**
   * Format star count in human-readable format
   * @param {number} stars - Star count
   * @returns {string} Formatted star count
   */
  formatStarCount: (stars) => {
    if (stars < 1000) {
      return stars.toString();
    } else if (stars < 1000000) {
      return `${(stars / 1000).toFixed(1)}k`;
    } else {
      return `${(stars / 1000000).toFixed(1)}M`;
    }
  },

  /**
   * Get language color for display
   * @param {string} language - Programming language
   * @returns {string} Color hex code
   */
  getLanguageColor: (language) => {
    const colors = {
      JavaScript: '#f1e05a',
      TypeScript: '#2b7489',
      Python: '#3572A5',
      Java: '#b07219',
      'C++': '#f34b7d',
      'C#': '#239120',
      PHP: '#4F5D95',
      Ruby: '#701516',
      Go: '#00ADD8',
      Rust: '#dea584',
      Swift: '#ffac45',
      Kotlin: '#F18E33',
      Dart: '#00B4AB',
      HTML: '#e34c26',
      CSS: '#1572B6',
      Shell: '#89e051',
      PowerShell: '#012456',
      Dockerfile: '#384d54',
      Vue: '#2c3e50',
      React: '#61dafb'
    };

    return colors[language] || '#586069';
  }
};

export default githubService;