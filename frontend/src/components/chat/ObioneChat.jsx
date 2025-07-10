import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, RotateCcw, Settings, Bot, User, Database, Code, Zap } from 'lucide-react';
import ChatHistory from './ChatHistory';
import RepositorySelector from './RepositorySelector';
import RepositoryContext from './RepositoryContext';
import SessionManager from './SessionManager';
import MessageContent from './MessageContent';
import { chatService } from '../../services/chat';
import { repositoryService } from '../../services/repositories';

const ObioneChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedRepository, setSelectedRepository] = useState('');
  const [selectedBranch, setSelectedBranch] = useState('main');
  const [repositories, setRepositories] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [ollamaStatus, setOllamaStatus] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [useRag, setUseRag] = useState(true);
  const [includeContext, setIncludeContext] = useState(true);
  const [showSettings, setShowSettings] = useState(false);
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

  // Create a new session when repository changes
  useEffect(() => {
    if (selectedRepository) {
      createNewSession();
    }
  }, [selectedRepository, selectedBranch]);

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

  const createNewSession = async () => {
    if (!selectedRepository) return;
    
    try {
      const response = await chatService.createChatSession(selectedRepository, selectedBranch);
      setSessionId(response.data.session_id);
      setMessages([]);
    } catch (error) {
      console.error('Error creating chat session:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedRepository) return;

    const userMessage = {
      id: Date.now(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString(),
      repository_id: selectedRepository,
      branch: selectedBranch
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Use enhanced chat API with RAG
      const response = await chatService.sendMessage({
        repositoryId: selectedRepository,
        message: inputMessage,
        context: {},
        sessionId: sessionId,
        branch: selectedBranch,
        useRag: useRag,
        includeContext: includeContext
      });

      const botMessage = {
        id: Date.now() + 1,
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        sources: response.data.sources || [],
        context_used: response.data.context_used
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        role: 'assistant',
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
    if (window.confirm('Are you sure you want to clear the current chat?')) {
      setMessages([]);
      createNewSession();
    }
  };

  const loadChatHistory = async () => {
    if (!selectedRepository || !sessionId) return;
    
    try {
      const response = await chatService.getChatHistory(selectedRepository, sessionId, selectedBranch);
      setMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error loading chat history:', error);
    }
  };

  const handleViewSource = (filePath, sources) => {
    // This would open a modal or panel to view the source file
    console.log('View source:', filePath, sources);
    // In a real implementation, you would fetch the file content and display it
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Left Sidebar */}
      <div className="w-80 bg-white border-r border-gray-200 flex flex-col shadow-sm">
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center space-x-2">
              <Bot className="w-6 h-6 text-blue-600" />
              <h1 className="text-xl font-bold text-gray-900">Obione Chat</h1>
            </div>
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="p-2 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full transition-colors"
              title="Settings"
            >
              <Settings className="w-5 h-5" />
            </button>
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
          
          {/* Settings Panel */}
          {showSettings && (
            <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
              <h3 className="text-sm font-medium text-gray-700 mb-2">Chat Settings</h3>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Database className="w-4 h-4 text-blue-600" />
                    <span className="text-sm">Use RAG</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input 
                      type="checkbox" 
                      className="sr-only peer"
                      checked={useRag}
                      onChange={() => setUseRag(!useRag)}
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
                
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <MessageSquare className="w-4 h-4 text-blue-600" />
                    <span className="text-sm">Include Chat Context</span>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input 
                      type="checkbox" 
                      className="sr-only peer"
                      checked={includeContext}
                      onChange={() => setIncludeContext(!includeContext)}
                    />
                    <div className="w-9 h-5 bg-gray-200 peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600"></div>
                  </label>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Chat Controls */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex space-x-2">
            <button
              onClick={() => setShowHistory(!showHistory)}
              className={`flex-1 px-3 py-2 rounded-lg flex items-center justify-center space-x-2 ${
                showHistory 
                  ? 'bg-blue-100 text-blue-700' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>History</span>
            </button>
            <button
              onClick={clearChat}
              className="flex-1 bg-gray-100 text-gray-700 px-3 py-2 rounded-lg flex items-center justify-center space-x-2 hover:bg-gray-200"
              disabled={messages.length === 0}
            >
              <RotateCcw className="w-4 h-4" />
              <span>Clear</span>
            </button>
          </div>
        </div>

        {/* Repository Context */}
        <div className="p-4 border-b border-gray-200">
          <RepositoryContext 
            repositoryId={selectedRepository}
            branch={selectedBranch}
          />
        </div>

        {/* Session Manager */}
        <div className="p-4 border-b border-gray-200 flex-1 overflow-y-auto">
          <SessionManager
            repositoryId={selectedRepository}
            branch={selectedBranch}
            currentSessionId={sessionId}
            onSessionChange={setSessionId}
            onNewSession={createNewSession}
          />
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Chat Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 ? (
            <div className="text-center py-12">
              <Bot className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Welcome to Obione Chat
              </h3>
              <p className="text-gray-600 max-w-md mx-auto">
                Ask questions about your repository code, get explanations, and explore your codebase with AI assistance.
              </p>
              {!selectedRepository && (
                <p className="text-red-600 mt-4">
                  Please select a repository to start chatting.
                </p>
              )}
              
              {selectedRepository && (
                <div className="mt-6 max-w-md mx-auto text-left bg-blue-50 p-4 rounded-lg border border-blue-200">
                  <h4 className="font-medium text-blue-800 mb-2 flex items-center">
                    <Zap className="w-4 h-4 mr-1" />
                    Try asking:
                  </h4>
                  <ul className="space-y-2 text-sm text-blue-700">
                    <li className="hover:bg-blue-100 p-1 rounded cursor-pointer">
                      "Explain the main functionality of this repository"
                    </li>
                    <li className="hover:bg-blue-100 p-1 rounded cursor-pointer">
                      "What are the key components in this codebase?"
                    </li>
                    <li className="hover:bg-blue-100 p-1 rounded cursor-pointer">
                      "Show me how error handling works in this project"
                    </li>
                    <li className="hover:bg-blue-100 p-1 rounded cursor-pointer">
                      "Find all API endpoints in this codebase"
                    </li>
                  </ul>
                </div>
              )}
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${(message.role === 'user' || message.type === 'user') ? 'justify-end' : 'justify-start'}`}
              >
                <div className={`max-w-3xl flex space-x-3 ${
                  (message.role === 'user' || message.type === 'user') ? 'flex-row-reverse space-x-reverse' : ''
                }`}>
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center shadow-sm ${
                    (message.role === 'user' || message.type === 'user')
                      ? 'bg-blue-600 text-white' 
                      : 'bg-gray-100 text-gray-600'
                  }`}>
                    {(message.role === 'user' || message.type === 'user') ? (
                      <User className="w-4 h-4" />
                    ) : (
                      <Bot className="w-4 h-4" />
                    )}
                  </div>
                  <div className={`rounded-lg px-4 py-3 shadow-sm ${
                    (message.role === 'user' || message.type === 'user')
                      ? 'bg-blue-600 text-white'
                      : message.isError
                      ? 'bg-red-50 text-red-800 border border-red-200'
                      : 'bg-white text-gray-900 border border-gray-200'
                  }`}>
                    <MessageContent 
                      message={message}
                      onViewSource={handleViewSource}
                    />
                    
                    {/* Context Used Indicator */}
                    {message.context_used && (
                      <div className="mt-1 text-xs text-blue-600 flex items-center">
                        <Database className="w-3 h-3 mr-1" />
                        <span>Used conversation context</span>
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
                <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center shadow-sm">
                  <Bot className="w-4 h-4 text-gray-600" />
                </div>
                <div className="bg-white border border-gray-200 rounded-lg px-4 py-3 shadow-sm">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                      <div className="w-2 h-2 bg-blue-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                    </div>
                    <span className="text-sm text-gray-500 ml-2">Obione is thinking...</span>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Message Input */}
        <div className="border-t border-gray-200 p-4 bg-white">
          <div className="flex space-x-3">
            <div className="flex-1">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={selectedRepository ? "Ask Obione about your code..." : "Select a repository first..."}
                disabled={!selectedRepository || isLoading}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none shadow-sm transition-all"
                rows="2"
              />
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || !selectedRepository || isLoading}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2 transition-colors shadow-sm"
            >
              <Send className="w-4 h-4" />
              <span>Send</span>
            </button>
          </div>
          
          {/* RAG Status Indicator */}
          <div className="mt-2 flex items-center justify-end space-x-4 text-xs text-gray-500">
            <div className="flex items-center space-x-1">
              <Database className="w-3 h-3" />
              <span>RAG: {useRag ? 'Enabled' : 'Disabled'}</span>
            </div>
            <div className="flex items-center space-x-1">
              <MessageSquare className="w-3 h-3" />
              <span>Context: {includeContext ? 'Included' : 'Excluded'}</span>
            </div>
            {sessionId && (
              <div className="flex items-center space-x-1">
                <Code className="w-3 h-3" />
                <span>Session: {sessionId.substring(0, 8)}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Chat History Sidebar */}
      {showHistory && (
        <div className="w-80 border-l border-gray-200 bg-white">
          <ChatHistory
            repositoryId={selectedRepository}
            branch={selectedBranch}
            sessionId={sessionId}
            onSelectMessage={(message) => {
              // Scroll to message or highlight it
              console.log('Selected message:', message);
            }}
            onClearHistory={clearChat}
          />
        </div>
      )}
    </div>
  );
};

export default ObioneChat;