import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { GitBranch, FileText, Search, Activity, Plus } from 'lucide-react';
import Layout from '../components/layout/Layout';
import StatusBadge from '../components/common/StatusBadge';
import LoadingSpinner from '../components/common/LoadingSpinner';
import { repositoryService } from '../services/repositories';

const Dashboard = () => {
  const [repositories, setRepositories] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [stats, setStats] = useState({
    totalRepos: 0,
    indexedRepos: 0,
    totalFunctions: 0,
    recentActivity: []
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setIsLoading(true);
      const response = await repositoryService.getRepositories();
      const repos = response.data.repositories || [];
      setRepositories(repos);
      
      // Calculate stats
      setStats({
        totalRepos: repos.length,
        indexedRepos: repos.filter(r => r.status === 'indexed').length,
        totalFunctions: repos.reduce((sum, r) => sum + (r.function_count || 0), 0),
        recentActivity: repos.slice(0, 5) // Show recent 5
      });
    } catch (error) {
      console.error('Error loading dashboard data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center py-12">
          <LoadingSpinner size="lg" />
          <span className="ml-3 text-gray-600">Loading dashboard...</span>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-8">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">Welcome to Multi-Agent Research System</p>
          </div>
          <Link
            to="/repositories"
            className="bg-primary-500 text-white px-4 py-2 rounded-lg flex items-center space-x-2 hover:bg-primary-600"
          >
            <Plus className="w-4 h-4" />
            <span>Add Repository</span>
          </Link>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <StatCard
            title="Total Repositories"
            value={stats.totalRepos}
            icon={<GitBranch className="w-6 h-6" />}
            color="blue"
          />
          <StatCard
            title="Indexed Repositories"
            value={stats.indexedRepos}
            icon={<FileText className="w-6 h-6" />}
            color="green"
          />
          <StatCard
            title="Total Functions"
            value={stats.totalFunctions}
            icon={<Search className="w-6 h-6" />}
            color="purple"
          />
          <StatCard
            title="System Status"
            value="Active"
            icon={<Activity className="w-6 h-6" />}
            color="primary"
          />
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Link
              to="/repositories"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <GitBranch className="w-8 h-8 text-primary-500 mb-2" />
              <h3 className="font-medium">Manage Repositories</h3>
              <p className="text-sm text-gray-600">Add, view, and manage your code repositories</p>
            </Link>
            
            <Link
              to="/chat"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <Search className="w-8 h-8 text-primary-500 mb-2" />
              <h3 className="font-medium">Kenobi Chat</h3>
              <p className="text-sm text-gray-600">Ask questions about your codebase</p>
            </Link>
            
            <Link
              to="/documentation"
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors"
            >
              <FileText className="w-8 h-8 text-primary-500 mb-2" />
              <h3 className="font-medium">Documentation</h3>
              <p className="text-sm text-gray-600">Browse generated documentation</p>
            </Link>
          </div>
        </div>

        {/* Recent Repositories */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold">Recent Repositories</h2>
              <Link to="/repositories" className="text-primary-600 hover:text-primary-700 text-sm">
                View all
              </Link>
            </div>
          </div>
          
          <div className="divide-y divide-gray-200">
            {repositories.length > 0 ? (
              repositories.slice(0, 5).map((repo) => (
                <div key={repo.id} className="px-6 py-4 flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <GitBranch className="w-5 h-5 text-gray-400" />
                    <div>
                      <h3 className="font-medium">{repo.name}</h3>
                      <p className="text-sm text-gray-600 truncate max-w-md">{repo.path}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <StatusBadge status={repo.status || 'indexed'} />
                    <Link
                      to={`/repositories/${repo.id}/functionalities`}
                      className="text-primary-600 hover:text-primary-700 text-sm"
                    >
                      View Functions
                    </Link>
                  </div>
                </div>
              ))
            ) : (
              <div className="px-6 py-8 text-center text-gray-500">
                <GitBranch className="w-12 h-12 text-gray-300 mx-auto mb-3" />
                <p>No repositories yet. Add your first repository to get started.</p>
                <Link
                  to="/repositories"
                  className="text-primary-600 hover:text-primary-700 mt-2 inline-block"
                >
                  Add Repository
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

const StatCard = ({ title, value, icon, color }) => {
  const colorClasses = {
    blue: 'text-blue-600 bg-blue-100',
    green: 'text-green-600 bg-green-100',
    purple: 'text-purple-600 bg-purple-100',
    primary: 'text-primary-600 bg-primary-100'
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;