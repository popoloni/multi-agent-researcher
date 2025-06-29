import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Repositories from './pages/Repositories';
import RepositoryDetails from './pages/RepositoryDetails';
import Chat from './pages/Chat';
import Documentation from './pages/Documentation';
import FunctionalitiesPage from './pages/FunctionalitiesPage';
import Layout from './components/layout/Layout';
import { NotificationProvider } from './contexts/NotificationContext';
import './styles/globals.css';

function App() {
  return (
    <NotificationProvider>
      <Router>
        <div className="App">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/repositories" element={<Repositories />} />
          <Route path="/repositories/:repositoryId" element={<RepositoryDetails />} />
          <Route 
            path="/repositories/:repositoryId/functionalities" 
            element={<FunctionalitiesPage />} 
          />
          <Route 
            path="/repositories/:repositoryId/documentation" 
            element={<Documentation />} 
          />
          <Route 
            path="/documentation" 
            element={
              <Layout>
                <div className="text-center py-12">
                  <h1 className="text-2xl font-bold text-gray-900 mb-4">Documentation</h1>
                  <p className="text-gray-600">Select a repository to view its documentation.</p>
                </div>
              </Layout>
            } 
          />
          <Route path="/chat" element={<Chat />} />
        </Routes>
        </div>
      </Router>
    </NotificationProvider>
  );
}

export default App;