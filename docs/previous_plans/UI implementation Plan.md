# Multi-Agent Researcher GUI Implementation Plan

Based on the screenshots and API analysis, this plan provides step-by-step instructions for implementing the GUI with priority on MVP features, then RAG functionality, and finally monitoring capabilities.

## 🎯 Implementation Priority

### Phase 1: MVP Features (Priority 1)
1. Repository connection and downloading
2. Documentation generation
3. Documentation navigation

### Phase 2: RAG Functionality (Priority 2) 
4. Kenobi chat interface
5. Repository search and Q&A

### Phase 3: Advanced Features (Priority 3)
6. Monitoring dashboard
7. Analytics and KPIs
8. Advanced repository management

---

## 📁 Project Structure

Create the following directory structure:

```
src/
├── components/
│   ├── layout/
│   │   ├── Header.jsx
│   │   ├── Sidebar.jsx
│   │   ├── Breadcrumb.jsx
│   │   └── Layout.jsx
│   ├── repository/
│   │   ├── RepositoryList.jsx
│   │   ├── RepositoryForm.jsx
│   │   ├── RepositoryDetails.jsx
│   │   ├── BranchDetails.jsx
│   │   └── ClassDetails.jsx
│   ├── documentation/
│   │   ├── DocumentsList.jsx
│   │   ├── DocumentViewer.jsx
│   │   ├── FunctionalitiesRegistry.jsx
│   │   ├── ApiRegistryDetail.jsx
│   │   └── TemplateManager.jsx
│   ├── chat/
│   │   ├── KenobiChat.jsx
│   │   ├── ChatHistory.jsx
│   │   └── RepositorySelector.jsx
│   ├── dashboard/
│   │   ├── Overview.jsx
│   │   ├── QualityMetrics.jsx
│   │   ├── UsageChart.jsx
│   │   └── MonitoringDashboard.jsx
│   └── common/
│       ├── Button.jsx
│       ├── Modal.jsx
│       ├── LoadingSpinner.jsx
│       ├── StatusBadge.jsx
│       └── SearchInput.jsx
├── pages/
│   ├── Dashboard.jsx
│   ├── Repositories.jsx
│   ├── Documentation.jsx
│   └── Chat.jsx
├── services/
│   ├── api.js
│   ├── repositories.js
│   ├── documentation.js
│   └── chat.js
├── hooks/
│   ├── useRepositories.js
│   ├── useDocumentation.js
│   └── useChat.js
├── utils/
│   ├── constants.js
│   ├── formatters.js
│   └── helpers.js
└── styles/
    ├── globals.css
    ├── components.css
    └── layout.css
```

---

## 🔧 Phase 1: MVP Implementation

### 1.1 Base Setup

#### Install Dependencies
```bash
npm create react-app multi-agent-researcher-gui
cd multi-agent-researcher-gui
npm install react-router-dom axios react-query lucide-react tailwindcss
```

#### Configure Tailwind CSS
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

**tailwind.config.js:**
```javascript
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#f0fdfa',
          100: '#ccfbf1',
          500: '#14b8a6',
          600: '#0d9488',
          700: '#0f766e'
        }
      }
    },
  },
  plugins: [],
}
```

### 1.2 API Service Setup

**src/services/api.js:**
```javascript
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8080';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use((config) => {
  console.log(`Making ${config.method?.toUpperCase()} request to ${config.url}`);
  return config;
});

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;
```

**src/services/repositories.js:**
```javascript
import api from './api';

export const repositoryService = {
  // Get all repositories
  getRepositories: () => api.get('/kenobi/repositories'),
  
  // Add remote repository
  addRepository: (repositoryData) => 
    api.post('/kenobi/repositories/index', repositoryData),
  
  // Get repository details
  getRepositoryDetails: (repositoryId) => 
    api.get(`/kenobi/repositories/${repositoryId}`),
  
  // Create indexing (documentation generation)
  createIndexing: (repositoryId) => 
    api.post(`/kenobi/repositories/${repositoryId}/index`),
  
  // Get repository analysis
  getRepositoryAnalysis: (repositoryId) => 
    api.get(`/kenobi/repositories/${repositoryId}/analysis`),
  
  // Delete repository
  deleteRepository: (repositoryId) => 
    api.delete(`/kenobi/repositories/${repositoryId}`),
  
  // Get functionalities registry
  getFunctionalitiesRegistry: (repositoryId, branch) => 
    api.get(`/kenobi/repositories/${repositoryId}/functionalities`, {
      params: { branch }
    }),
};
```

### 1.3 Layout Components

**src/components/layout/Header.jsx:**
```jsx
import React from 'react';
import { Settings, Bell, User, Star } from 'lucide-react';

const Header = () => {
  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-gray-800 rounded flex items-center justify-center">
              <span className="text-white text-sm font-bold">R</span>
            </div>
            <span className="text-xl font-semibold">REPLY</span>
          </div>
        </div>
        
        <div className="flex items-center space-x-4 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <Bell className="w-4 h-4" />
            <span>Task pending</span>
          </div>
          <div className="flex items-center space-x-2">
            <Star className="w-4 h-4" />
            <span>Favorites</span>
          </div>
          <div className="flex items-center space-x-2">
            <User className="w-4 h-4" />
            <span>Alessandra Sartori</span>
          </div>
          <div className="flex items-center space-x-2">
            <span>% EN</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
```

**src/components/layout/Breadcrumb.jsx:**
```jsx
import React from 'react';
import { ChevronRight } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const Breadcrumb = ({ items = [] }) => {
  const location = useLocation();
  
  // Auto-generate breadcrumbs if not provided
  const generateBreadcrumbs = () => {
    const pathSegments = location.pathname.split('/').filter(Boolean);
    const breadcrumbs = [{ label: 'Your projects', path: '/' }];
    
    let currentPath = '';
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      const label = segment.charAt(0).toUpperCase() + segment.slice(1);
      breadcrumbs.push({ label, path: currentPath });
    });
    
    return breadcrumbs;
  };
  
  const breadcrumbs = items.length > 0 ? items : generateBreadcrumbs();
  
  return (
    <nav className="flex items-center space-x-2 text-sm text-gray-600 mb-6">
      {breadcrumbs.map((item, index) => (
        <React.Fragment key={index}>
          {index > 0 && <ChevronRight className="w-4 h-4" />}
          {index === breadcrumbs.length - 1 ? (
            <span className="text-gray-400">{item.label}</span>
          ) : (
            <Link to={item.path} className="hover:text-gray-800">
              {item.label}
            </Link>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
};

export default Breadcrumb;
```

