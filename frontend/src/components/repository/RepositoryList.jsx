import React, { useState } from 'react';
import { Plus, Trash2, Eye, FileText, ExternalLink, GitBranch } from 'lucide-react';
import { Link } from 'react-router-dom';
import RepositoryForm from './RepositoryForm';
import StatusBadge from '../common/StatusBadge';
import { cleanRepositoryPath } from '../../services/repositories';

const RepositoryList = ({ repositories, onAddRepository, onDeleteRepository, isLoading }) => {
  const [showAddForm, setShowAddForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [keywordFilter, setKeywordFilter] = useState('');

  const filteredRepositories = repositories.filter(repo => 
    repo.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (keywordFilter === '' || repo.keywords?.includes(keywordFilter))
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Repository</h1>
        <button
          onClick={() => setShowAddForm(true)}
          className="bg-primary-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-primary-600"
        >
          <Plus className="w-4 h-4" />
          <span>Add remote repository</span>
        </button>
      </div>

      {/* Search and Filter */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Repository name
          </label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Enter repository name"
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Keyword
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={keywordFilter}
              onChange={(e) => setKeywordFilter(e.target.value)}
              placeholder="Enter keyword"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <button 
              onClick={() => setKeywordFilter('')}
              className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Repository Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-500">
            <div className="col-span-3">Name</div>
            <div className="col-span-4">Path/URL</div>
            <div className="col-span-2">Status</div>
            <div className="col-span-3">Actions</div>
          </div>
        </div>
        
        <div className="divide-y divide-gray-200">
          {isLoading ? (
            <div className="p-8 text-center">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
              <p className="mt-2 text-gray-500">Loading repositories...</p>
            </div>
          ) : filteredRepositories.length > 0 ? (
            filteredRepositories.map((repo) => (
              <RepositoryRow 
                key={repo.id} 
                repository={repo} 
                onDelete={onDeleteRepository}
              />
            ))
          ) : (
            <div className="p-8 text-center text-gray-500">
              No repositories found. Add your first repository to get started.
            </div>
          )}
        </div>
      </div>

      {/* Pagination */}
      {filteredRepositories.length > 0 && (
        <div className="flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <button className="w-8 h-8 rounded bg-primary-500 text-white flex items-center justify-center">
              1
            </button>
          </div>
          <div className="text-sm text-gray-500">
            1 - {filteredRepositories.length} of {repositories.length}
          </div>
        </div>
      )}

      {/* Add Repository Modal */}
      {showAddForm && (
        <RepositoryForm
          onSubmit={(data) => {
            onAddRepository(data);
            setShowAddForm(false);
          }}
          onCancel={() => setShowAddForm(false)}
        />
      )}
    </div>
  );
};

const RepositoryRow = ({ repository, onDelete }) => {
  const [showDebug, setShowDebug] = useState(false);
  
  // Extract GitHub URL from repository name
  const getGitHubUrl = (repo) => {
    if (repo.url && repo.url.startsWith('http')) {
      return repo.url;
    }
    
    // Try to extract GitHub URL from repository name
    // Expected format: reponame_username_timestamp or similar
    const name = repo.name || '';
    if (name.includes('_')) {
      const parts = name.split('_');
      if (parts.length >= 2) {
        const repoName = parts[0];
        const username = parts[1];
        return `https://github.com/${username}/${repoName}`;
      }
    }
    
    // Fallback: show the repository name as a display value
    return `Repository: ${cleanRepositoryPath(name)}`;
  };

  // Get display URL
  const displayUrl = getGitHubUrl(repository);
  const isExternalUrl = displayUrl.startsWith('http');
  const isInferredGitHub = isExternalUrl && !repository.url;
  
  return (
    <div 
      className="px-6 py-4 grid grid-cols-12 gap-4 items-center hover:bg-gray-50"
    >
      <div className="col-span-3">
        <div className="font-medium">{cleanRepositoryPath(repository.name)}</div>
        {repository.branch && (
          <div className="flex items-center text-sm text-gray-500 mt-1">
            <GitBranch className="w-3 h-3 mr-1" />
            {repository.branch}
          </div>
        )}
      </div>
      <div className="col-span-4 text-gray-600">
        <div className="flex items-center space-x-2">
          <span className="truncate">{displayUrl}</span>
          {isInferredGitHub && (
            <span className="text-xs text-gray-400 flex-shrink-0">(inferred)</span>
          )}
          {isExternalUrl && (
            <a
              href={displayUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-700 flex-shrink-0"
              title={isInferredGitHub ? "Open inferred GitHub URL (may not be accurate)" : "Open in new tab"}
            >
              <ExternalLink className="w-3 h-3" />
            </a>
          )}
        </div>
        <button 
          onClick={() => setShowDebug(!showDebug)}
          className="text-xs text-gray-500 hover:text-gray-700 mt-1"
        >
          {showDebug ? 'Hide Debug' : 'Show Debug'}
        </button>
        {showDebug && (
          <div className="mt-2 text-xs text-gray-500 bg-gray-50 p-2 rounded">
            <div><strong>Local Path:</strong></div>
            <div className="break-all font-mono">{repository.local_path || repository.path}</div>
            <div className="mt-1"><strong>Repository ID:</strong></div>
            <div className="font-mono">{repository.id}</div>
          </div>
        )}
      </div>
      <div className="col-span-2">
        <StatusBadge status={repository.status || 'indexed'} />
      </div>
      <div className="col-span-3 flex items-center space-x-2">
        <Link
          to={`/repositories/${repository.id}/functionalities`}
          className="text-gray-600 hover:text-gray-700 p-1"
          title="View functionalities"
        >
          <Eye className="w-4 h-4" />
        </Link>
        <Link
          to={`/repositories/${repository.id}/documentation`}
          className="text-gray-600 hover:text-gray-700 p-1"
          title="View documentation"
        >
          <FileText className="w-4 h-4" />
        </Link>
        <button
          onClick={() => onDelete(repository.id)}
          className="text-red-600 hover:text-red-700 p-1"
          title="Delete repository (removes local files and database records)"
        >
          <Trash2 className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default RepositoryList;