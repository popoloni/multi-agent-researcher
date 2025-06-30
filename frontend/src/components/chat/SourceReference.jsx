import React, { useState } from 'react';
import { File, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';

const SourceReference = ({ sources, onViewSource }) => {
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  // Group sources by file path
  const groupedSources = sources.reduce((acc, source) => {
    const filePath = source.file_path || source.file || 'unknown';
    if (!acc[filePath]) {
      acc[filePath] = [];
    }
    acc[filePath].push(source);
    return acc;
  }, {});

  return (
    <div className="mt-3 pt-2 border-t border-gray-200">
      <div 
        className="flex items-center justify-between cursor-pointer text-xs text-gray-500 mb-1"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center space-x-1">
          <File className="w-3 h-3" />
          <span>{sources.length} source{sources.length !== 1 ? 's' : ''}</span>
        </div>
        {expanded ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </div>

      {expanded && (
        <div className="space-y-2 mt-2">
          {Object.entries(groupedSources).map(([filePath, fileSources]) => (
            <div key={filePath} className="bg-gray-50 rounded-md p-2 text-xs">
              <div className="font-medium text-gray-700 mb-1 flex items-center justify-between">
                <div className="truncate flex-1" title={filePath}>
                  {filePath.split('/').pop()}
                </div>
                <button
                  onClick={() => onViewSource(filePath, fileSources)}
                  className="text-blue-600 hover:text-blue-800 ml-2 flex items-center"
                >
                  <ExternalLink className="w-3 h-3 mr-1" />
                  View
                </button>
              </div>
              
              <div className="text-gray-600">
                {fileSources.map((source, index) => {
                  const lineInfo = source.line_number || source.line || '';
                  const sourceType = source.source_type || 'code';
                  const relevance = source.relevance || '';
                  
                  return (
                    <div key={index} className="flex items-center space-x-2">
                      <span className="text-gray-400">•</span>
                      <span>
                        {lineInfo && `Line ${lineInfo}`}
                        {sourceType && ` (${sourceType})`}
                        {relevance && ` - Relevance: ${relevance}`}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SourceReference;