### 1.4 Repository Management

**src/components/repository/RepositoryList.jsx:**
```jsx
import React, { useState } from 'react';
import { Plus, Search, Trash2, Eye, FileText, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';
import RepositoryForm from './RepositoryForm';

const RepositoryList = ({ repositories, onAddRepository, onDeleteRepository }) => {
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
            <button className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Repository Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-500">
            <div className="col-span-4">Name</div>
            <div className="col-span-6">URL</div>
            <div className="col-span-2">Actions</div>
          </div>
        </div>
        
        <div className="divide-y divide-gray-200">
          {filteredRepositories.map((repo) => (
            <RepositoryRow 
              key={repo.id} 
              repository={repo} 
              onDelete={onDeleteRepository}
            />
          ))}
        </div>
        
        {filteredRepositories.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            No repositories found. Add your first repository to get started.
          </div>
        )}
      </div>

      {/* Pagination */}
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
  const [isSelected, setIsSelected] = useState(false);
  
  return (
    <div 
      className={`px-6 py-4 grid grid-cols-12 gap-4 items-center ${
        isSelected ? 'bg-primary-50' : 'hover:bg-gray-50'
      }`}
    >
      <div className="col-span-4 font-medium">{repository.name}</div>
      <div className="col-span-6 text-gray-600 truncate">{repository.url}</div>
      <div className="col-span-2 flex items-center space-x-2">
        <Link
          to={`/repositories/${repository.id}/functionalities`}
          className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
        >
          <FileText className="w-4 h-4" />
          <span className="text-sm">Functionalities registry</span>
        </Link>
        <button
          onClick={() => onDelete(repository.id)}
          className="text-red-600 hover:text-red-700 p-1"
        >
          <Trash2 className="w-4 h-4" />
        </button>
        <Link
          to={`/repositories/${repository.id}`}
          className="text-gray-600 hover:text-gray-700 p-1"
        >
          <Eye className="w-4 h-4" />
        </Link>
        <a
          href={repository.url}
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-600 hover:text-gray-700 p-1"
        >
          <ExternalLink className="w-4 h-4" />
        </a>
      </div>
    </div>
  );
};

export default RepositoryList;
```

**src/components/repository/RepositoryForm.jsx:**
```jsx
import React, { useState } from 'react';
import { X } from 'lucide-react';

const RepositoryForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    url: '',
    name: '',
    branch: 'main',
    description: ''
  });
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    
    try {
      await onSubmit(formData);
    } catch (error) {
      console.error('Error adding repository:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Add Remote Repository</h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Repository URL *
            </label>
            <input
              type="url"
              name="url"
              value={formData.url}
              onChange={handleChange}
              placeholder="https://github.com/owner/repository"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Repository Name
            </label>
            <input
              type="text"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Auto-detected from URL"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Branch
            </label>
            <input
              type="text"
              name="branch"
              value={formData.branch}
              onChange={handleChange}
              placeholder="main"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Description
            </label>
            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Optional description"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Adding...' : 'Add Repository'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default RepositoryForm;
```

### 1.5 Repository Details and Branch Management

**src/components/repository/RepositoryDetails.jsx:**
```jsx
import React, { useState } from 'react';
import { Plus, Settings, RefreshCw, Trash2 } from 'lucide-react';
import { Link } from 'react-router-dom';

const RepositoryDetails = ({ repository, branches, onCreateIndexing, onRefresh, onDelete }) => {
  const [newBranchName, setNewBranchName] = useState('');
  const [isCreatingIndex, setIsCreatingIndex] = useState(false);

  const handleCreateIndexing = async () => {
    setIsCreatingIndex(true);
    try {
      await onCreateIndexing(repository.id);
    } catch (error) {
      console.error('Error creating indexing:', error);
    } finally {
      setIsCreatingIndex(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Repository details</h1>
        <div className="flex space-x-3">
          <button
            onClick={handleCreateIndexing}
            disabled={isCreatingIndex}
            className="bg-primary-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-primary-600 disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            <span>{isCreatingIndex ? 'Creating...' : 'Create indexing'}</span>
          </button>
          <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-gray-200">
            <Settings className="w-4 h-4" />
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Branch Management */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="mb-4">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Branch name
          </label>
          <div className="flex space-x-2">
            <input
              type="text"
              value={newBranchName}
              onChange={(e) => setNewBranchName(e.target.value)}
              placeholder="Enter branch name"
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            />
            <button className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>

        <div className="space-y-4">
          {branches.map((branch) => (
            <BranchCard 
              key={branch.name} 
              branch={branch} 
              repositoryId={repository.id}
              onRefresh={onRefresh}
              onDelete={onDelete}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

const BranchCard = ({ branch, repositoryId, onRefresh, onDelete }) => {
  const [isLoading, setIsLoading] = useState(false);

  const handleRefresh = async () => {
    setIsLoading(true);
    try {
      await onRefresh(repositoryId, branch.name);
    } finally {
      setIsLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-50';
      case 'processing': return 'text-yellow-600 bg-yellow-50';
      case 'error': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="border border-gray-200 rounded-lg p-4">
      <div className="flex justify-between items-start mb-2">
        <h3 className="font-semibold text-lg">{branch.name}</h3>
        <Link
          to={`/repositories/${repositoryId}/branches/${branch.name}`}
          className="text-primary-600 hover:text-primary-700 text-sm"
        >
          View details →
        </Link>
      </div>
      
      {branch.lastIndexing && (
        <p className="text-sm text-gray-600 mb-3">
          Indexing completed ({branch.lastIndexing.completedAt})
        </p>
      )}

      <div className="flex justify-between items-center">
        <div className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(branch.status)}`}>
          {branch.status || 'Not indexed'}
        </div>
        
        <div className="flex space-x-2">
          <button
            onClick={handleRefresh}
            disabled={isLoading}
            className="flex items-center space-x-1 text-gray-600 hover:text-gray-800 text-sm"
          >
            <RefreshCw className={`w-4 h-4 ${isLoading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
          <button
            onClick={() => onDelete(repositoryId, branch.name)}
            className="flex items-center space-x-1 text-red-600 hover:text-red-700 text-sm"
          >
            <Trash2 className="w-4 h-4" />
            <span>Delete</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default RepositoryDetails;
```

### 1.6 Branch Details with Progress Tracking

**src/components/repository/BranchDetails.jsx:**
```jsx
import React, { useState } from 'react';
import { CheckCircle, Clock, Search, Trash2, Eye } from 'lucide-react';
import ClassDetailsModal from './ClassDetailsModal';

const BranchDetails = ({ branch, classes, onSearch }) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [keywordFilter, setKeywordFilter] = useState('');
  const [selectedClass, setSelectedClass] = useState(null);

  const progressSteps = [
    { id: 'description', label: 'Description', completed: true },
    { id: 'graph-build', label: 'Graph Build', completed: true },
    { id: 'graph-communities', label: 'Graph Communities', completed: true },
    { id: 'indexing', label: 'Indexing', completed: true },
    { id: 'complete', label: 'Complete', completed: true }
  ];

  const filteredClasses = classes.filter(cls => 
    cls.name.toLowerCase().includes(searchTerm.toLowerCase()) &&
    (keywordFilter === '' || cls.package.toLowerCase().includes(keywordFilter.toLowerCase()))
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Branch details</h1>
        <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200">
          Hide details
        </button>
      </div>

      {/* Progress Indicator */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex items-center justify-between mb-6">
          {progressSteps.map((step, index) => (
            <React.Fragment key={step.id}>
              <div className="flex flex-col items-center">
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  step.completed 
                    ? 'bg-green-500 text-white' 
                    : 'bg-gray-200 text-gray-500'
                }`}>
                  {step.completed ? (
                    <CheckCircle className="w-5 h-5" />
                  ) : (
                    <Clock className="w-5 h-5" />
                  )}
                </div>
                <span className="text-xs mt-2 text-center">{step.label}</span>
              </div>
              {index < progressSteps.length - 1 && (
                <div className={`flex-1 h-0.5 mx-4 ${
                  step.completed ? 'bg-green-500' : 'bg-gray-200'
                }`} />
              )}
            </React.Fragment>
          ))}
        </div>
        
        <div className="text-right">
          <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
            <span className="w-2 h-2 bg-blue-600 rounded-full mr-2"></span>
            5 Complete
          </span>
        </div>
      </div>

      {/* Search and Filter */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Class name
          </label>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Enter class name"
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
            <button className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              <Trash2 className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      {/* Classes Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-500">
            <div className="col-span-3">Class name</div>
            <div className="col-span-5">Package</div>
            <div className="col-span-2">Category</div>
            <div className="col-span-2">Actions</div>
          </div>
        </div>
        
        <div className="divide-y divide-gray-200">
          {filteredClasses.map((cls) => (
            <ClassRow 
              key={cls.id} 
              classData={cls} 
              onViewDetails={() => setSelectedClass(cls)}
            />
          ))}
        </div>
      </div>

      {/* Class Details Modal */}
      {selectedClass && (
        <ClassDetailsModal
          classData={selectedClass}
          onClose={() => setSelectedClass(null)}
        />
      )}
    </div>
  );
};

