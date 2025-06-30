import React, { useState, useEffect } from 'react';
import { Folder, GitBranch, FileText, Code, Database, Info, ChevronDown, ChevronUp } from 'lucide-react';
import { chatService } from '../../services/chat';

const RepositoryContext = ({ repositoryId, branch }) => {
  const [context, setContext] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    if (repositoryId && branch) {
      loadRepositoryContext();
    }
  }, [repositoryId, branch]);

  const loadRepositoryContext = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await chatService.getRepositoryContext(repositoryId, branch);
      setContext(response.data);
    } catch (err) {
      console.error('Error loading repository context:', err);
      setError('Failed to load repository context');
    } finally {
      setLoading(false);
    }
  };

  if (!repositoryId || !branch) {
    return null;
  }

  if (loading) {
    return (
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 animate-pulse">
        <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
        <div className="h-3 bg-gray-200 rounded w-1/2 mb-1"></div>
        <div className="h-3 bg-gray-200 rounded w-2/3"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-sm text-red-600">
        {error}
      </div>
    );
  }

  if (!context) {
    return null;
  }

  return (
    <div className="bg-blue-50 border border-blue-200 rounded-lg overflow-hidden">
      {/* Header */}
      <div 
        className="p-3 flex items-center justify-between cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center space-x-2">
          <Info className="w-4 h-4 text-blue-600" />
          <span className="font-medium text-blue-900">Repository Context</span>
        </div>
        {expanded ? (
          <ChevronUp className="w-4 h-4 text-blue-600" />
        ) : (
          <ChevronDown className="w-4 h-4 text-blue-600" />
        )}
      </div>

      {/* Content */}
      {expanded && (
        <div className="p-3 pt-0 border-t border-blue-200">
          <div className="space-y-3 text-sm">
            {/* Basic Info */}
            <div className="flex items-start space-x-3">
              <Folder className="w-4 h-4 text-blue-600 mt-0.5" />
              <div>
                <div className="font-medium text-blue-900">Repository</div>
                <div className="text-blue-700">{context.name || repositoryId}</div>
                {context.description && (
                  <div className="text-blue-600 text-xs mt-1">{context.description}</div>
                )}
              </div>
            </div>

            {/* Branch */}
            <div className="flex items-start space-x-3">
              <GitBranch className="w-4 h-4 text-blue-600 mt-0.5" />
              <div>
                <div className="font-medium text-blue-900">Branch</div>
                <div className="text-blue-700">{branch}</div>
              </div>
            </div>

            {/* Files */}
            {context.file_count && (
              <div className="flex items-start space-x-3">
                <FileText className="w-4 h-4 text-blue-600 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-900">Files</div>
                  <div className="text-blue-700">
                    {context.file_count.toLocaleString()} files
                    {context.line_count && ` (${context.line_count.toLocaleString()} lines)`}
                  </div>
                </div>
              </div>
            )}

            {/* Languages */}
            {context.languages && context.languages.length > 0 && (
              <div className="flex items-start space-x-3">
                <Code className="w-4 h-4 text-blue-600 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-900">Languages</div>
                  <div className="text-blue-700 flex flex-wrap gap-1">
                    {context.languages.map((lang, index) => (
                      <span key={index} className="bg-blue-100 px-2 py-0.5 rounded text-xs">
                        {lang}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Vector DB Status */}
            {context.indexed_at && (
              <div className="flex items-start space-x-3">
                <Database className="w-4 h-4 text-blue-600 mt-0.5" />
                <div>
                  <div className="font-medium text-blue-900">Knowledge Base</div>
                  <div className="text-blue-700">
                    Indexed: {new Date(context.indexed_at).toLocaleString()}
                    {context.vector_count && ` (${context.vector_count.toLocaleString()} vectors)`}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default RepositoryContext;