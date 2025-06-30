import api from './api';

export const chatService = {
  // Send a message to Kenobi (legacy endpoint)
  sendLegacyMessage: async (messageData) => {
    const response = await api.post('/kenobi/chat', messageData);
    return response.data;
  },

  // Enhanced chat with RAG capabilities
  sendMessage: async (messageData, options = {}) => {
    const { 
      repositoryId, 
      message, 
      context = {}, 
      sessionId = null, 
      branch = 'main', 
      useRag = true, 
      includeContext = true 
    } = messageData;

    // Use enhanced chat API endpoint
    const response = await api.post(`/chat/repository/${repositoryId}`, 
      { message, context },
      { 
        params: { 
          session_id: sessionId, 
          branch, 
          use_rag: useRag, 
          include_context: includeContext 
        } 
      }
    );
    return response;
  },

  // Get chat history
  getChatHistory: async (repositoryId, sessionId = null, branch = 'main', limit = 50) => {
    // Use enhanced chat history endpoint
    const response = await api.get(`/chat/repository/${repositoryId}/history`, {
      params: { 
        session_id: sessionId, 
        branch,
        limit
      }
    });
    return response;
  },

  // Clear chat history
  clearChatHistory: async (repositoryId, sessionId = null, branch = 'main') => {
    // Use enhanced clear history endpoint
    const response = await api.delete(`/chat/repository/${repositoryId}/history`, {
      params: { 
        session_id: sessionId, 
        branch 
      }
    });
    return response;
  },

  // Create a new chat session
  createChatSession: async (repositoryId, branch = 'main') => {
    const response = await api.post(`/chat/repository/${repositoryId}/session`, null, {
      params: { branch }
    });
    return response;
  },

  // Get chat sessions (legacy)
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