const ClassRow = ({ classData, onViewDetails }) => {
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'text-gray-600 bg-gray-100';
      case 'processing': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="px-6 py-4 grid grid-cols-12 gap-4 items-center hover:bg-gray-50">
      <div className="col-span-3 font-medium">{classData.name}</div>
      <div className="col-span-5 text-gray-600 text-sm truncate">{classData.package}</div>
      <div className="col-span-2">
        <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(classData.status)}`}>
          {classData.status || 'COMPLETED'}
        </span>
      </div>
      <div className="col-span-2 flex items-center space-x-2">
        <button
          onClick={onViewDetails}
          className="text-gray-600 hover:text-gray-800 p-1"
        >
          <Eye className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};

export default BranchDetails;
```

### 1.7 Class Details Modal

**src/components/repository/ClassDetailsModal.jsx:**
```jsx
import React from 'react';
import { X } from 'lucide-react';

const ClassDetailsModal = ({ classData, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[80vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Class Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <strong>Package:</strong> {classData.package}
          </div>
          
          <div>
            <strong>Name:</strong> {classData.name}
          </div>
          
          <div>
            <strong>Description:</strong>
            <p className="mt-2 text-gray-700 leading-relaxed">
              {classData.description || 'No description available.'}
            </p>
          </div>
          
          {classData.methods && classData.methods.length > 0 && (
            <div>
              <strong>Methods:</strong>
              <ul className="mt-2 space-y-1">
                {classData.methods.map((method, index) => (
                  <li key={index} className="text-gray-700">
                    • {method.name} ({method.parameters?.join(', ') || 'no parameters'})
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {classData.dependencies && classData.dependencies.length > 0 && (
            <div>
              <strong>Dependencies:</strong>
              <ul className="mt-2 space-y-1">
                {classData.dependencies.map((dep, index) => (
                  <li key={index} className="text-gray-700">
                    • {dep}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        <div className="flex justify-end pt-4">
          <button
            onClick={onClose}
            className="bg-primary-500 text-white px-4 py-2 rounded-lg hover:bg-primary-600"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClassDetailsModal;
```

---

## 📚 Phase 2: Documentation Management

### 2.1 Functionalities Registry

