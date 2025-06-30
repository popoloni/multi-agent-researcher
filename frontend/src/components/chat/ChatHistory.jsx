import React, { useState, useEffect } from 'react';
import { Clock, Search, Trash2, MessageSquare, Code, Bot, User, Filter } from 'lucide-react';
import { chatService } from '../../services/chat';
import { messageContainsCode } from '../../utils/messageFormatter';

const ChatHistory = ({ 
  repositoryId, 
  branch = 'main',
  sessionId = null,
  onSelectMessage,
  onClearHistory
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSession, setSelectedSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    onlyCode: false,
    onlyUser: false,
    onlyAssistant: false
  });

  useEffect(() => {
    if (repositoryId) {
      loadChatHistory();
    }
  }, [repositoryId, branch, sessionId]);

  const loadChatHistory = async () => {
    if (!repositoryId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await chatService.getChatHistory(repositoryId, sessionId, branch);
      setMessages(response.data.messages || []);
    } catch (err) {
      console.error('Error loading chat history:', err);
      setError('Failed to load chat history');
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = async () => {
    if (!repositoryId) return;
    
    if (window.confirm('Are you sure you want to clear chat history?')) {
      try {
        await chatService.clearChatHistory(repositoryId, sessionId, branch);
        setMessages([]);
        if (onClearHistory) {
          onClearHistory();
        }
      } catch (err) {
        console.error('Error clearing history:', err);
        setError('Failed to clear history');
      }
    }
  };

  // Group messages by session (by day for now)
  const groupMessagesBySession = () => {
    const sessions = {};
    
    // Apply filters
    let filteredMessages = [...messages];
    
    if (filters.onlyCode) {
      filteredMessages = filteredMessages.filter(message => 
        messageContainsCode(message.content)
      );
    }
    
    if (filters.onlyUser) {
      filteredMessages = filteredMessages.filter(message => 
        message.role === 'user' || message.type === 'user'
      );
    }
    
    if (filters.onlyAssistant) {
      filteredMessages = filteredMessages.filter(message => 
        message.role === 'assistant' || message.type === 'assistant'
      );
    }
    
    // Apply search
    if (searchTerm) {
      filteredMessages = filteredMessages.filter(message =>
        message.content.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    
    // Group by date
    filteredMessages.forEach(message => {
      const date = new Date(message.timestamp).toDateString();
      if (!sessions[date]) {
        sessions[date] = [];
      }
      sessions[date].push(message);
    });

    return Object.entries(sessions).map(([date, sessionMessages]) => ({
      id: date,
      date,
      messages: sessionMessages,
      lastMessage: sessionMessages[sessionMessages.length - 1],
      messageCount: sessionMessages.length
    }));
  };

  const sessions = groupMessagesBySession();

  const formatTime = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return 'Today';
    } else if (date.toDateString() === yesterday.toDateString()) {
      return 'Yesterday';
    } else {
      return date.toLocaleDateString([], { 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  const toggleFilter = (filterName) => {
    setFilters(prev => ({
      ...prev,
      [filterName]: !prev[filterName]
    }));
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold mb-3">Chat History</h2>
        
        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
        
        {/* Filters */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => toggleFilter('onlyCode')}
            className={`text-xs px-2 py-1 rounded-full flex items-center space-x-1 ${
              filters.onlyCode 
                ? 'bg-blue-100 text-blue-700' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Code className="w-3 h-3" />
            <span>Code</span>
          </button>
          
          <button
            onClick={() => toggleFilter('onlyUser')}
            className={`text-xs px-2 py-1 rounded-full flex items-center space-x-1 ${
              filters.onlyUser 
                ? 'bg-blue-100 text-blue-700' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <User className="w-3 h-3" />
            <span>User</span>
          </button>
          
          <button
            onClick={() => toggleFilter('onlyAssistant')}
            className={`text-xs px-2 py-1 rounded-full flex items-center space-x-1 ${
              filters.onlyAssistant 
                ? 'bg-blue-100 text-blue-700' 
                : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            }`}
          >
            <Bot className="w-3 h-3" />
            <span>Assistant</span>
          </button>
          
          {(filters.onlyCode || filters.onlyUser || filters.onlyAssistant) && (
            <button
              onClick={() => setFilters({
                onlyCode: false,
                onlyUser: false,
                onlyAssistant: false
              })}
              className="text-xs px-2 py-1 rounded-full bg-red-100 text-red-700 hover:bg-red-200 flex items-center space-x-1"
            >
              <Filter className="w-3 h-3" />
              <span>Clear Filters</span>
            </button>
          )}
        </div>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        {loading ? (
          <div className="p-4 space-y-3">
            <div className="animate-pulse h-20 bg-gray-100 rounded-lg"></div>
            <div className="animate-pulse h-20 bg-gray-100 rounded-lg"></div>
          </div>
        ) : error ? (
          <div className="p-4 text-center text-red-600 bg-red-50 rounded-lg m-2">
            {error}
            <button 
              onClick={loadChatHistory}
              className="block mx-auto mt-2 text-sm bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded"
            >
              Retry
            </button>
          </div>
        ) : sessions.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p className="text-sm">
              {searchTerm || Object.values(filters).some(v => v) 
                ? 'No matching messages found' 
                : 'No chat history yet'}
            </p>
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`p-3 rounded-lg cursor-pointer transition-colors ${
                  selectedSession === session.id
                    ? 'bg-blue-50 border border-blue-200'
                    : 'hover:bg-gray-50'
                }`}
                onClick={() => setSelectedSession(
                  selectedSession === session.id ? null : session.id
                )}
              >
                {/* Session Header */}
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-900">
                    {formatDate(session.date)}
                  </span>
                  <div className="flex items-center space-x-2">
                    <span className="text-xs text-gray-500">
                      {session.messageCount} messages
                    </span>
                    <Clock className="w-3 h-3 text-gray-400" />
                  </div>
                </div>

                {/* Last Message Preview */}
                <div className="text-sm text-gray-600 truncate">
                  {(session.lastMessage.role === 'user' || session.lastMessage.type === 'user') 
                    ? 'You: ' 
                    : 'Kenobi: '
                  }
                  {session.lastMessage.content}
                </div>

                <div className="text-xs text-gray-400 mt-1">
                  {formatTime(session.lastMessage.timestamp)}
                </div>

                {/* Expanded Session Messages */}
                {selectedSession === session.id && (
                  <div className="mt-3 pt-3 border-t border-gray-200 space-y-2">
                    {session.messages.map((message) => (
                      <div
                        key={message.id}
                        className={`p-2 rounded text-xs cursor-pointer hover:bg-gray-100 ${
                          (message.role === 'user' || message.type === 'user')
                            ? 'bg-blue-50 text-blue-800' 
                            : 'bg-gray-50 text-gray-700'
                        }`}
                        onClick={(e) => {
                          e.stopPropagation();
                          if (onSelectMessage) {
                            onSelectMessage(message);
                          }
                        }}
                      >
                        <div className="font-medium mb-1 flex items-center justify-between">
                          <div>
                            {(message.role === 'user' || message.type === 'user') ? 'You' : 'Kenobi'} - {formatTime(message.timestamp)}
                          </div>
                          {messageContainsCode(message.content) && (
                            <Code className="w-3 h-3 text-blue-600" title="Contains code" />
                          )}
                        </div>
                        <div className="truncate">
                          {message.content}
                        </div>
                        {(message.repository_id || message.repository) && (
                          <div className="text-gray-500 mt-1">
                            📁 {message.repository_id || message.repository}
                            {(message.branch) && ` (${message.branch})`}
                          </div>
                        )}
                        {message.sources && message.sources.length > 0 && (
                          <div className="text-gray-500 mt-1">
                            🔍 {message.sources.length} source{message.sources.length !== 1 ? 's' : ''}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Footer Actions */}
      <div className="p-4 border-t border-gray-200">
        <button
          className="w-full flex items-center justify-center space-x-2 px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          onClick={handleClearHistory}
          disabled={loading || messages.length === 0}
        >
          <Trash2 className="w-4 h-4" />
          <span>Clear History</span>
        </button>
      </div>
    </div>
  );
};

export default ChatHistory;