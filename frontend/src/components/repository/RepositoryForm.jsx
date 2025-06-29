import React, { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Tabs,
  Tab,
  Box,
  TextField,
  Typography,
  IconButton,
  Alert
} from '@mui/material';
import { Close as CloseIcon, Close as X } from '@mui/icons-material';
import GitHubRepositorySearch from './GitHubRepositorySearch';
import CloneProgress from './CloneProgress';
import { githubService } from '../../services/github';
import LoadingSpinner from '../common/LoadingSpinner';

const RepositoryForm = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    path: '',
    name: '',
    branch: 'main',
    description: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [currentStep, setCurrentStep] = useState('');
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      // Show different steps based on the operation
      if (formData.path.includes('github.com')) {
        setCurrentStep('🔄 Cloning repository from GitHub...');
        await new Promise(resolve => setTimeout(resolve, 1000)); // Brief delay to show step
        
        setCurrentStep('📁 Analyzing repository structure...');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setCurrentStep('🤖 Generating AI descriptions...');
      } else {
        setCurrentStep('📁 Analyzing local repository...');
        await new Promise(resolve => setTimeout(resolve, 500));
        
        setCurrentStep('🤖 Generating AI descriptions...');
      }
      
      await onSubmit(formData);
      
      setCurrentStep('✅ Repository added successfully!');
    } catch (error) {
      console.error('Error adding repository:', error);
      setError(error.response?.data?.detail || error.message || 'Failed to add repository');
      setCurrentStep('');
    } finally {
      setIsLoading(false);
      setCurrentStep('');
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear error when user starts typing
    if (error) setError(null);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Add Remote Repository</h2>
          <button
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
            disabled={isLoading}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Error Display */}
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-800 text-sm">{error}</p>
          </div>
        )}

        {/* Progress Display */}
        {isLoading && currentStep && (
          <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <LoadingSpinner size="sm" />
              <p className="text-blue-800 text-sm">{currentStep}</p>
            </div>
            <div className="mt-2 text-xs text-blue-600">
              This may take several minutes for larger repositories...
            </div>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Repository URL/Path *
            </label>
            <input
              type="text"
              name="path"
              value={formData.path}
              onChange={handleChange}
              placeholder="https://github.com/owner/repository or /local/path"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              required
              disabled={isLoading}
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
              disabled={isLoading}
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
              disabled={isLoading}
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
              disabled={isLoading}
            />
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 flex items-center space-x-2 min-w-[120px]"
            >
              {isLoading && <LoadingSpinner size="sm" />}
              <span>{isLoading ? 'Adding...' : 'Add Repository'}</span>
            </button>
          </div>
        </form>

        {/* Helpful Information */}
        {!isLoading && (
          <div className="mt-4 p-3 bg-gray-50 rounded-lg">
            <p className="text-xs text-gray-600">
              💡 <strong>Note:</strong> Adding repositories may take 3-5 minutes for cloning, parsing, and AI analysis.
              Large repositories may take even longer.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default RepositoryForm;