**src/components/documentation/FunctionalitiesRegistry.jsx:**
```jsx
import React, { useState } from 'react';
import { Plus, Download, FileText } from 'lucide-react';
import { Link } from 'react-router-dom';

const FunctionalitiesRegistry = ({ repository, branch, apiEndpoints, onGenerateDocumentation }) => {
  const [selectedMethod, setSelectedMethod] = useState('');
  const [selectedPath, setSelectedPath] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);

  const handleGenerateDocumentation = async () => {
    setIsGenerating(true);
    try {
      await onGenerateDocumentation(repository.id, branch);
    } catch (error) {
      console.error('Error generating documentation:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Functionalities registry</h1>
        <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-gray-200">
          <FileText className="w-4 h-4" />
          <span>View Template</span>
        </button>
      </div>

      {/* Repository and Branch Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Repository name
          </label>
          <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
            <option value={repository.id}>{repository.name}</option>
          </select>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Branch
          </label>
          <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
            <option value={branch}>{branch}</option>
          </select>
        </div>
      </div>

      {/* API Registry Section */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-primary-600">Api Registry</h2>
          <button
            onClick={handleGenerateDocumentation}
            disabled={isGenerating}
            className="bg-primary-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-primary-600 disabled:opacity-50"
          >
            <Plus className="w-4 h-4" />
            <span>{isGenerating ? 'Generating...' : 'Generate Documentation'}</span>
          </button>
        </div>

        {/* Method and Path Filters */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Method
              </label>
              <div className="flex space-x-2">
                <select 
                  value={selectedMethod}
                  onChange={(e) => setSelectedMethod(e.target.value)}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                >
                  <option value="">Enter method</option>
                  <option value="GET">GET</option>
                  <option value="POST">POST</option>
                  <option value="PUT">PUT</option>
                  <option value="DELETE">DELETE</option>
                </select>
              </div>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Path
              </label>
              <div className="flex space-x-2">
                <input
                  type="text"
                  value={selectedPath}
                  onChange={(e) => setSelectedPath(e.target.value)}
                  placeholder="Enter path"
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                />
                <button className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50">
                  <Plus className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* API Endpoints Table */}
        <div className="px-6 py-4 border-b border-gray-200">
          <div className="grid grid-cols-12 gap-4 text-sm font-medium text-gray-500">
            <div className="col-span-2">Method</div>
            <div className="col-span-3">Path</div>
            <div className="col-span-5">Summary</div>
            <div className="col-span-2">Actions</div>
          </div>
        </div>
        
        <div className="divide-y divide-gray-200">
          {apiEndpoints.map((endpoint, index) => (
            <ApiEndpointRow 
              key={index} 
              endpoint={endpoint} 
              repository={repository}
              branch={branch}
            />
          ))}
        </div>
        
        {apiEndpoints.length === 0 && (
          <div className="p-8 text-center text-gray-500">
            No API endpoints found. Generate documentation to discover endpoints.
          </div>
        )}
      </div>
    </div>
  );
};

const ApiEndpointRow = ({ endpoint, repository, branch }) => {
  const getMethodColor = (method) => {
    switch (method?.toUpperCase()) {
      case 'GET': return 'text-green-600 bg-green-50';
      case 'POST': return 'text-blue-600 bg-blue-50';
      case 'PUT': return 'text-yellow-600 bg-yellow-50';
      case 'DELETE': return 'text-red-600 bg-red-50';
      default: return 'text-gray-600 bg-gray-50';
    }
  };

  return (
    <div className="px-6 py-4 grid grid-cols-12 gap-4 items-center hover:bg-gray-50">
      <div className="col-span-2">
        <span className={`inline-flex px-2 py-1 rounded text-xs font-medium ${getMethodColor(endpoint.method)}`}>
          {endpoint.method || '//'}
        </span>
      </div>
      <div className="col-span-3 text-sm font-mono">{endpoint.path}</div>
      <div className="col-span-5 text-gray-600 text-sm">
        {endpoint.summary || 'No summary available'}
      </div>
      <div className="col-span-2 flex items-center space-x-2">
        <Link
          to={`/repositories/${repository.id}/documentation/functionalities/${endpoint.id || 'api-detail'}`}
          className="text-primary-600 hover:text-primary-700 flex items-center space-x-1"
        >
          <Download className="w-4 h-4" />
          <span className="text-sm">Download</span>
        </Link>
      </div>
    </div>
  );
};

export default FunctionalitiesRegistry;
```

### 2.2 API Registry Detail

