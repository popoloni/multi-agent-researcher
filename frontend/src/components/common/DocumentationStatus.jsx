import React from 'react';
import { Clock, CheckCircle, AlertTriangle, XCircle, RefreshCw } from 'lucide-react';

const DocumentationStatus = ({ 
  status = 'not_generated', 
  lastGenerated = null,
  qualityScore = null,
  missingTypes = [],
  onRefresh,
  size = 'md' // 'sm', 'md', 'lg'
}) => {
  // Status can be: 'not_generated', 'generating', 'generated', 'failed', 'outdated'
  
  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return null;
    
    const date = new Date(dateString);
    return date.toLocaleDateString(undefined, { 
      year: 'numeric', 
      month: 'short', 
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };
  
  // Calculate time since generation
  const getTimeSince = (dateString) => {
    if (!dateString) return null;
    
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    
    if (diffDays > 30) {
      return `${Math.floor(diffDays / 30)} months ago`;
    } else if (diffDays > 0) {
      return `${diffDays} days ago`;
    } else {
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
      if (diffHours > 0) {
        return `${diffHours} hours ago`;
      } else {
        const diffMinutes = Math.floor(diffMs / (1000 * 60));
        return `${diffMinutes} minutes ago`;
      }
    }
  };
  
  // Get status color
  const getStatusColor = () => {
    switch (status) {
      case 'generated':
        return 'text-green-500';
      case 'generating':
        return 'text-blue-500';
      case 'failed':
        return 'text-red-500';
      case 'outdated':
        return 'text-amber-500';
      default:
        return 'text-gray-500';
    }
  };
  
  // Get status icon
  const getStatusIcon = () => {
    switch (status) {
      case 'generated':
        return <CheckCircle className={`${getIconSize()} ${getStatusColor()}`} />;
      case 'generating':
        return <RefreshCw className={`${getIconSize()} ${getStatusColor()} animate-spin`} />;
      case 'failed':
        return <XCircle className={`${getIconSize()} ${getStatusColor()}`} />;
      case 'outdated':
        return <AlertTriangle className={`${getIconSize()} ${getStatusColor()}`} />;
      default:
        return <Clock className={`${getIconSize()} ${getStatusColor()}`} />;
    }
  };
  
  // Get status text
  const getStatusText = () => {
    switch (status) {
      case 'generated':
        return 'Documentation generated';
      case 'generating':
        return 'Generating documentation...';
      case 'failed':
        return 'Generation failed';
      case 'outdated':
        return 'Documentation outdated';
      default:
        return 'Not generated yet';
    }
  };
  
  // Get icon size based on component size
  const getIconSize = () => {
    switch (size) {
      case 'sm':
        return 'w-4 h-4';
      case 'lg':
        return 'w-6 h-6';
      default:
        return 'w-5 h-5';
    }
  };
  
  // Get text size based on component size
  const getTextSize = () => {
    switch (size) {
      case 'sm':
        return 'text-xs';
      case 'lg':
        return 'text-base';
      default:
        return 'text-sm';
    }
  };
  
  // Compact version (small)
  if (size === 'sm') {
    return (
      <div className="flex items-center">
        {getStatusIcon()}
        <span className={`ml-1 ${getTextSize()} ${getStatusColor()}`}>
          {getStatusText()}
        </span>
      </div>
    );
  }
  
  // Full version (medium or large)
  return (
    <div className="flex flex-col">
      <div className="flex items-center">
        {getStatusIcon()}
        <span className={`ml-2 font-medium ${getTextSize()} ${getStatusColor()}`}>
          {getStatusText()}
        </span>
        
        {onRefresh && (status === 'outdated' || status === 'failed' || status === 'not_generated') && (
          <button
            onClick={onRefresh}
            className="ml-auto text-primary-600 hover:text-primary-800"
            title="Regenerate documentation"
          >
            <RefreshCw className={size === 'lg' ? 'w-5 h-5' : 'w-4 h-4'} />
          </button>
        )}
      </div>
      
      {lastGenerated && (
        <div className={`mt-1 ${getTextSize() === 'text-xs' ? 'text-xs' : 'text-xs'} text-gray-500`}>
          Last updated: {getTimeSince(lastGenerated)}
        </div>
      )}
      
      {qualityScore !== null && (
        <div className="mt-1 flex items-center">
          <div className="w-full bg-gray-200 rounded-full h-1.5">
            <div 
              className={`h-1.5 rounded-full ${
                qualityScore >= 80 ? 'bg-green-500' : 
                qualityScore >= 50 ? 'bg-amber-500' : 
                'bg-red-500'
              }`}
              style={{ width: `${qualityScore}%` }}
            ></div>
          </div>
          <span className="ml-2 text-xs text-gray-500">{qualityScore}%</span>
        </div>
      )}
      
      {missingTypes.length > 0 && (
        <div className="mt-1 text-xs text-amber-600">
          Missing: {missingTypes.join(', ')}
        </div>
      )}
    </div>
  );
};

export default DocumentationStatus;