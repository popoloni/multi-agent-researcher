import api from './api';

export const chatService = {
  // Send a message to Kenobi
  sendMessage: async (message, repositoryId, branch = 'main') => {
    const response = await api.post('/kenobi/chat', {
      message,
      repository_id: repositoryId,
      branch
    });
    return response.data;
  },

  // Get chat history
  getChatHistory: async (repositoryId, branch = 'main') => {
    const response = await api.get('/kenobi/chat/history', {
      params: { repository_id: repositoryId, branch }
    });
    return response.data;
  },

  // Clear chat history
  clearChatHistory: async (repositoryId, branch = 'main') => {
    const response = await api.delete('/kenobi/chat/history', {
      data: { repository_id: repositoryId, branch }
    });
    return response.data;
  },

  // Get chat sessions
  getChatSessions: async () => {
    const response = await api.get('/kenobi/chat/sessions');
    return response.data;
  },

  // Search in chat history
  searchChatHistory: async (query, repositoryId = null, branch = null) => {
    const response = await api.get('/kenobi/chat/search', {
      params: { 
        query, 
        repository_id: repositoryId, 
        branch 
      }
    });
    return response.data;
  },

  // Get repository branches for chat context
  getRepositoryBranches: async (repositoryId) => {
    const response = await api.get(`/kenobi/repositories/${repositoryId}/branches`);
    return response.data;
  },

  // Get repository context for chat
  getRepositoryContext: async (repositoryId, branch = 'main') => {
    const response = await api.get(`/kenobi/repositories/${repositoryId}/context`, {
      params: { branch }
    });
    return response.data;
  },

  // Get available models
  getAvailableModels: () => 
    api.get('/models/info'),
  
  // Check Ollama status
  getOllamaStatus: () => 
    api.get('/ollama/status'),
};