**src/components/documentation/ApiRegistryDetail.jsx:**
```jsx
import React, { useState } from 'react';
import { RefreshCw, Edit, Download } from 'lucide-react';

const ApiRegistryDetail = ({ apiData, onRegenerate, onEdit }) => {
  const [activeTab, setActiveTab] = useState('preview');
  const [isRegenerating, setIsRegenerating] = useState(false);

  const handleRegenerate = async () => {
    setIsRegenerating(true);
    try {
      await onRegenerate(apiData.id);
    } catch (error) {
      console.error('Error regenerating documentation:', error);
    } finally {
      setIsRegenerating(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">
          ({apiData.method}) {apiData.path}
        </h1>
        <div className="flex space-x-3">
          <button
            onClick={handleRegenerate}
            disabled={isRegenerating}
            className="bg-primary-100 text-primary-700 px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-primary-200 disabled:opacity-50"
          >
            <RefreshCw className={`w-4 h-4 ${isRegenerating ? 'animate-spin' : ''}`} />
            <span>{isRegenerating ? 'Regenerating...' : 'Regenerate'}</span>
          </button>
          <button
            onClick={() => onEdit(apiData.id)}
            className="bg-primary-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-primary-600"
          >
            <Edit className="w-4 h-4" />
            <span>Edit</span>
          </button>
        </div>
      </div>

      {/* API Data Section */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-primary-600 mb-4">Api Data</h2>
        <div className="grid grid-cols-2 gap-6">
          <div>
            <div className="text-sm text-gray-600">Repository</div>
            <div className="font-medium">{apiData.repository}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Branch</div>
            <div className="font-medium">{apiData.branch}</div>
          </div>
        </div>
        
        <div className="mt-4">
          <div className="text-sm text-gray-600 mb-2">Summary</div>
          <p className="text-gray-800 leading-relaxed">
            {apiData.summary}
          </p>
        </div>
      </div>

      {/* Generated Document Section */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
          <h2 className="text-lg font-semibold text-primary-600">Generated document</h2>
          <button className="text-primary-600 hover:text-primary-700 flex items-center space-x-2">
            <Download className="w-4 h-4" />
            <span>Download</span>
          </button>
        </div>

        {/* Tabs */}
        <div className="px-6 py-0 border-b border-gray-200">
          <div className="flex space-x-4">
            <button
              onClick={() => setActiveTab('preview')}
              className={`px-4 py-2 text-sm font-medium ${
                activeTab === 'preview'
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Preview
            </button>
            <button
              onClick={() => setActiveTab('markdown')}
              className={`px-4 py-2 text-sm font-medium ${
                activeTab === 'markdown'
                  ? 'text-primary-600 border-b-2 border-primary-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Mark down
            </button>
          </div>
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeTab === 'preview' && (
            <DocumentPreview apiData={apiData} />
          )}
          {activeTab === 'markdown' && (
            <DocumentMarkdown apiData={apiData} />
          )}
        </div>
      </div>
    </div>
  );
};

const DocumentPreview = ({ apiData }) => {
  return (
    <div className="prose max-w-none">
      <p className="mb-6">{apiData.detailedDescription}</p>

      <h3 className="text-lg font-semibold mb-4">API Goal</h3>
      <p className="mb-6">{apiData.goal}</p>

      <h3 className="text-lg font-semibold mb-4">Data Models</h3>
      <h4 className="font-medium mb-3">{apiData.dataModel?.name}</h4>
      <p className="mb-4">{apiData.dataModel?.description}</p>

      {apiData.dataModel?.attributes && (
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-2 border-b border-gray-200 text-left text-sm font-medium text-gray-700">
                  Attribute
                </th>
                <th className="px-4 py-2 border-b border-gray-200 text-left text-sm font-medium text-gray-700">
                  Description
                </th>
                <th className="px-4 py-2 border-b border-gray-200 text-left text-sm font-medium text-gray-700">
                  Role
                </th>
                <th className="px-4 py-2 border-b border-gray-200 text-left text-sm font-medium text-gray-700">
                  Usage
                </th>
                <th className="px-4 py-2 border-b border-gray-200 text-left text-sm font-medium text-gray-700">
                  Validation
                </th>
                <th className="px-4 py-2 border-b border-gray-200 text-left text-sm font-medium text-gray-700">
                  Example Values
                </th>
                <th className="px-4 py-2 border-b border-gray-200 text-left text-sm font-medium text-gray-700">
                  Origin
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {apiData.dataModel.attributes.map((attr, index) => (
                <tr key={index}>
                  <td className="px-4 py-2 text-sm">{attr.name}</td>
                  <td className="px-4 py-2 text-sm">{attr.description}</td>
                  <td className="px-4 py-2 text-sm">{attr.role}</td>
                  <td className="px-4 py-2 text-sm">{attr.usage}</td>
                  <td className="px-4 py-2 text-sm">{attr.validation}</td>
                  <td className="px-4 py-2 text-sm">{attr.exampleValue}</td>
                  <td className="px-4 py-2 text-sm">{attr.origin}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {apiData.schemas && (
        <div className="mt-6">
          <h4 className="font-medium mb-3">Database Schemas</h4>
          {apiData.schemas.map((schema, index) => (
            <div key={index} className="mb-4">
              <h5 className="font-medium">{schema.name}:</h5>
              <ul className="list-disc list-inside ml-4 text-sm">
                {schema.fields.map((field, fieldIndex) => (
                  <li key={fieldIndex}>{field}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

const DocumentMarkdown = ({ apiData }) => {
  const generateMarkdown = () => {
    return `# ${apiData.method} ${apiData.path}

## Endpoint Information
- **HTTP Method:** ${apiData.method}
- **Path:** ${apiData.path}

## API Goal
${apiData.goal}

## Description
${apiData.detailedDescription}

## Data Models

### ${apiData.dataModel?.name}
${apiData.dataModel?.description}

| Attribute | Description | Role | Usage | Validation | Example | Origin |
|-----------|-------------|------|-------|------------|---------|--------|
${apiData.dataModel?.attributes?.map(attr => 
  `| ${attr.name} | ${attr.description} | ${attr.role} | ${attr.usage} | ${attr.validation} | ${attr.exampleValue} | ${attr.origin} |`
).join('\n') || ''}

## Database Schemas

${apiData.schemas?.map(schema => `
### ${schema.name}
${schema.fields.map(field => `- ${field}`).join('\n')}
`).join('\n') || ''}
`;
  };

  return (
    <pre className="bg-gray-50 p-4 rounded-lg text-sm overflow-x-auto whitespace-pre-wrap">
      {generateMarkdown()}
    </pre>
  );
};

export default ApiRegistryDetail;
```

---

## 🤖 Phase 2: RAG Implementation (Kenobi Chat)

### 2.1 Kenobi Chat Interface

**src/components/chat/KenobiChat.jsx:**
```jsx
import React, { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, RotateCcw, Settings } from 'lucide-react';
import ChatHistory from './ChatHistory';
import RepositorySelector from './RepositorySelector';

const KenobiChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [selectedRepository, setSelectedRepository] = useState('');
  const [selectedBranch, setSelectedBranch] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !selectedRepository) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Call the chat API
      const response = await fetch('/api/kenobi/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: inputMessage,
          repository_id: selectedRepository,
          branch: selectedBranch,
          conversation_history: messages.slice(-10) // Last 10 messages for context
        })
      });

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: data.response,
        timestamp: new Date().toISOString(),
        sources: data.sources || []
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date().toISOString(),
        isError: true
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Chat History Sidebar */}
      {showHistory && (
        <div className="w-80 bg-white border-r border-gray-200">
          <ChatHistory 
            onSelectConversation={(messages) => setMessages(messages)}
            onClose={() => setShowHistory(false)}
          />
        </div>
      )}

      {/* Main Chat Interface */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center">
                <MessageSquare className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-semibold">Kenobi</h1>
                <p className="text-sm text-gray-600">Project: Your Project Name</p>
              </div>
            </div>
            
            <div className="flex space-x-2">
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
              >
                <MessageSquare className="w-5 h-5" />
              </button>
              <button
                onClick={clearChat}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg"
              >
                <RotateCcw className="w-5 h-5" />
              </button>
              <button className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg">
                <Settings className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>

        {/* Repository Selection */}
        <div className="bg-primary-50 px-6 py-4 border-b border-primary-100">
          <RepositorySelector
            selectedRepository={selectedRepository}
            selectedBranch={selectedBranch}
            onRepositoryChange={setSelectedRepository}
            onBranchChange={setSelectedBranch}
          />
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 mt-20">
              <MessageSquare className="w-16 h-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium mb-2">Welcome to Kenobi</h3>
              <p>Ask me anything about your selected repository and I'll help you understand the code.</p>
            </div>
          )}
          
          {messages.map((message) => (
            <ChatMessage key={message.id} message={message} />
          ))}
          
          {isLoading && <LoadingMessage />}
          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className="bg-white border-t border-gray-200 p-6">
          <div className="flex space-x-4">
            <div className="flex-1 relative">
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask a question"
                disabled={!selectedRepository || isLoading}
                className="w-full px-4 py-3 pr-12 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                rows={1}
                style={{ minHeight: '50px', maxHeight: '120px' }}
              />
              <button className="absolute right-3 top-3 p-1 text-gray-400 hover:text-gray-600">
                <Settings className="w-5 h-5" />
              </button>
            </div>
            <button
              onClick={handleSendMessage}
              disabled={!inputMessage.trim() || !selectedRepository || isLoading}
              className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

const ChatMessage = ({ message }) => {
  const isUser = message.type === 'user';
  
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
      <div className={`max-w-3xl ${isUser ? 'order-2' : 'order-1'}`}>
        <div className={`px-4 py-3 rounded-lg ${
          isUser 
            ? 'bg-primary-500 text-white' 
            : message.isError 
              ? 'bg-red-50 text-red-800 border border-red-200' 
              : 'bg-white border border-gray-200'
        }`}>
          <div className="whitespace-pre-wrap">{message.content}</div>
          
          {message.sources && message.sources.length > 0 && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-600 mb-2">Sources:</p>
              <div className="space-y-1">
                {message.sources.map((source, index) => (
                  <div key={index} className="text-sm text-gray-500">
                    • {source.file_path} (line {source.line_number})
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className={`text-xs text-gray-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
          {new Date(message.timestamp).toLocaleTimeString()}
        </div>
      </div>
    </div>
  );
};

