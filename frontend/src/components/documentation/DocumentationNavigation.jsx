import React from 'react';
import { FileText, Code, Box, BookOpen, Home, Search, ChevronRight } from 'lucide-react';

const DocumentationNavigation = ({ 
  repository, 
  selectedDocType = 'overview',
  onSelectDocType,
  documentationTypes = [],
  onSearch
}) => {
  // Default documentation types if none provided
  const docTypes = documentationTypes.length > 0 ? documentationTypes : [
    { id: 'overview', name: 'Overview', icon: <Home className="w-4 h-4" /> },
    { id: 'api', name: 'API Reference', icon: <Code className="w-4 h-4" /> },
    { id: 'architecture', name: 'Architecture', icon: <Box className="w-4 h-4" /> },
    { id: 'usage', name: 'Usage Guide', icon: <BookOpen className="w-4 h-4" /> }
  ];

  return (
    <div className="bg-white rounded-lg shadow mb-6">
      {/* Repository Info */}
      <div className="border-b border-gray-200 px-6 py-4">
        <h2 className="text-lg font-bold text-gray-800 truncate">
          {repository?.name || 'Repository Documentation'}
        </h2>
        {repository && (
          <div className="flex items-center text-sm text-gray-500 mt-1">
            <span className="truncate">{repository.url || repository.path}</span>
          </div>
        )}
      </div>

      {/* Breadcrumb */}
      <div className="border-b border-gray-200 px-6 py-2 flex items-center text-sm">
        <span className="text-gray-500">Documentation</span>
        <ChevronRight className="w-3 h-3 mx-1 text-gray-400" />
        <span className="text-primary-600 font-medium">
          {docTypes.find(dt => dt.id === selectedDocType)?.name || 'Overview'}
        </span>
      </div>

      {/* Documentation Types */}
      <div className="px-6 py-3">
        <div className="flex flex-wrap gap-2">
          {docTypes.map((docType) => (
            <button
              key={docType.id}
              onClick={() => onSelectDocType(docType.id)}
              className={`flex items-center px-3 py-2 rounded-md text-sm ${
                selectedDocType === docType.id
                  ? 'bg-primary-50 text-primary-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              <span className="mr-2">{docType.icon}</span>
              {docType.name}
            </button>
          ))}
        </div>
      </div>

      {/* Quick Search */}
      {onSearch && (
        <div className="border-t border-gray-200 px-6 py-3">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Quick search..."
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  onSearch(e.target.value);
                }
              }}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default DocumentationNavigation;