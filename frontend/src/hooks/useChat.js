import { useState, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import { chatService } from '../services/chat';

export const useChat = (repositoryId, branch = 'main') => {
  const [messages, setMessages] = useState([]);
  const queryClient = useQueryClient();

  // Send message mutation
  const sendMessageMutation = useMutation(
    ({ message, repositoryId, branch }) => 
      chatService.sendMessage(message, repositoryId, branch),
    {
      onSuccess: (data, variables) => {
        // Add user message
        const userMessage = {
          id: Date.now(),
          type: 'user',
          content: variables.message,
          timestamp: new Date().toISOString(),
          repository: variables.repositoryId,
          branch: variables.branch
        };

        // Add bot response
        const botMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: data.response,
          timestamp: new Date().toISOString(),
          sources: data.sources || [],
          repository: variables.repositoryId,
          branch: variables.branch
        };

        setMessages(prev => [...prev, userMessage, botMessage]);
        
        // Invalidate chat history
        queryClient.invalidateQueries(['chatHistory', repositoryId, branch]);
      },
      onError: (error, variables) => {
        // Add user message
        const userMessage = {
          id: Date.now(),
          type: 'user',
          content: variables.message,
          timestamp: new Date().toISOString(),
          repository: variables.repositoryId,
          branch: variables.branch
        };

        // Add error message
        const errorMessage = {
          id: Date.now() + 1,
          type: 'bot',
          content: 'Sorry, I encountered an error while processing your request. Please try again.',
          timestamp: new Date().toISOString(),
          isError: true
        };

        setMessages(prev => [...prev, userMessage, errorMessage]);
      }
    }
  );

  // Chat history query
  const chatHistoryQuery = useQuery(
    ['chatHistory', repositoryId, branch],
    () => chatService.getChatHistory(repositoryId, branch),
    {
      enabled: !!repositoryId,
      onSuccess: (data) => {
        if (data.messages) {
          setMessages(data.messages);
        }
      }
    }
  );

  // Clear chat history mutation
  const clearHistoryMutation = useMutation(
    ({ repositoryId, branch }) => 
      chatService.clearChatHistory(repositoryId, branch),
    {
      onSuccess: () => {
        setMessages([]);
        queryClient.invalidateQueries(['chatHistory', repositoryId, branch]);
      }
    }
  );

  // Repository branches query
  const branchesQuery = useQuery(
    ['repositoryBranches', repositoryId],
    () => chatService.getRepositoryBranches(repositoryId),
    {
      enabled: !!repositoryId
    }
  );

  // Send message function
  const sendMessage = useCallback((message) => {
    if (!message.trim() || !repositoryId) return;
    
    sendMessageMutation.mutate({
      message,
      repositoryId,
      branch
    });
  }, [repositoryId, branch, sendMessageMutation]);

  // Clear chat function
  const clearChat = useCallback(() => {
    if (repositoryId) {
      clearHistoryMutation.mutate({ repositoryId, branch });
    } else {
      setMessages([]);
    }
  }, [repositoryId, branch, clearHistoryMutation]);

  return {
    messages,
    sendMessage,
    clearChat,
    isLoading: sendMessageMutation.isLoading,
    isError: sendMessageMutation.isError,
    error: sendMessageMutation.error,
    branches: branchesQuery.data?.branches || [],
    isBranchesLoading: branchesQuery.isLoading,
    chatHistory: chatHistoryQuery.data,
    isChatHistoryLoading: chatHistoryQuery.isLoading
  };
};

export const useChatSessions = () => {
  return useQuery(
    ['chatSessions'],
    chatService.getChatSessions
  );
};

export const useChatSearch = (query, repositoryId = null, branch = null) => {
  return useQuery(
    ['chatSearch', query, repositoryId, branch],
    () => chatService.searchChatHistory(query, repositoryId, branch),
    {
      enabled: !!query && query.length > 2
    }
  );
};