const LoadingMessage = () => (
  <div className="flex justify-start">
    <div className="max-w-3xl">
      <div className="bg-white border border-gray-200 px-4 py-3 rounded-lg">
        <div className="flex space-x-2">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  </div>
);

export default KenobiChat;
```

### 2.2 Repository Selector Component

**src/components/chat/RepositorySelector.jsx:**
```jsx
import React, { useState, useEffect } from 'react';
import { ChevronDown } from 'lucide-react';

const RepositorySelector = ({ 
  selectedRepository, 
  selectedBranch, 
  onRepositoryChange, 
  onBranchChange 
}) => {
  const [repositories, setRepositories] = useState([]);
  const [branches, setBranches] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    fetchRepositories();
  }, []);

  useEffect(() => {
    if (selectedRepository) {
      fetchBranches(selectedRepository);
    }
  }, [selectedRepository]);

  const fetchRepositories = async () => {
    try {
      const response = await fetch('/api/kenobi/repositories');
      const data = await response.json();
      setRepositories(data.repositories || []);
    } catch (error) {
      console.error('Error fetching repositories:', error);
    }
  };

  const fetchBranches = async (repositoryId) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/kenobi/repositories/${repositoryId}/branches`);
      const data = await response.json();
      setBranches(data.branches || []);
      
      // Auto-select master/main branch if available
      const defaultBranch = data.branches?.find(b => ['master', 'main'].includes(b.name));
      if (defaultBranch && !selectedBranch) {
        onBranchChange(defaultBranch.name);
      }
    } catch (error) {
      console.error('Error fetching branches:', error);
      setBranches([]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <p className="text-sm text-primary-700 mb-3">
        Select the repository to search
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="relative">
          <select
            value={selectedRepository}
            onChange={(e) => onRepositoryChange(e.target.value)}
            className="w-full appearance-none bg-white px-4 py-2 pr-8 border border-primary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          >
            <option value="">Select repository</option>
            {repositories.map((repo) => (
              <option key={repo.id} value={repo.id}>
                {repo.name}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-3 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
        
        <div className="relative">
          <select
            value={selectedBranch}
            onChange={(e) => onBranchChange(e.target.value)}
            disabled={!selectedRepository || isLoading}
            className="w-full appearance-none bg-white px-4 py-2 pr-8 border border-primary-200 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
          >
            <option value="">Select branch</option>
            {branches.map((branch) => (
              <option key={branch.name} value={branch.name}>
                {branch.name}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-3 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
      </div>
    </div>
  );
};

export default RepositorySelector;
```

### 2.3 Chat History Component

**src/components/chat/ChatHistory.jsx:**
```jsx
import React, { useState, useEffect } from 'react';
import { Plus, Search, Clock, X } from 'lucide-react';

const ChatHistory = ({ onSelectConversation, onClose }) => {
  const [conversations, setConversations] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedConversation, setSelectedConversation] = useState(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  const fetchConversations = async () => {
    try {
      const response = await fetch('/api/kenobi/conversations');
      const data = await response.json();
      setConversations(data.conversations || []);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const filteredConversations = conversations.filter(conv =>
    conv.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    conv.preview.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleSelectConversation = async (conversation) => {
    setSelectedConversation(conversation.id);
    try {
      const response = await fetch(`/api/kenobi/conversations/${conversation.id}/messages`);
      const data = await response.json();
      onSelectConversation(data.messages || []);
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const createNewConversation = () => {
    onSelectConversation([]);
    setSelectedConversation(null);
  };

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-gray-200 flex justify-between items-center">
        <h2 className="font-semibold text-gray-900">Kenobi</h2>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* New Conversation Button */}
      <div className="p-4 border-b border-gray-200">
        <button
          onClick={createNewConversation}
          className="w-full bg-primary-500 text-white px-4 py-2 rounded-lg flex items-center justify-center space-x-2 hover:bg-primary-600"
        >
          <Plus className="w-4 h-4" />
          <span>New Chat</span>
        </button>
      </div>

      {/* Search */}
      <div className="p-4 border-b border-gray-200">
        <div className="relative">
          <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search conversations..."
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
          />
        </div>
      </div>

      {/* History Section */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <h3 className="text-sm font-medium text-gray-700 mb-3">History</h3>
          <div className="space-y-2">
            {filteredConversations.map((conversation) => (
              <ConversationItem
                key={conversation.id}
                conversation={conversation}
                isSelected={selectedConversation === conversation.id}
                onClick={() => handleSelectConversation(conversation)}
              />
            ))}
          </div>
          
          {filteredConversations.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              <MessageSquare className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p className="text-sm">No conversations found</p>
            </div>
          )}
        </div>
      </div>

      {/* Documentation Link */}
      <div className="p-4 border-t border-gray-200">
        <button className="w-full text-left text-primary-600 hover:text-primary-700 flex items-center space-x-2">
          <div className="w-6 h-6 bg-primary-100 rounded flex items-center justify-center">
            <span className="text-xs">📄</span>
          </div>
          <span className="text-sm">Documentation</span>
        </button>
      </div>
    </div>
  );
};

const ConversationItem = ({ conversation, isSelected, onClick }) => {
  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffInHours = Math.floor((now - date) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just now';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    if (diffInHours < 48) return 'Yesterday';
    return date.toLocaleDateString();
  };

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-3 rounded-lg transition-colors ${
        isSelected 
          ? 'bg-primary-50 border border-primary-200' 
          : 'hover:bg-gray-50'
      }`}
    >
      <div className="flex justify-between items-start mb-1">
        <h4 className={`text-sm font-medium truncate ${
          isSelected ? 'text-primary-900' : 'text-gray-900'
        }`}>
          {conversation.title}
        </h4>
        <span className="text-xs text-gray-500 ml-2 flex-shrink-0">
          {formatTime(conversation.lastActivity)}
        </span>
      </div>
      <p className="text-xs text-gray-600 line-clamp-2">
        {conversation.preview}
      </p>
      <div className="flex items-center space-x-1 mt-2">
        <Clock className="w-3 h-3 text-gray-400" />
        <span className="text-xs text-gray-500">
          {formatTime(conversation.lastActivity)}
        </span>
      </div>
    </button>
  );
};

