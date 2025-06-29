import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Settings, User, MessageSquare, Home, FolderOpen, Globe } from 'lucide-react';
import NotificationBadge from '../common/NotificationBadge';

const Header = () => {
  const location = useLocation();
  // Using NotificationContext via the NotificationBadge component
  
  const isActive = (path) => location.pathname === path;
  
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-8">
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-primary-600 rounded flex items-center justify-center">
              <span className="text-white text-sm font-bold">M</span>
            </div>
            <span className="text-xl font-semibold">Multi-Agent Researcher</span>
          </Link>
          
          {/* Navigation */}
          <nav className="flex items-center space-x-6">
            <Link 
              to="/" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                isActive('/') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <Home className="w-4 h-4" />
              <span>Dashboard</span>
            </Link>
            <Link 
              to="/repositories" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                isActive('/repositories') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <FolderOpen className="w-4 h-4" />
              <span>Repositories</span>
            </Link>
            <Link 
              to="/chat" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                isActive('/chat') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <MessageSquare className="w-4 h-4" />
              <span>Kenobi Chat</span>
            </Link>
            <Link 
              to="/research" 
              className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-colors ${
                isActive('/research') 
                  ? 'bg-primary-100 text-primary-700' 
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <Globe className="w-4 h-4" />
              <span>Web Research</span>
            </Link>
          </nav>
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <NotificationBadge />
          <div className="flex items-center space-x-2">
            <User className="w-4 h-4" />
            <span>Research Agent</span>
          </div>
          <div className="flex items-center space-x-2">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;