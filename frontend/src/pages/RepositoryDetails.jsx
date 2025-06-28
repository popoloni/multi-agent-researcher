import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { FileText, GitBranch, Calendar, Code, Hash, ExternalLink } from 'lucide-react';
import Layout from '../components/layout/Layout';
import { repositoryService } from '../services/repositories';

const RepositoryDetails = () => {
  const { repositoryId } = useParams();
  const [repository, setRepository] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRepositoryDetails();
  }, [repositoryId]);

  const loadRepositoryDetails = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await repositoryService.getRepositoryDetails(repositoryId);
      setRepository(response.data);
    } catch (err) {
      console.error('Error loading repository details:', err);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const breadcrumbItems = [
    { label: 'Dashboard', path: '/' },
    { label: 'Repositories', path: '/repositories' },
    { label: repository?.name || 'Repository Details', path: `/repositories/${repositoryId}` }
  ];

  if (isLoading) {
    return (
      <Layout breadcrumbItems={breadcrumbItems}>
        <div className="flex justify-center items-center h-64">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
          <p className="ml-3 text-gray-500">Loading repository details...</p>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout breadcrumbItems={breadcrumbItems}>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-red-800 mb-2">Error Loading Repository</h2>
          <p className="text-red-700 mb-4">{error}</p>
          <button
            onClick={loadRepositoryDetails}
            className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700"
          >
            Try Again
          </button>
        </div>
      </Layout>
    );
  }

  if (!repository) {
    return (
      <Layout breadcrumbItems={breadcrumbItems}>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Repository Not Found</h2>
          <p className="text-gray-600 mb-4">The requested repository could not be found.</p>
          <Link
            to="/repositories"
            className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
          >
            Back to Repositories
          </Link>
        </div>
      </Layout>
    );
  }

  return (
    <Layout breadcrumbItems={breadcrumbItems}>
      <div className="space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">{repository.name}</h1>
              <div className="flex items-center space-x-4 text-sm text-gray-600">
                <div className="flex items-center">
                  <Code className="w-4 h-4 mr-1" />
                  {repository.language}
                </div>
                {repository.framework && (
                  <div className="flex items-center">
                    <Hash className="w-4 h-4 mr-1" />
                    {repository.framework}
                  </div>
                )}
                <div className="flex items-center">
                  <Calendar className="w-4 h-4 mr-1" />
                  Indexed {new Date(repository.indexed_at).toLocaleDateString()}
                </div>
              </div>
            </div>
            <div className="flex space-x-3">
              <Link
                to={`/repositories/${repository.id}/functionalities`}
                className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 flex items-center space-x-2"
              >
                <FileText className="w-4 h-4" />
                <span>View Functionalities</span>
              </Link>
              <Link
                to={`/repositories/${repository.id}/documentation`}
                className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 flex items-center space-x-2"
              >
                <FileText className="w-4 h-4" />
                <span>View Documentation</span>
              </Link>
            </div>
          </div>
        </div>

        {/* Statistics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <FileText className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Files</p>
                <p className="text-2xl font-bold text-gray-900">{repository.file_count.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <Code className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Lines of Code</p>
                <p className="text-2xl font-bold text-gray-900">{repository.line_count.toLocaleString()}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <Hash className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Language</p>
                <p className="text-2xl font-bold text-gray-900">{repository.language}</p>
              </div>
            </div>
          </div>
        </div>

        {/* Repository Information */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Repository Information</h2>
          </div>
          <div className="p-6">
            <dl className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <dt className="text-sm font-medium text-gray-600">Repository ID</dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono">{repository.id}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-600">Local Path</dt>
                <dd className="mt-1 text-sm text-gray-900 font-mono">{repository.local_path}</dd>
              </div>
              <div>
                <dt className="text-sm font-medium text-gray-600">Language</dt>
                <dd className="mt-1 text-sm text-gray-900">{repository.language}</dd>
              </div>
              {repository.framework && (
                <div>
                  <dt className="text-sm font-medium text-gray-600">Framework</dt>
                  <dd className="mt-1 text-sm text-gray-900">{repository.framework}</dd>
                </div>
              )}
              <div>
                <dt className="text-sm font-medium text-gray-600">Indexed At</dt>
                <dd className="mt-1 text-sm text-gray-900">
                  {new Date(repository.indexed_at).toLocaleString()}
                </dd>
              </div>
            </dl>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-semibold text-gray-900">Quick Actions</h2>
          </div>
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Link
                to={`/repositories/${repository.id}/functionalities`}
                className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <FileText className="w-8 h-8 text-primary-600 mr-4" />
                <div>
                  <h3 className="font-medium text-gray-900">View Functionalities</h3>
                  <p className="text-sm text-gray-600">Browse extracted functions, classes, and methods</p>
                </div>
              </Link>

              <Link
                to={`/repositories/${repository.id}/documentation`}
                className="flex items-center p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
              >
                <FileText className="w-8 h-8 text-green-600 mr-4" />
                <div>
                  <h3 className="font-medium text-gray-900">View Documentation</h3>
                  <p className="text-sm text-gray-600">Read generated technical documentation</p>
                </div>
              </Link>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default RepositoryDetails;