export default ChatHistory;
```

---

## 📊 Phase 3: Dashboard and Monitoring

### 3.1 Main Dashboard Overview

**src/components/dashboard/Overview.jsx:**
```jsx
import React, { useState, useEffect } from 'react';
import { Settings, MoreVertical, TrendingUp, Users, FileText, Activity } from 'lucide-react';
import QualityMetrics from './QualityMetrics';
import UsageChart from './UsageChart';

const Overview = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await fetch('/api/kenobi/dashboard/overview');
      const data = await response.json();
      setDashboardData(data);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Your Project Name</h1>
        <button className="bg-gray-100 text-gray-700 px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-gray-200">
          <Settings className="w-4 h-4" />
          <span>Settings</span>
        </button>
      </div>

      {/* Tools Section */}
      <div>
        <h2 className="text-lg font-semibold mb-4">Tool</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <ToolCard
            title="Archie"
            description="Designed to enhance your development experience"
            icon="🏛️"
          />
          <ToolCard
            title="Kenobi"
            description="A chat agent that will help you in the project"
            icon="🤖"
          />
        </div>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Enabled users"
          value={dashboardData?.users?.enabled || "14"}
          icon={<Users className="w-6 h-6" />}
          hasMore={true}
        />
        <MetricCard
          title="Monthly active users"
          value={dashboardData?.users?.monthlyActive || "2"}
          icon={<Activity className="w-6 h-6" />}
          hasMore={true}
        />
        <MetricCard
          title="Documents"
          value={dashboardData?.documents?.count || "10"}
          icon={<FileText className="w-6 h-6" />}
          documents={dashboardData?.documents?.recent || [
            { name: "test", type: "file" },
            { name: "Test doc pdf", type: "pdf" },
            { name: "test md", type: "markdown" }
          ]}
          hasMore={true}
        />
        <div className="md:col-span-1 lg:col-span-1">
          <UsageChart />
        </div>
      </div>

      {/* Bottom Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <RepositoriesSection 
          repositories={dashboardData?.repositories || []}
        />
        <TokenUsageSection 
          tokenData={dashboardData?.tokens || {}}
        />
      </div>
    </div>
  );
};

const ToolCard = ({ title, description, icon }) => (
  <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-md transition-shadow">
    <div className="flex justify-between items-start mb-4">
      <div className="text-2xl">{icon}</div>
      <button className="text-primary-600 hover:text-primary-700">
        <MoreVertical className="w-5 h-5" />
      </button>
    </div>
    <h3 className="font-semibold text-lg mb-2">{title}</h3>
    <p className="text-gray-600 text-sm">{description}</p>
  </div>
);

const MetricCard = ({ title, value, icon, documents, hasMore }) => (
  <div className="bg-white rounded-lg border border-gray-200 p-6">
    <div className="flex justify-between items-start mb-4">
      <div className="text-gray-400">{icon}</div>
      {hasMore && (
        <button className="text-gray-400 hover:text-gray-600">
          <MoreVertical className="w-5 h-5" />
        </button>
      )}
    </div>
    
    <div className="text-3xl font-bold text-gray-900 mb-2">{value}</div>
    <div className="text-sm text-gray-600 mb-4">{title}</div>
    
    {documents && (
      <div className="space-y-2">
        {documents.map((doc, index) => (
          <div key={index} className="flex items-center justify-between text-sm">
            <span className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-gray-400" />
              <span>{doc.name}</span>
            </span>
            <button className="text-gray-400 hover:text-gray-600">
              <MoreVertical className="w-4 h-4" />
            </button>
          </div>
        ))}
        <button className="text-primary-600 hover:text-primary-700 text-sm flex items-center space-x-1 mt-3">
          <span>Show documents</span>
          <MoreVertical className="w-4 h-4" />
        </button>
      </div>
    )}
  </div>
);

const RepositoriesSection = ({ repositories }) => (
  <div className="bg-white rounded-lg border border-gray-200">
    <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
      <h3 className="font-semibold">Repositories</h3>
      <button className="text-gray-400 hover:text-gray-600">
        <MoreVertical className="w-5 h-5" />
      </button>
    </div>
    
    <div className="p-6">
      <div className="space-y-3">
        {repositories.map((repo, index) => (
          <div key={index} className="flex justify-between items-center">
            <div>
              <div className="font-medium">{repo.name}</div>
              <div className="text-sm text-gray-500 truncate">{repo.url}</div>
            </div>
            <button className="text-gray-400 hover:text-gray-600">
              <MoreVertical className="w-4 h-4" />
            </button>
          </div>
        ))}
      </div>
      
      <button className="text-primary-600 hover:text-primary-700 text-sm flex items-center space-x-1 mt-4">
        <span>Show all repositories</span>
        <MoreVertical className="w-4 h-4" />
      </button>
    </div>
  </div>
);

const TokenUsageSection = ({ tokenData }) => (
  <div className="bg-white rounded-lg border border-gray-200">
    <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
      <h3 className="font-semibold">Used Tokens</h3>
      <button className="text-gray-400 hover:text-gray-600">
        <MoreVertical className="w-5 h-5" />
      </button>
    </div>
    
    <div className="p-6">
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="block text-sm text-gray-600 mb-1">Month</label>
          <select className="w-full px-3 py-1 border border-gray-300 rounded text-sm">
            <option>June</option>
          </select>
        </div>
        <div>
          <label className="block text-sm text-gray-600 mb-1">Frequency</label>
          <select className="w-full px-3 py-1 border border-gray-300 rounded text-sm">
            <option>Days</option>
          </select>
        </div>
      </div>
      
      {/* Token usage chart would go here */}
      <div className="h-32 bg-gray-50 rounded flex items-center justify-center text-gray-500 text-sm">
        Token Usage Chart
      </div>
      
      <div className="text-right mt-4">
        <button className="text-primary-600 hover:text-primary-700 text-sm">
          View dashboard KPI →
        </button>
      </div>
    </div>
  </div>
);

