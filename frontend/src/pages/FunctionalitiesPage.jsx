import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import Layout from '../components/layout/Layout';
import FunctionalitiesRegistry from '../components/documentation/FunctionalitiesRegistry';
import { repositoryService } from '../services/repositories';
import { documentationService } from '../services/documentation';

const FunctionalitiesPage = () => {
  const { repositoryId } = useParams();
  const [repository, setRepository] = useState(null);
  const [selectedBranch, setSelectedBranch] = useState('main');
  const [apiEndpoints, setApiEndpoints] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load repository and functionalities on mount
  useEffect(() => {
    if (repositoryId) {
      loadRepositoryDetails();
      loadFunctionalities();
    }
  }, [repositoryId, selectedBranch]);

  // Load repository details
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

  // Load functionalities
  const loadFunctionalities = async () => {
    try {
      const response = await repositoryService.getFunctionalitiesRegistry(repositoryId, selectedBranch);
      setApiEndpoints(response.data.functionalities || []);
    } catch (err) {
      console.error('Error loading functionalities:', err);
      setApiEndpoints([]);
    }
  };

  // Generate documentation
  const handleGenerateDocumentation = async (repoId, branch) => {
    if (!repository || !repository.id) return;
    
    try {
      // Generate documentation
      const response = await documentationService.generateDocumentation(repository.id, {
        branch: branch || selectedBranch
      });
      
      console.log('Documentation generated:', response);
      
      // Reload functionalities after generation
      await loadFunctionalities();
      
      // Show success message or redirect to documentation view
      alert('Documentation generated successfully!');
    } catch (error) {
      console.error('Error generating documentation:', error);
      alert('Error generating documentation: ' + error.message);
    }
  };

  // Handle branch change
  const handleBranchChange = (newBranch) => {
    setSelectedBranch(newBranch);
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

  return (
    <Layout>
      <FunctionalitiesRegistry
        repository={repository}
        branch={selectedBranch}
        apiEndpoints={apiEndpoints}
        onGenerateDocumentation={handleGenerateDocumentation}
        onBranchChange={handleBranchChange}
      />
    </Layout>
  );
};

export default FunctionalitiesPage;