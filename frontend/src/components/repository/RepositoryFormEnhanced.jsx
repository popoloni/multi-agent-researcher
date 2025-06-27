/**
 * Enhanced Repository Form Component
 * Provides both GitHub search and manual URL/path input with tabbed interface
 */

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
import { Close as CloseIcon } from '@mui/icons-material';
import GitHubRepositorySearch from './GitHubRepositorySearch';
import CloneProgress from './CloneProgress';
import { githubService } from '../../services/github';

const RepositoryFormEnhanced = ({ open, onSubmit, onCancel }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    path: '',
    name: '',
    branch: 'main',
    description: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [cloneOperations, setCloneOperations] = useState([]);

  // Handle tab change
  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
    setError(null);
  };

  // Handle manual form submission
  const handleManualSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);
    
    try {
      // Check if it's a GitHub URL and parse it
      const parsed = githubService.parseGitHubUrl(formData.path);
      
      if (parsed) {
        // It's a GitHub URL, use GitHub clone endpoint
        const cloneData = {
          owner: parsed.owner,
          repo: parsed.repo,
          branch: formData.branch || 'main',
          local_name: formData.name || null
        };
        
        const result = await githubService.cloneRepository(cloneData);
        await onSubmit(result);
      } else {
        // It's a local path or other URL, use original submission
        await onSubmit(formData);
      }
    } catch (error) {
      console.error('Error adding repository:', error);
      setError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle GitHub repository clone
  const handleGitHubClone = async (cloneResult) => {
    try {
      // Add to clone operations for tracking
      const operation = {
        repository_id: cloneResult.repository_id,
        owner: cloneResult.repository.owner,
        repo: cloneResult.repository.repo,
        branch: cloneResult.repository.branch,
        status: 'completed',
        progress: 100,
        message: 'Repository cloned successfully',
        started_at: new Date().toISOString(),
        completed_at: new Date().toISOString(),
        ...cloneResult.repository
      };
      
      setCloneOperations(prev => [...prev, operation]);
      
      // Submit to parent component
      await onSubmit(cloneResult);
    } catch (error) {
      console.error('Error handling GitHub clone:', error);
      setError(error.message);
    }
  };

  // Handle form field changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    setError(null);
  };

  // Handle retry clone
  const handleRetryClone = (operation) => {
    // Remove failed operation and retry
    setCloneOperations(prev => prev.filter(op => op.repository_id !== operation.repository_id));
    // Could trigger a new clone here
  };

  // Handle cancel clone
  const handleCancelClone = (operation) => {
    setCloneOperations(prev => 
      prev.map(op => 
        op.repository_id === operation.repository_id 
          ? { ...op, status: 'failed', message: 'Cancelled by user' }
          : op
      )
    );
  };

  // Handle remove operation
  const handleRemoveOperation = (operation) => {
    setCloneOperations(prev => prev.filter(op => op.repository_id !== operation.repository_id));
  };

  // Tab panel component
  const TabPanel = ({ children, value, index, ...other }) => (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`repository-tabpanel-${index}`}
      aria-labelledby={`repository-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );

  return (
    <Dialog 
      open={open} 
      onClose={onCancel} 
      maxWidth="lg" 
      fullWidth
      PaperProps={{
        sx: { minHeight: '70vh' }
      }}
    >
      <DialogTitle>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Typography variant="h6">Add Repository</Typography>
          <IconButton onClick={onCancel} size="small">
            <CloseIcon />
          </IconButton>
        </Box>
      </DialogTitle>
      
      <DialogContent dividers>
        {/* Error Display */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        
        {/* Clone Progress */}
        {cloneOperations.length > 0 && (
          <CloneProgress
            cloneOperations={cloneOperations}
            onRetryClone={handleRetryClone}
            onCancelClone={handleCancelClone}
            onRemoveOperation={handleRemoveOperation}
          />
        )}
        
        {/* Tab Navigation */}
        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}>
          <Tabs value={activeTab} onChange={handleTabChange}>
            <Tab label="GitHub Search" />
            <Tab label="Manual URL/Path" />
          </Tabs>
        </Box>
        
        {/* GitHub Search Tab */}
        <TabPanel value={activeTab} index={0}>
          <GitHubRepositorySearch
            onRepositorySelect={(repo) => {
              // Could be used for preview functionality
              console.log('Repository selected:', repo);
            }}
            onCloneRepository={handleGitHubClone}
          />
        </TabPanel>
        
        {/* Manual URL/Path Tab */}
        <TabPanel value={activeTab} index={1}>
          <Box component="form" onSubmit={handleManualSubmit}>
            <Typography variant="h6" gutterBottom>
              Add Repository Manually
            </Typography>
            
            <Typography variant="body2" color="text.secondary" paragraph>
              Enter a GitHub URL, Git repository URL, or local directory path.
            </Typography>
            
            <TextField
              fullWidth
              label="Repository URL/Path"
              name="path"
              value={formData.path}
              onChange={handleChange}
              placeholder="https://github.com/user/repo or /path/to/local/repo"
              required
              sx={{ mb: 2 }}
              helperText="GitHub URLs will be automatically detected and cloned with enhanced features"
            />
            
            <TextField
              fullWidth
              label="Display Name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              placeholder="Optional display name"
              sx={{ mb: 2 }}
              helperText="Leave empty to use repository name"
            />
            
            <TextField
              fullWidth
              label="Branch"
              name="branch"
              value={formData.branch}
              onChange={handleChange}
              placeholder="main"
              sx={{ mb: 2 }}
              helperText="Branch to clone (for Git repositories)"
            />
            
            <TextField
              fullWidth
              label="Description"
              name="description"
              value={formData.description}
              onChange={handleChange}
              placeholder="Optional description"
              multiline
              rows={3}
              sx={{ mb: 3 }}
            />
            
            <Box display="flex" justifyContent="flex-end" gap={2}>
              <Button
                type="button"
                onClick={onCancel}
                color="secondary"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                disabled={isLoading || !formData.path.trim()}
              >
                {isLoading ? 'Adding...' : 'Add Repository'}
              </Button>
            </Box>
          </Box>
        </TabPanel>
      </DialogContent>
    </Dialog>
  );
};

export default RepositoryFormEnhanced;