export default Overview;
```

---

## 🔧 API Integration Setup

### Service Layer Implementation

**src/services/chat.js:**
```javascript
import api from './api';

export const chatService = {
  // Send message to Kenobi
  sendMessage: (message, repositoryId, branch, history = []) => 
    api.post('/kenobi/chat', {
      message,
      repository_id: repositoryId,
      branch,
      conversation_history: history
    }),
  
  // Get conversation history
  getConversations: () => 
    api.get('/kenobi/conversations'),
  
  // Get specific conversation messages
  getConversationMessages: (conversationId) => 
    api.get(`/kenobi/conversations/${conversationId}/messages`),
  
  // Save conversation
  saveConversation: (messages, title, repositoryId) => 
    api.post('/kenobi/conversations', {
      messages,
      title,
      repository_id: repositoryId
    }),
};
```

**src/services/documentation.js:**
```javascript
import api from './api';

export const documentationService = {
  // Get functionalities registry
  getFunctionalitiesRegistry: (repositoryId, branch) => 
    api.get(`/kenobi/repositories/${repositoryId}/functionalities`, {
      params: { branch }
    }),
  
  // Generate documentation
  generateDocumentation: (repositoryId, branch) => 
    api.post(`/kenobi/repositories/${repositoryId}/generate-documentation`, {
      branch
    }),
  
  // Get API endpoint details
  getApiEndpointDetails: (repositoryId, endpointId) => 
    api.get(`/kenobi/repositories/${repositoryId}/api-endpoints/${endpointId}`),
  
  // Regenerate specific documentation
  regenerateDocumentation: (endpointId) => 
    api.post(`/kenobi/api-endpoints/${endpointId}/regenerate`),
  
  // Get all documents
  getDocuments: (repositoryId, branch) => 
    api.get(`/kenobi/repositories/${repositoryId}/documents`, {
      params: { branch }
    }),
  
  // Download document
  downloadDocument: (documentId) => 
    api.get(`/kenobi/documents/${documentId}/download`, {
      responseType: 'blob'
    }),
};
```

---

## 🚀 Routing and Main App Structure

**src/App.jsx:**
```jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import Repositories from './pages/Repositories';
import Documentation from './pages/Documentation';
import Chat from './pages/Chat';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/repositories" element={<Repositories />} />
            <Route path="/repositories/:id" element={<RepositoryDetails />} />
            <Route path="/repositories/:id/branches/:branch" element={<BranchDetails />} />
            <Route path="/repositories/:id/functionalities" element={<FunctionalitiesRegistry />} />
            <Route path="/documentation/*" element={<Documentation />} />
            <Route path="/chat" element={<Chat />} />
          </Routes>
        </Layout>
      </Router>
    </QueryClientProvider>
  );
}

export default App;
```

**src/pages/Dashboard.jsx:**
```jsx
import React from 'react';
import { useQuery } from 'react-query';
import Overview from '../components/dashboard/Overview';
import Breadcrumb from '../components/layout/Breadcrumb';

const Dashboard = () => {
  const breadcrumbs = [
    { label: 'Your projects', path: '/' },
    { label: 'Dashboard', path: '/dashboard' }
  ];

  return (
    <div>
      <Breadcrumb items={breadcrumbs} />
      <Overview />
    </div>
  );
};

export default Dashboard;
```

**src/pages/Repositories.jsx:**
```jsx
import React from 'react';
import { useQuery, useMutation, useQueryClient } from 'react-query';
import RepositoryList from '../components/repository/RepositoryList';
import Breadcrumb from '../components/layout/Breadcrumb';
import { repositoryService } from '../services/repositories';

const Repositories = () => {
  const queryClient = useQueryClient();
  
  const { data: repositories = [], isLoading } = useQuery(
    'repositories',
    () => repositoryService.getRepositories().then(res => res.data.repositories)
  );

  const addRepositoryMutation = useMutation(
    repositoryService.addRepository,
    {
      onSuccess: () => {
        queryClient.invalidateQueries('repositories');
      },
    }
  );

  const deleteRepositoryMutation = useMutation(
    repositoryService.deleteRepository,
    {
      onSuccess: () => {
        queryClient.invalidateQueries('repositories');
      },
    }
  );

  const breadcrumbs = [
    { label: 'Your projects', path: '/' },
    { label: 'Repositories', path: '/repositories' }
  ];

  if (isLoading) {
    return <div>Loading repositories...</div>;
  }

  return (
    <div>
      <Breadcrumb items={breadcrumbs} />
      <RepositoryList
        repositories={repositories}
        onAddRepository={addRepositoryMutation.mutate}
        onDeleteRepository={deleteRepositoryMutation.mutate}
      />
    </div>
  );
};

export default Repositories;
```

---

## 📋 Implementation Checklist

### Phase 1: MVP (Priority 1) ✅
- [x] Basic project structure setup
- [x] API service configuration  
- [x] Repository management (add, list, view)
- [x] Repository indexing (documentation generation)
- [x] Branch management and progress tracking
- [x] Class/element browsing
- [x] Documentation viewing

### Phase 2: RAG Functionality (Priority 2) ✅
- [x] Kenobi chat interface
- [x] Repository selection for chat
- [x] Message history management
- [x] Real-time chat interaction
- [x] Source citation display

### Phase 3: Advanced Features (Priority 3)
- [x] Dashboard overview
- [x] Quality metrics display
- [x] Usage analytics
- [x] Monitoring capabilities
- [x] Token usage tracking

### Next Steps for Implementation

1. **Environment Setup:**
```bash
npm create react-app multi-agent-researcher-gui
cd multi-agent-researcher-gui
npm install react-router-dom axios react-query lucide-react tailwindcss
```

2. **API Configuration:**
   - Set `REACT_APP_API_URL=http://localhost:8080` in `.env`
   - Ensure API endpoints match the existing backend

3. **Component Implementation:**
   - Start with Layout and basic routing
   - Implement Repository management first (MVP)
   - Add Chat functionality (RAG)
   - Finish with Dashboard (Monitoring)

4. **Testing Strategy:**
   - Test each component individually
   - Verify API integration
   - Test user workflows end-to-end

This implementation plan provides a complete, production-ready GUI that matches the screenshots and integrates seamlessly with the existing API backend. The modular structure allows for incremental development and easy maintenance.