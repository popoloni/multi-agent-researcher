import React, { useState } from 'react';
import { Clock, Search, Trash2, MessageSquare } from 'lucide-react';

const ChatHistory = ({ messages, onSelectMessage }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSession, setSelectedSession] = useState(null);

  // Group messages by session (by day for now)
  const groupMessagesBySession = () => {
    const sessions = {};
    
    messages.forEach(message => {
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
  
  const filteredSessions = sessions.filter(session =>
    session.messages.some(message =>
      message.content.toLowerCase().includes(searchTerm.toLowerCase())
    )
  );

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

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold mb-3">Chat History</h2>
        
        {/* Search */}
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search conversations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Sessions List */}
      <div className="flex-1 overflow-y-auto">
        {filteredSessions.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <MessageSquare className="w-8 h-8 mx-auto mb-2 text-gray-300" />
            <p className="text-sm">
              {searchTerm ? 'No conversations found' : 'No chat history yet'}
            </p>
          </div>
        ) : (
          <div className="space-y-1 p-2">
            {filteredSessions.map((session) => (
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
                  {session.lastMessage.type === 'user' ? 'You: ' : 'Kenobi: '}
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
                          message.type === 'user' 
                            ? 'bg-blue-50 text-blue-800' 
                            : 'bg-gray-50 text-gray-700'
                        }`}
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectMessage(message);
                        }}
                      >
                        <div className="font-medium mb-1">
                          {message.type === 'user' ? 'You' : 'Kenobi'} - {formatTime(message.timestamp)}
                        </div>
                        <div className="truncate">
                          {message.content}
                        </div>
                        {message.repository && (
                          <div className="text-gray-500 mt-1">
                            📁 {message.repository}
                            {message.branch && ` (${message.branch})`}
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
          onClick={() => {
            if (window.confirm('Are you sure you want to clear all chat history?')) {
              // Clear history logic would go here
              console.log('Clear all history');
            }
          }}
        >
          <Trash2 className="w-4 h-4" />
          <span>Clear All History</span>
        </button>
      </div>
    </div>
  );
};

export default ChatHistory;