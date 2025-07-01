import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { FileText, ExternalLink, Eye, Search, Filter, List, TreePine, ChevronDown, ChevronRight, Folder, File } from 'lucide-react';
import { repositoryService, cleanRepositoryPath } from '../../services/repositories';
import LoadingSpinner from '../common/LoadingSpinner';
import StatusBadge from '../common/StatusBadge';

const FunctionalitiesRegistry = ({ 
  repository, 
  branch, 
  apiEndpoints = [], 
  onGenerateDocumentation,
  onBranchChange 
}) => {
  const { repositoryId } = useParams();
  const navigate = useNavigate();
  const [functionalities, setFunctionalities] = useState(apiEndpoints);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBranch, setSelectedBranch] = useState(branch || 'main');
  const [viewMode, setViewMode] = useState('hierarchical'); // 'hierarchical' or 'flat'
  const [expandedFiles, setExpandedFiles] = useState(new Set());
  const [currentRepository, setRepository] = useState(repository);

  useEffect(() => {
    setFunctionalities(apiEndpoints);
    // Auto-expand all files by default
    const allFiles = [...new Set(apiEndpoints.map(func => func.file_path))];
    setExpandedFiles(new Set(allFiles));
  }, [apiEndpoints]);

  useEffect(() => {
    setSelectedBranch(branch);
  }, [branch]);

  const handleGoToDocumentation = () => {
    if (repository?.id) {
      navigate(`/repositories/${repository.id}/documentation`);
    }
  };

  const handleBranchChange = (newBranch) => {
    setSelectedBranch(newBranch);
    if (onBranchChange) {
      onBranchChange(newBranch);
    }
  };

  const loadData = async () => {
    if (!repositoryId) return;
    
    setIsLoading(true);
    setError(null);
    try {
      const response = await repositoryService.getRepositoryFunctionalities(repositoryId);
      setFunctionalities(response.data.functionalities || []);
    } catch (err) {
      setError(err.message || 'Failed to load functionalities');
    } finally {
      setIsLoading(false);
    }
  };

  const filteredFunctionalities = functionalities.filter(func =>
    func.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    func.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    func.file_path?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Group functionalities by file path
  const groupedFunctionalities = filteredFunctionalities.reduce((acc, func) => {
    // Better handling of missing file paths
    let filePath = func.file_path || func.file || 'Unknown File';
    
    // If we still have "Unknown File", try to create a meaningful grouping
    if (filePath === 'Unknown File' && func.element_type) {
      filePath = `Unknown File (${func.element_type}s)`;
    }
    
    if (!acc[filePath]) {
      acc[filePath] = [];
    }
    acc[filePath].push(func);
    return acc;
  }, {});

  // Sort files alphabetically and sort functions within each file
  const sortedFiles = Object.keys(groupedFunctionalities).sort();
  sortedFiles.forEach(filePath => {
    groupedFunctionalities[filePath].sort((a, b) => {
      // Sort by type first (classes, then functions, then methods), then by name
      const typeOrder = { 'class': 0, 'function': 1, 'method': 2, 'variable': 3 };
      const aTypeOrder = typeOrder[a.element_type] ?? 4;
      const bTypeOrder = typeOrder[b.element_type] ?? 4;
      
      if (aTypeOrder !== bTypeOrder) {
        return aTypeOrder - bTypeOrder;
      }
      return a.name.localeCompare(b.name);
    });
  });

  const toggleFileExpansion = (filePath) => {
    const newExpanded = new Set(expandedFiles);
    if (newExpanded.has(filePath)) {
      newExpanded.delete(filePath);
    } else {
      newExpanded.add(filePath);
    }
    setExpandedFiles(newExpanded);
  };

  const handleViewSource = (functionality) => {
    if (!repository) {
      console.warn('Repository information not available');
      return;
    }

    // Try multiple ways to get the GitHub URL
    const githubUrl = repository.github_metadata?.html_url || 
                     repository.github_url || 
                     repository.html_url ||
                     repository.clone_url?.replace('.git', '');

    if (!githubUrl) {
      console.warn('GitHub URL not available for this repository');
      return;
    }

    const filePath = functionality.file_path || functionality.file;
    
    // If no file path, just open the repository
    if (!filePath || filePath.startsWith('Unknown File')) {
      window.open(githubUrl, '_blank');
      return;
    }

    // Create GitHub link to specific line
    if (functionality.start_line) {
      const fullUrl = `${githubUrl}/blob/${selectedBranch}/${filePath}#L${functionality.start_line}`;
      window.open(fullUrl, '_blank');
    } else {
      // Fallback to file without line number
      const fullUrl = `${githubUrl}/blob/${selectedBranch}/${filePath}`;
      window.open(fullUrl, '_blank');
    }
  };

  const handleViewDocumentation = (functionality) => {
    if (repository?.id) {
      // Navigate to documentation page with API reference section and search for the function
      navigate(`/repositories/${repository.id}/documentation?type=api&search=${encodeURIComponent(functionality.name)}`);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <LoadingSpinner size="lg" />
        <span className="ml-3 text-gray-600">Loading functionalities...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error loading functionalities: {error}</p>
        <button 
          onClick={loadData}
          className="mt-2 text-red-600 hover:text-red-800 underline"
        >
          Try again
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Temporary Debug Information */}
      {process.env.NODE_ENV === 'development' && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm">
          <details>
            <summary className="cursor-pointer font-medium text-yellow-800">
              Debug Info - Functionalities Data (Click to expand)
            </summary>
            <div className="mt-2 space-y-2">
              <div><strong>Total functionalities:</strong> {functionalities.length}</div>
              <div><strong>Filtered functionalities:</strong> {filteredFunctionalities.length}</div>
              <div><strong>Files found:</strong> {sortedFiles.length}</div>
              <div><strong>Repository data available:</strong> {repository ? 'Yes' : 'No'}</div>
              {repository && (
                <div><strong>GitHub URL:</strong> {repository.github_metadata?.html_url || 'Not available'}</div>
              )}
              <div><strong>Sample functionality:</strong></div>
              <pre className="text-xs bg-gray-100 p-2 rounded overflow-auto max-h-32">
                {JSON.stringify(functionalities[0], null, 2)}
              </pre>
            </div>
          </details>
        </div>
      )}

      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-2xl font-bold">Functionalities Registry</h1>
          {repository && (
            <p className="text-gray-600 mt-1">
              Repository: <span className="font-medium">{repository.name}</span>
            </p>
          )}
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={handleGoToDocumentation}
            className="bg-primary-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-primary-600"
          >
            <FileText className="w-4 h-4" />
            <span>Go to Documentation</span>
          </button>
        </div>
      </div>

      {/* Filters and View Options */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Search functionalities
          </label>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by name, description, or file"
              className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Branch
          </label>
          <select
            value={selectedBranch}
            onChange={(e) => handleBranchChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="main">main</option>
            <option value="develop">develop</option>
            <option value="master">master</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            View Mode
          </label>
          <div className="flex rounded-lg border border-gray-300 overflow-hidden">
            <button
              onClick={() => setViewMode('hierarchical')}
              className={`flex items-center px-3 py-2 text-sm ${
                viewMode === 'hierarchical' 
                  ? 'bg-primary-500 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <TreePine className="w-4 h-4 mr-1" />
              Tree
            </button>
            <button
              onClick={() => setViewMode('flat')}
              className={`flex items-center px-3 py-2 text-sm ${
                viewMode === 'flat' 
                  ? 'bg-primary-500 text-white' 
                  : 'bg-white text-gray-700 hover:bg-gray-50'
              }`}
            >
              <List className="w-4 h-4 mr-1" />
              Flat
            </button>
          </div>
        </div>

        <div className="flex items-end">
          <button
            onClick={() => {
              if (expandedFiles.size === sortedFiles.length) {
                setExpandedFiles(new Set());
              } else {
                setExpandedFiles(new Set(sortedFiles));
              }
            }}
            className="px-3 py-2 text-sm border border-gray-300 rounded-lg hover:bg-gray-50"
          >
            {expandedFiles.size === sortedFiles.length ? 'Collapse All' : 'Expand All'}
          </button>
        </div>
      </div>

      {/* Functionalities List */}
      <div className="bg-white rounded-lg shadow">
        {viewMode === 'hierarchical' ? (
          <HierarchicalView 
            sortedFiles={sortedFiles}
            groupedFunctionalities={groupedFunctionalities}
            expandedFiles={expandedFiles}
            toggleFileExpansion={toggleFileExpansion}
            onViewSource={handleViewSource}
            onViewDocumentation={handleViewDocumentation}
            searchTerm={searchTerm}
          />
        ) : (
          <FlatView 
            functionalities={filteredFunctionalities.sort((a, b) => {
              // Sort by file, then by type, then by name
              const fileCompare = (a.file_path || '').localeCompare(b.file_path || '');
              if (fileCompare !== 0) return fileCompare;
              
              const typeOrder = { 'class': 0, 'function': 1, 'method': 2, 'variable': 3 };
              const aTypeOrder = typeOrder[a.element_type] ?? 4;
              const bTypeOrder = typeOrder[b.element_type] ?? 4;
              
              if (aTypeOrder !== bTypeOrder) {
                return aTypeOrder - bTypeOrder;
              }
              return a.name.localeCompare(b.name);
            })}
            onViewSource={handleViewSource}
            onViewDocumentation={handleViewDocumentation}
            searchTerm={searchTerm}
          />
        )}
      </div>

      {/* Summary */}
      {filteredFunctionalities.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary-600">{filteredFunctionalities.length}</div>
              <div className="text-sm text-gray-600">Total Items</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {filteredFunctionalities.filter(f => f.element_type === 'function').length}
              </div>
              <div className="text-sm text-gray-600">Functions</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {filteredFunctionalities.filter(f => f.element_type === 'class').length}
              </div>
              <div className="text-sm text-gray-600">Classes</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {filteredFunctionalities.filter(f => f.element_type === 'method').length}
              </div>
              <div className="text-sm text-gray-600">Methods</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-orange-600">
                {sortedFiles.length}
              </div>
              <div className="text-sm text-gray-600">Files</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const HierarchicalView = ({ 
  sortedFiles, 
  groupedFunctionalities, 
  expandedFiles, 
  toggleFileExpansion,
  onViewSource,
  onViewDocumentation,
  searchTerm 
}) => {
  if (sortedFiles.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        {searchTerm ? 'No functionalities match your search.' : 'No functionalities found in this repository.'}
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-200">
      {sortedFiles.map((filePath) => (
        <div key={filePath}>
          {/* File Header */}
          <div 
            className="px-6 py-3 bg-gray-50 hover:bg-gray-100 cursor-pointer flex items-center justify-between"
            onClick={() => toggleFileExpansion(filePath)}
          >
            <div className="flex items-center">
              {expandedFiles.has(filePath) ? (
                <ChevronDown className="w-4 h-4 text-gray-500 mr-2" />
              ) : (
                <ChevronRight className="w-4 h-4 text-gray-500 mr-2" />
              )}
              <File className="w-4 h-4 text-blue-500 mr-2" />
              <span className="font-medium text-gray-800">{filePath}</span>
              <span className="ml-2 text-sm text-gray-500">
                ({groupedFunctionalities[filePath].length} items)
              </span>
            </div>
          </div>

          {/* File Contents */}
          {expandedFiles.has(filePath) && (
            <div className="bg-white">
              {groupedFunctionalities[filePath].map((func, index) => (
                <FunctionalityRow 
                  key={`${filePath}-${index}`}
                  functionality={func}
                  onViewSource={onViewSource}
                  onViewDocumentation={onViewDocumentation}
                  showFile={false}
                />
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

const FlatView = ({ 
  functionalities, 
  onViewSource, 
  onViewDocumentation,
  searchTerm 
}) => {
  if (functionalities.length === 0) {
    return (
      <div className="p-8 text-center text-gray-500">
        {searchTerm ? 'No functionalities match your search.' : 'No functionalities found in this repository.'}
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-gray-50">
        <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-500">
          <div className="col-span-3">Function Name</div>
          <div className="col-span-2">Type</div>
          <div className="col-span-4">File</div>
          <div className="col-span-1">Line</div>
          <div className="col-span-2">Actions</div>
        </div>
      </div>
      
      {/* Content */}
      <div className="divide-y divide-gray-200">
        {functionalities.map((func, index) => (
          <FunctionalityRow 
            key={index}
            functionality={func}
            onViewSource={onViewSource}
            onViewDocumentation={onViewDocumentation}
            showFile={true}
          />
        ))}
      </div>
    </div>
  );
};

const FunctionalityRow = ({ 
  functionality, 
  onViewSource, 
  onViewDocumentation, 
  showFile = true 
}) => {
  const getTypeColor = (type) => {
    const colors = {
      'function': 'bg-green-100 text-green-800',
      'class': 'bg-blue-100 text-blue-800',
      'method': 'bg-purple-100 text-purple-800',
      'variable': 'bg-orange-100 text-orange-800'
    };
    return colors[type] || 'bg-gray-100 text-gray-800';
  };

  if (showFile) {
    return (
      <div className="px-6 py-4 grid grid-cols-12 gap-4 items-center hover:bg-gray-50">
        <div className="col-span-3">
          <div className="font-medium text-gray-900">{functionality.name}</div>
          {functionality.description && (
            <div className="text-sm text-gray-500 mt-1 line-clamp-2">
              {functionality.description}
            </div>
          )}
        </div>
        <div className="col-span-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getTypeColor(functionality.element_type)}`}>
            {functionality.element_type}
          </span>
        </div>
        <div className="col-span-4 text-gray-600 text-sm">
          <div className="truncate" title={functionality.file_path}>
            {functionality.file_path}
          </div>
        </div>
        <div className="col-span-1 text-gray-500 text-sm">
          {functionality.start_line && `L${functionality.start_line}`}
        </div>
        <div className="col-span-2 flex items-center space-x-2">
          <button
            onClick={() => onViewSource(functionality)}
            className="text-primary-600 hover:text-primary-700 p-1 rounded hover:bg-primary-50"
            title="View source code"
          >
            <Eye className="w-4 h-4" />
          </button>
          <button
            onClick={() => onViewDocumentation(functionality)}
            className="text-gray-600 hover:text-gray-700 p-1 rounded hover:bg-gray-50"
            title="View documentation"
          >
            <FileText className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  } else {
    return (
      <div className="px-8 py-3 flex items-center justify-between hover:bg-gray-50 border-l-4 border-transparent hover:border-primary-200">
        <div className="flex-1">
          <div className="flex items-center">
            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium mr-3 ${getTypeColor(functionality.element_type)}`}>
              {functionality.element_type}
            </span>
            <span className="font-medium text-gray-900">{functionality.name}</span>
            {functionality.start_line && (
              <span className="ml-2 text-sm text-gray-500">L{functionality.start_line}</span>
            )}
          </div>
          {functionality.description && (
            <div className="text-sm text-gray-500 mt-1 line-clamp-2">
              {functionality.description}
            </div>
          )}
        </div>
        <div className="flex items-center space-x-2 ml-4">
          <button
            onClick={() => onViewSource(functionality)}
            className="text-primary-600 hover:text-primary-700 p-1 rounded hover:bg-primary-50"
            title="View source code"
          >
            <Eye className="w-4 h-4" />
          </button>
          <button
            onClick={() => onViewDocumentation(functionality)}
            className="text-gray-600 hover:text-gray-700 p-1 rounded hover:bg-gray-50"
            title="View documentation"
          >
            <FileText className="w-4 h-4" />
          </button>
        </div>
      </div>
    );
  }
};

const FunctionalityItem = ({ functionality, level = 0 }) => {
  const [isExpanded, setIsExpanded] = useState(false);
  
  // Clean the path for display
  const displayPath = functionality.path ? cleanRepositoryPath(functionality.path) : functionality.name;
  
  return (
    <div className={`pl-${level * 4}`}>
      <div className="flex items-center py-2">
        <button
          onClick={() => setIsExpanded(!isExpanded)}
          className="flex items-center text-gray-700 hover:text-gray-900"
        >
          {functionality.children?.length > 0 && (
            <span className="mr-2">{isExpanded ? '▼' : '▶'}</span>
          )}
          <span className="font-medium">{displayPath}</span>
        </button>
        {functionality.items && (
          <span className="ml-2 text-sm text-gray-500">
            ({functionality.items} items)
          </span>
        )}
      </div>
      {isExpanded && functionality.children?.map((child, index) => (
        <FunctionalityItem
          key={index}
          functionality={child}
          level={level + 1}
        />
      ))}
    </div>
  );
};

export default FunctionalitiesRegistry;