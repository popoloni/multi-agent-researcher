import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import FunctionalitiesRegistry from '../components/documentation/FunctionalitiesRegistry';
import { repositoryService } from '../services/repositories';

const Documentation = () => {
  const { repositoryId } = useParams();
  const [repository, setRepository] = useState(null);
  const [selectedBranch, setSelectedBranch] = useState('main');
  const [apiEndpoints, setApiEndpoints] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (repositoryId) {
      loadRepositoryDetails();
      loadFunctionalities();
    }
  }, [repositoryId, selectedBranch]);

  const loadRepositoryDetails = async () => {
    try {
      setIsLoading(true);
      const response = await repositoryService.getRepositoryDetails(repositoryId);
      setRepository(response.data);
    } catch (err) {
      setError(err.message);
      console.error('Error loading repository details:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const loadFunctionalities = async () => {
    try {
      const response = await repositoryService.getFunctionalitiesRegistry(repositoryId, selectedBranch);
      setApiEndpoints(response.data.endpoints || []);
    } catch (err) {
      console.error('Error loading functionalities:', err);
      setApiEndpoints([]);
    }
  };

  const handleGenerateDocumentation = async (repoId, branch) => {
    try {
      await repositoryService.createIndexing(repoId);
      // Reload functionalities after generation
      await loadFunctionalities();
    } catch (error) {
      console.error('Error generating documentation:', error);
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="text-red-600 mb-4">Error loading repository</div>
          <p className="text-gray-600">{error}</p>
        </div>
      </Layout>
    );
  }

  if (!repository) {
    return (
      <Layout>
        <div className="text-center py-12">
          <div className="text-gray-600">Repository not found</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        <FunctionalitiesRegistry
          repository={repository}
          branch={selectedBranch}
          apiEndpoints={apiEndpoints}
          onGenerateDocumentation={handleGenerateDocumentation}
          onBranchChange={setSelectedBranch}
        />
      </div>
    </Layout>
  );
};

export default Documentation;