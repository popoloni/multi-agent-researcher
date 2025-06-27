import React, { useState, useEffect } from 'react';
import Layout from '../components/layout/Layout';
import RepositoryList from '../components/repository/RepositoryList';
import { repositoryService } from '../services/repositories';

const Repositories = () => {
  console.log('Repositories component mounting...');
  const [repositories, setRepositories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    console.log('Repositories useEffect running...');
    loadRepositories();
  }, []);

  const loadRepositories = async () => {
    try {
      console.log('Loading repositories...');
      setIsLoading(true);
      setError(null);
      const response = await repositoryService.getRepositories();
      console.log('Repositories response:', response);
      setRepositories(response.data.repositories || []);
    } catch (err) {
      console.error('Error loading repositories:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddRepository = async (repositoryData) => {
    try {
      const response = await repositoryService.addRepository(repositoryData);
      
      // Add the new repository to the list
      const newRepo = {
        id: response.data.repository_id,
        name: repositoryData.name || repositoryData.path.split('/').pop(),
        path: repositoryData.path,
        branch: repositoryData.branch || 'main',
        status: 'indexing'
      };
      
      setRepositories(prev => [...prev, newRepo]);
      
      // Reload repositories to get updated status
      setTimeout(loadRepositories, 2000);
    } catch (error) {
      console.error('Error adding repository:', error);
      throw error;
    }
  };

  const handleDeleteRepository = async (repositoryId) => {
    if (!window.confirm('Are you sure you want to delete this repository?')) {
      return;
    }

    try {
      await repositoryService.deleteRepository(repositoryId);
      setRepositories(prev => prev.filter(repo => repo.id !== repositoryId));
    } catch (error) {
      console.error('Error deleting repository:', error);
      alert('Failed to delete repository. Please try again.');
    }
  };

  const breadcrumbItems = [
    { label: 'Dashboard', path: '/' },
    { label: 'Repositories', path: '/repositories' }
  ];

  return (
    <Layout breadcrumbItems={breadcrumbItems}>
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
          <p className="text-red-800">Error loading repositories: {error}</p>
          <button 
            onClick={loadRepositories}
            className="mt-2 text-red-600 hover:text-red-800 underline"
          >
            Try again
          </button>
        </div>
      )}
      
      <RepositoryList
        repositories={repositories}
        onAddRepository={handleAddRepository}
        onDeleteRepository={handleDeleteRepository}
        isLoading={isLoading}
      />
    </Layout>
  );
};

export default Repositories;