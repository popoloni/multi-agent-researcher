import React, { useState, useEffect } from 'react';
import { Plus, MessageSquare, Trash2, Clock } from 'lucide-react';
import { chatService } from '../../services/chat';

const SessionManager = ({ 
  repositoryId, 
  branch, 
  currentSessionId, 
  onSessionChange, 
  onNewSession 
}) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (repositoryId && branch) {
      loadSessions();
    }
  }, [repositoryId, branch]);

  const loadSessions = async () => {
    if (!repositoryId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await chatService.getChatHistory(repositoryId, null, branch);
      
      // Extract unique session IDs from the history
      const sessionData = response.data.sessions || [];
      setSessions(sessionData);
    } catch (err) {
      console.error('Error loading sessions:', err);
      setError('Failed to load chat sessions');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateSession = async () => {
    if (!repositoryId) return;
    
    setLoading(true);
    try {
      const response = await chatService.createChatSession(repositoryId, branch);
      const newSession = response.data;
      
      setSessions(prev => [newSession, ...prev]);
      
      if (onNewSession) {
        onNewSession(newSession.session_id);
      }
    } catch (err) {
      console.error('Error creating session:', err);
      setError('Failed to create new session');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation();
    if (!repositoryId || !sessionId) return;
    
    if (window.confirm('Are you sure you want to delete this chat session?')) {
      try {
        await chatService.clearChatHistory(repositoryId, sessionId, branch);
        setSessions(prev => prev.filter(s => s.session_id !== sessionId));
        
        if (currentSessionId === sessionId && sessions.length > 0) {
          // Select another session if the current one is deleted
          const nextSession = sessions.find(s => s.session_id !== sessionId);
          if (nextSession && onSessionChange) {
            onSessionChange(nextSession.session_id);
          }
        }
      } catch (err) {
        console.error('Error deleting session:', err);
        setError('Failed to delete session');
      }
    }
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

  if (!repositoryId || !branch) {
    return null;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-medium text-gray-700">Chat Sessions</h3>
        <button
          onClick={handleCreateSession}
          disabled={loading}
          className="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 px-2 py-1 rounded flex items-center space-x-1"
        >
          <Plus className="w-3 h-3" />
          <span>New Session</span>
        </button>
      </div>

      {error && (
        <div className="text-xs text-red-600 bg-red-50 p-2 rounded">
          {error}
        </div>
      )}

      <div className="space-y-1 max-h-64 overflow-y-auto">
        {loading && sessions.length === 0 ? (
          <div className="animate-pulse space-y-2">
            <div className="h-10 bg-gray-100 rounded"></div>
            <div className="h-10 bg-gray-100 rounded"></div>
          </div>
        ) : sessions.length === 0 ? (
          <div className="text-xs text-gray-500 bg-gray-50 p-2 rounded text-center">
            No sessions found. Create a new session to start chatting.
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.session_id}
              onClick={() => onSessionChange(session.session_id)}
              className={`p-2 rounded-lg cursor-pointer flex items-center justify-between ${
                currentSessionId === session.session_id
                  ? 'bg-blue-50 border border-blue-200'
                  : 'hover:bg-gray-50 border border-transparent'
              }`}
            >
              <div className="flex items-center space-x-2">
                <MessageSquare className={`w-4 h-4 ${
                  currentSessionId === session.session_id ? 'text-blue-600' : 'text-gray-400'
                }`} />
                <div>
                  <div className="text-sm font-medium">
                    {session.name || `Session ${session.session_id.substring(0, 8)}`}
                  </div>
                  <div className="text-xs text-gray-500 flex items-center space-x-1">
                    <Clock className="w-3 h-3" />
                    <span>{formatDate(session.created_at)}</span>
                  </div>
                </div>
              </div>
              
              <button
                onClick={(e) => handleDeleteSession(session.session_id, e)}
                className="text-gray-400 hover:text-red-600 p-1 rounded-full hover:bg-red-50"
              >
                <Trash2 className="w-3 h-3" />
              </button>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default SessionManager;