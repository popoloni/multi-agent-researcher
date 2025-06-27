import React, { useState, useEffect } from 'react';
import { ChevronDown, GitBranch, Folder } from 'lucide-react';

const RepositorySelector = ({ 
  repositories = [],
  selectedRepository, 
  selectedBranch, 
  onRepositoryChange, 
  onBranchChange 
}) => {
  const [branches, setBranches] = useState([]);
  const [loadingBranches, setLoadingBranches] = useState(false);
  const isLoading = false; // Since repositories are passed as props

  // Load branches when repository changes
  useEffect(() => {
    if (selectedRepository) {
      loadBranches(selectedRepository);
    } else {
      setBranches([]);
      onBranchChange('');
    }
  }, [selectedRepository]);

  const loadBranches = async (repositoryId) => {
    setLoadingBranches(true);
    try {
      const response = await fetch(`/kenobi/repositories/${repositoryId}/branches`);
      if (response.ok) {
        const data = await response.json();
        setBranches(data.branches || ['main', 'master', 'develop']);
        // Auto-select main or master if available
        const defaultBranch = data.branches?.find(b => ['main', 'master'].includes(b)) || data.branches?.[0] || 'main';
        onBranchChange(defaultBranch);
      } else {
        // Fallback to common branch names
        setBranches(['main', 'master', 'develop']);
        onBranchChange('main');
      }
    } catch (error) {
      console.error('Error loading branches:', error);
      setBranches(['main', 'master', 'develop']);
      onBranchChange('main');
    } finally {
      setLoadingBranches(false);
    }
  };

  const selectedRepo = repositories.find(repo => repo.id === selectedRepository);

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-4">
        {/* Repository Selector */}
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Repository
          </label>
          <div className="relative">
            <select
              value={selectedRepository}
              onChange={(e) => onRepositoryChange(e.target.value)}
              disabled={isLoading}
              className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed appearance-none"
            >
              <option value="">
                {isLoading ? 'Loading repositories...' : 'Select a repository'}
              </option>
              {repositories.map((repo) => (
                <option key={repo.id} value={repo.id}>
                  {repo.name} ({repo.language || 'Unknown'})
                </option>
              ))}
            </select>
            <Folder className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          </div>
        </div>

        {/* Branch Selector */}
        <div className="w-48">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Branch
          </label>
          <div className="relative">
            <select
              value={selectedBranch}
              onChange={(e) => onBranchChange(e.target.value)}
              disabled={!selectedRepository || loadingBranches}
              className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg bg-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed appearance-none"
            >
              <option value="">
                {loadingBranches ? 'Loading...' : 'Select branch'}
              </option>
              {branches.map((branch) => (
                <option key={branch} value={branch}>
                  {branch}
                </option>
              ))}
            </select>
            <GitBranch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
            <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          </div>
        </div>
      </div>

      {/* Repository Info */}
      {selectedRepo && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                <Folder className="w-4 h-4 text-blue-600" />
              </div>
              <div>
                <h3 className="font-medium text-blue-900">{selectedRepo.name}</h3>
                <div className="flex items-center space-x-4 text-sm text-blue-700">
                  <span>{selectedRepo.language || 'Unknown language'}</span>
                  <span>•</span>
                  <span>{selectedRepo.file_count} files</span>
                  <span>•</span>
                  <span>{selectedRepo.line_count?.toLocaleString()} lines</span>
                </div>
              </div>
            </div>
            {selectedRepo.indexed_at && (
              <div className="text-xs text-blue-600">
                Indexed: {new Date(selectedRepo.indexed_at).toLocaleDateString()}
              </div>
            )}
          </div>
          
          {selectedBranch && (
            <div className="mt-2 pt-2 border-t border-blue-200">
              <div className="flex items-center space-x-2 text-sm text-blue-700">
                <GitBranch className="w-4 h-4" />
                <span>Working on branch: <strong>{selectedBranch}</strong></span>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Help Text */}
      {!selectedRepository && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
          <p className="text-sm text-gray-600">
            💡 Select a repository to start chatting with Kenobi about your code. 
            Kenobi can help you understand functions, explain code patterns, and answer questions about your codebase.
          </p>
        </div>
      )}
    </div>
  );
};

export default RepositorySelector;