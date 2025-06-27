import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { FileText, Download, Eye, Search, Filter } from 'lucide-react';
import { repositoryService } from '../../services/repositories';
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
  const [functionalities, setFunctionalities] = useState(apiEndpoints);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedBranch, setSelectedBranch] = useState(branch || 'main');
  const [isGenerating, setIsGenerating] = useState(false);
  const [currentRepository, setRepository] = useState(repository);

  useEffect(() => {
    setFunctionalities(apiEndpoints);
  }, [apiEndpoints]);

  useEffect(() => {
    setSelectedBranch(branch);
  }, [branch]);

  const handleGenerateDocumentation = async () => {
    if (!repository || !onGenerateDocumentation) return;
    
    setIsGenerating(true);
    try {
      await onGenerateDocumentation(repository.id, selectedBranch);
    } catch (error) {
      console.error('Error generating documentation:', error);
    } finally {
      setIsGenerating(false);
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
    func.description?.toLowerCase().includes(searchTerm.toLowerCase())
  );

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
          <button className="bg-primary-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-primary-600">
            <Download className="w-4 h-4" />
            <span>Export Documentation</span>
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
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
              placeholder="Search by name or description"
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
            onChange={(e) => setSelectedBranch(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="main">main</option>
            <option value="develop">develop</option>
            <option value="master">master</option>
          </select>
        </div>
      </div>

      {/* Functionalities List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-500">
            <div className="col-span-4">Function Name</div>
            <div className="col-span-3">Type</div>
            <div className="col-span-3">File</div>
            <div className="col-span-2">Actions</div>
          </div>
        </div>
        
        <div className="divide-y divide-gray-200">
          {filteredFunctionalities.length > 0 ? (
            filteredFunctionalities.map((func, index) => (
              <FunctionalityRow key={index} functionality={func} />
            ))
          ) : (
            <div className="p-8 text-center text-gray-500">
              {searchTerm ? 'No functionalities match your search.' : 'No functionalities found in this repository.'}
            </div>
          )}
        </div>
      </div>

      {/* Summary */}
      {filteredFunctionalities.length > 0 && (
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-center">
            <div>
              <div className="text-2xl font-bold text-primary-600">{filteredFunctionalities.length}</div>
              <div className="text-sm text-gray-600">Total Functions</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-green-600">
                {filteredFunctionalities.filter(f => f.type === 'function').length}
              </div>
              <div className="text-sm text-gray-600">Functions</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-blue-600">
                {filteredFunctionalities.filter(f => f.type === 'class').length}
              </div>
              <div className="text-sm text-gray-600">Classes</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-purple-600">
                {filteredFunctionalities.filter(f => f.type === 'method').length}
              </div>
              <div className="text-sm text-gray-600">Methods</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const FunctionalityRow = ({ functionality }) => {
  return (
    <div className="px-6 py-4 grid grid-cols-12 gap-4 items-center hover:bg-gray-50">
      <div className="col-span-4">
        <div className="font-medium">{functionality.name}</div>
        {functionality.description && (
          <div className="text-sm text-gray-500 mt-1 truncate">
            {functionality.description}
          </div>
        )}
      </div>
      <div className="col-span-3">
        <StatusBadge status={functionality.type} />
      </div>
      <div className="col-span-3 text-gray-600 truncate">
        {functionality.file_path}
      </div>
      <div className="col-span-2 flex items-center space-x-2">
        <button
          className="text-primary-600 hover:text-primary-700 p-1"
          title="View details"
        >
          <Eye className="w-4 h-4" />
        </button>
        <button
          className="text-gray-600 hover:text-gray-700 p-1"
          title="View documentation"
        >
          <FileText className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default FunctionalitiesRegistry;