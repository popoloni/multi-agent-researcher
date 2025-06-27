import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, RotateCcw, Settings, Bot, User } from 'lucide-react';
import ChatHistory from './ChatHistory';
import RepositorySelector from './RepositorySelector';
import { chatService } from '../../services/chat';
import { repositoryService } from '../../services/repositories';

const KenobiChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedRepository, setSelectedRepository] = useState('');
  const [selectedBranch, setSelectedBranch] = useState('main');
  const [repositories, setRepositories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [ollamaStatus, setOllamaStatus] = useState(null);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    loadRepositories();
    checkOllamaStatus();
  }, []);

  const loadRepositories = async () => {
    try {
      const response = await repositoryService.getRepositories();
      setRepositories(response.data.repositories || []);
      if (response.data.repositories?.length > 0) {
        setSelectedRepository(response.data.repositories[0].id);
      }
    } catch (error) {
      console.error('Error loading repositories:', error);
    }
  };

  const checkOllamaStatus = async () => {
    try {
      const response = await chatService.getOllamaStatus();
      setOllamaStatus(response.data);
    } catch (error) {
      console.error('Error checking Ollama status:', error);
      setOllamaStatus({ status: 'error', message: 'Ollama not available' });
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedRepository) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
      repository: selectedRepository,
      branch: selectedBranch
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage({
        message: inputMessage,
        repository_id: selectedRepository,
        branch: selectedBranch,
        conversation_history: messages.slice(-10) // Last 10 messages for context
      });

      const botMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        sources: response.data.sources || []
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  const loadChatHistory = async () => {
    if (!selectedRepository) return;
    
    try {
      const response = await chatService.getChatHistory(selectedRepository);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center space-x-2 mb-4">
            <Bot className="w-6 h-6 text-primary-500" />
            <h1 className="text-xl font-bold">Kenobi Chat</h1>
          </div>
          
          {/* Ollama Status */}
          <div className="mb-4">
            <div className="flex items-center space-x-2">
              <div className={`w-2 h-2 rounded-full ${
                ollamaStatus?.status === 'running' ? 'bg-green-500' : 'bg-red-500'
              }`} />
              <span className="text-sm text-gray-600">
                {ollamaStatus?.status === 'running' ? 'Ollama Connected' : 'Ollama Disconnected'}
              </span>
            </div>
          </div>

          {/* Repository Selector */}
          <RepositorySelector
            repositories={repositories}
            selectedRepository={selectedRepository}
            selectedBranch={selectedBranch}
            onRepositoryChange={setSelectedRepository}
            onBranchChange={setSelectedBranch}
          />
        </div>

        {/* Chat Controls */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex space-x-2">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className="flex-1 bg-gray-100 text-gray-700 px-3 py-2 rounded-lg flex items-center justify-center space-x-2 hover:bg-gray-200"
            >
              <MessageSquare className="w-4 h-4" />
              <span>History</span>
            </button>
            <button
              onClick={clearChat}
              className="flex-1 bg-gray-100 text-gray-700 px-3 py-2 rounded-lg flex items-center justify-center space-x-2 hover:bg-gray-200"
            >
              <RotateCcw className="w-4 h-4" />
              <span>Clear</span>
            </button>
          </div>
        </div>

        {/* Chat History */}
        {showHistory && (
          <div className="flex-1 overflow-y-auto">
            <ChatHistory 
              repositoryId={selectedRepository}
              onLoadHistory={loadChatHistory}
            />
          </div>
        )}
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">

        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Welcome to Kenobi Chat
              </h3>
              <p className="text-gray-600 max-w-md mx-auto">
                Ask questions about your repository code, get explanations, and explore your codebase with AI assistance.
              </p>
              {!selectedRepository && (
                <p className="text-red-600 mt-4">
                  Please select a repository to start chatting.
                </p>
              )}
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-3xl flex space-x-3 ${
                  message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                    message.type === 'user' 
                      ? 'bg-primary-500 text-white' 
                      : 'bg-gray-200 text-gray-600'
                  }`}>
                    {message.type === 'user' ? (
                      <User className="w-4 h-4" />
                    ) : (
                      <Bot className="w-4 h-4" />
                    )}
                  </div>
                  <div className={`rounded-lg px-4 py-2 ${
                    message.type === 'user'
                      ? 'bg-primary-500 text-white'
                      : message.isError
                      ? 'bg-red-50 text-red-800 border border-red-200'
                      : 'bg-white text-gray-900 border border-gray-200'
                  }`}>
                    <div className="whitespace-pre-wrap">{message.content}</div>
                    {message.sources && message.sources.length > 0 && (
                      <div className="mt-2 pt-2 border-t border-gray-200">
                        <p className="text-xs text-gray-500 mb-1">Sources:</p>
                        {message.sources.map((source, index) => (
                          <div key={index} className="text-xs text-gray-600">
                            {source.file}:{source.line}
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="text-xs text-gray-400 mt-1">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              </div>
            ))
          )}
          
          {isLoading && (
            <div className="flex justify-start">
              <div className="max-w-3xl flex space-x-3">
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center">
                  <Bot className="w-4 h-4 text-gray-600" />
                </div>
                <div className="bg-white border border-gray-200 rounded-lg px-4 py-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex space-x-4">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={selectedRepository ? "Ask Kenobi about your code..." : "Select a repository first..."}
                disabled={!selectedRepository || isLoading}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 resize-none"
                rows="3"
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || !selectedRepository || isLoading}
              className="bg-primary-500 text-white px-6 py-3 rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Send className="w-4 h-4" />
              <span>Send</span>
            </button>
          </div>
        </div>
      </div>

      {/* Chat History Sidebar */}
      {showHistory && (
        <div className="w-80 border-l border-gray-200 bg-white">
          <ChatHistory
            messages={messages}
            onSelectMessage={(message) => {
              // Scroll to message or highlight it
              console.log('Selected message:', message);
            }}
          />
        </div>
      )}
    </div>
  );
};

export default KenobiChat;