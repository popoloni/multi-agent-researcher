/**
 * GitHub Repository Search Component
 * Provides search functionality for GitHub repositories with filters and preview
 */

import React, { useState, useEffect, useCallback } from 'react';
import {
  Box,
  TextField,
  Button,
  Grid,
  Card,
  CardContent,
  Typography,
  Chip,
  IconButton,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Pagination,
  CircularProgress,
  Alert,
  Tooltip,
  Avatar,
  Divider,
  Link
} from '@mui/material';
import {
  Search as SearchIcon,
  Star as StarIcon,
  ForkRight as ForkIcon,
  BugReport as IssueIcon,
  Download as CloneIcon,
  Visibility as PreviewIcon,
  Language as LanguageIcon,
  Schedule as UpdatedIcon,
  Person as OwnerIcon
} from '@mui/icons-material';
import { githubService } from '../../services/github';

const GitHubRepositorySearch = ({ onRepositorySelect, onCloneRepository }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({
    language: '',
    sort: 'stars',
    order: 'desc'
  });
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 12,
    total_count: 0,
    has_next: false
  });
  const [selectedRepo, setSelectedRepo] = useState(null);
  const [branches, setBranches] = useState([]);
  const [selectedBranch, setSelectedBranch] = useState('main');
  const [cloning, setCloning] = useState(false);

  // Programming languages for filter
  const languages = [
    'JavaScript', 'TypeScript', 'Python', 'Java', 'C++', 'C#', 'PHP', 'Ruby',
    'Go', 'Rust', 'Swift', 'Kotlin', 'Dart', 'HTML', 'CSS', 'Shell'
  ];

  // Sort options
  const sortOptions = [
    { value: 'stars', label: 'Stars' },
    { value: 'forks', label: 'Forks' },
    { value: 'updated', label: 'Recently Updated' },
    { value: 'help-wanted-issues', label: 'Help Wanted' }
  ];

  // Debounced search function
  const debouncedSearch = useCallback(
    debounce(async (query, searchFilters, page = 1) => {
      if (!query.trim()) {
        setSearchResults([]);
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const result = await githubService.searchRepositories(query, {
          ...searchFilters,
          page,
          per_page: pagination.per_page
        });

        setSearchResults(result.repositories || []);
        setPagination(prev => ({
          ...prev,
          page,
          total_count: result.total_count || 0,
          has_next: result.has_next || false
        }));
      } catch (err) {
        setError(err.message);
        setSearchResults([]);
      } finally {
        setLoading(false);
      }
    }, 500),
    [pagination.per_page]
  );

  // Handle search
  const handleSearch = (page = 1) => {
    debouncedSearch(searchQuery, filters, page);
  };

  // Handle filter change
  const handleFilterChange = (filterName, value) => {
    const newFilters = { ...filters, [filterName]: value };
    setFilters(newFilters);
    if (searchQuery.trim()) {
      debouncedSearch(searchQuery, newFilters, 1);
    }
  };

  // Handle page change
  const handlePageChange = (event, page) => {
    setPagination(prev => ({ ...prev, page }));
    handleSearch(page);
  };

  // Handle repository selection for preview
  const handleRepositoryPreview = async (repo) => {
    setSelectedRepo(repo);
    setSelectedBranch(repo.default_branch || 'main');
    
    try {
      const branchList = await githubService.listBranches(repo.owner, repo.name);
      setBranches(branchList);
    } catch (err) {
      console.error('Failed to load branches:', err);
      setBranches([{ name: repo.default_branch || 'main' }]);
    }
  };

  // Handle repository clone
  const handleClone = async () => {
    if (!selectedRepo) return;

    setCloning(true);
    try {
      const cloneData = {
        owner: selectedRepo.owner,
        repo: selectedRepo.name,
        branch: selectedBranch,
        local_name: null // Use default name
      };

      const result = await githubService.cloneRepository(cloneData);
      
      if (onCloneRepository) {
        onCloneRepository(result);
      }

      setSelectedRepo(null);
    } catch (err) {
      setError(`Clone failed: ${err.message}`);
    } finally {
      setCloning(false);
    }
  };

  // Format date
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString();
  };

  // Calculate total pages
  const totalPages = Math.ceil(pagination.total_count / pagination.per_page);

  return (
    <Box sx={{ p: 3 }}>
      {/* Search Header */}
      <Typography variant="h5" gutterBottom>
        Search GitHub Repositories
      </Typography>
      
      {/* Search Controls */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <TextField
            fullWidth
            label="Search repositories..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
            InputProps={{
              endAdornment: (
                <IconButton onClick={() => handleSearch()}>
                  <SearchIcon />
                </IconButton>
              )
            }}
          />
        </Grid>
        
        <Grid item xs={12} md={2}>
          <FormControl fullWidth>
            <InputLabel>Language</InputLabel>
            <Select
              value={filters.language}
              onChange={(e) => handleFilterChange('language', e.target.value)}
              label="Language"
            >
              <MenuItem value="">All Languages</MenuItem>
              {languages.map(lang => (
                <MenuItem key={lang} value={lang}>{lang}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={2}>
          <FormControl fullWidth>
            <InputLabel>Sort by</InputLabel>
            <Select
              value={filters.sort}
              onChange={(e) => handleFilterChange('sort', e.target.value)}
              label="Sort by"
            >
              {sortOptions.map(option => (
                <MenuItem key={option.value} value={option.value}>
                  {option.label}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        
        <Grid item xs={12} md={2}>
          <FormControl fullWidth>
            <InputLabel>Order</InputLabel>
            <Select
              value={filters.order}
              onChange={(e) => handleFilterChange('order', e.target.value)}
              label="Order"
            >
              <MenuItem value="desc">Descending</MenuItem>
              <MenuItem value="asc">Ascending</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {/* Error Display */}
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Loading Indicator */}
      {loading && (
        <Box display="flex" justifyContent="center" sx={{ my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Search Results */}
      {!loading && searchResults.length > 0 && (
        <>
          <Typography variant="h6" gutterBottom>
            Found {pagination.total_count.toLocaleString()} repositories
          </Typography>
          
          <Grid container spacing={2}>
            {searchResults.map((repo) => (
              <Grid item xs={12} md={6} lg={4} key={repo.id}>
                <Card 
                  sx={{ 
                    height: '100%', 
                    display: 'flex', 
                    flexDirection: 'column',
                    '&:hover': { boxShadow: 4 }
                  }}
                >
                  <CardContent sx={{ flexGrow: 1 }}>
                    {/* Repository Header */}
                    <Box display="flex" alignItems="center" mb={1}>
                      <Avatar sx={{ width: 24, height: 24, mr: 1 }}>
                        <OwnerIcon fontSize="small" />
                      </Avatar>
                      <Typography variant="subtitle2" color="text.secondary">
                        {repo.owner}
                      </Typography>
                    </Box>
                    
                    {/* Repository Name */}
                    <Typography variant="h6" component="div" gutterBottom>
                      <Link 
                        href={repo.html_url} 
                        target="_blank" 
                        rel="noopener"
                        sx={{ textDecoration: 'none' }}
                      >
                        {repo.name}
                      </Link>
                    </Typography>
                    
                    {/* Description */}
                    <Typography 
                      variant="body2" 
                      color="text.secondary" 
                      sx={{ 
                        mb: 2, 
                        height: '3em', 
                        overflow: 'hidden',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical'
                      }}
                    >
                      {repo.description || 'No description available'}
                    </Typography>
                    
                    {/* Language and Topics */}
                    <Box mb={2}>
                      {repo.language && (
                        <Chip
                          icon={<LanguageIcon />}
                          label={repo.language}
                          size="small"
                          sx={{ 
                            mr: 1, 
                            mb: 1,
                            backgroundColor: githubService.getLanguageColor(repo.language),
                            color: 'white'
                          }}
                        />
                      )}
                      {repo.topics?.slice(0, 2).map(topic => (
                        <Chip
                          key={topic}
                          label={topic}
                          size="small"
                          variant="outlined"
                          sx={{ mr: 1, mb: 1 }}
                        />
                      ))}
                    </Box>
                    
                    {/* Repository Stats */}
                    <Box display="flex" alignItems="center" gap={2} mb={2}>
                      <Tooltip title="Stars">
                        <Box display="flex" alignItems="center">
                          <StarIcon fontSize="small" sx={{ mr: 0.5 }} />
                          <Typography variant="caption">
                            {githubService.formatStarCount(repo.stars)}
                          </Typography>
                        </Box>
                      </Tooltip>
                      
                      <Tooltip title="Forks">
                        <Box display="flex" alignItems="center">
                          <ForkIcon fontSize="small" sx={{ mr: 0.5 }} />
                          <Typography variant="caption">
                            {repo.forks}
                          </Typography>
                        </Box>
                      </Tooltip>
                      
                      <Tooltip title="Issues">
                        <Box display="flex" alignItems="center">
                          <IssueIcon fontSize="small" sx={{ mr: 0.5 }} />
                          <Typography variant="caption">
                            {repo.issues}
                          </Typography>
                        </Box>
                      </Tooltip>
                    </Box>
                    
                    {/* Updated Date */}
                    <Typography variant="caption" color="text.secondary" display="flex" alignItems="center">
                      <UpdatedIcon fontSize="small" sx={{ mr: 0.5 }} />
                      Updated {formatDate(repo.updated_at)}
                    </Typography>
                  </CardContent>
                  
                  {/* Action Buttons */}
                  <Box sx={{ p: 2, pt: 0 }}>
                    <Button
                      fullWidth
                      variant="outlined"
                      startIcon={<PreviewIcon />}
                      onClick={() => handleRepositoryPreview(repo)}
                      sx={{ mb: 1 }}
                    >
                      Preview & Clone
                    </Button>
                  </Box>
                </Card>
              </Grid>
            ))}
          </Grid>
          
          {/* Pagination */}
          {totalPages > 1 && (
            <Box display="flex" justifyContent="center" sx={{ mt: 4 }}>
              <Pagination
                count={totalPages}
                page={pagination.page}
                onChange={handlePageChange}
                color="primary"
                size="large"
              />
            </Box>
          )}
        </>
      )}

      {/* No Results */}
      {!loading && searchQuery && searchResults.length === 0 && (
        <Box textAlign="center" sx={{ my: 4 }}>
          <Typography variant="h6" color="text.secondary">
            No repositories found
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Try adjusting your search query or filters
          </Typography>
        </Box>
      )}

      {/* Repository Preview Modal */}
      {selectedRepo && (
        <Box
          sx={{
            position: 'fixed',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'rgba(0, 0, 0, 0.5)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            zIndex: 1300
          }}
          onClick={() => setSelectedRepo(null)}
        >
          <Card
            sx={{ 
              maxWidth: 600, 
              width: '90%', 
              maxHeight: '80vh', 
              overflow: 'auto',
              m: 2
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <CardContent>
              <Typography variant="h5" gutterBottom>
                {selectedRepo.owner}/{selectedRepo.name}
              </Typography>
              
              <Typography variant="body1" paragraph>
                {selectedRepo.description}
              </Typography>
              
              <Divider sx={{ my: 2 }} />
              
              {/* Repository Details */}
              <Grid container spacing={2} sx={{ mb: 3 }}>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Language</Typography>
                  <Typography variant="body2">{selectedRepo.language || 'Not specified'}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Size</Typography>
                  <Typography variant="body2">
                    {githubService.formatRepositorySize(selectedRepo.size)}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Stars</Typography>
                  <Typography variant="body2">{selectedRepo.stars}</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="subtitle2">Forks</Typography>
                  <Typography variant="body2">{selectedRepo.forks}</Typography>
                </Grid>
              </Grid>
              
              {/* Branch Selection */}
              <FormControl fullWidth sx={{ mb: 3 }}>
                <InputLabel>Branch</InputLabel>
                <Select
                  value={selectedBranch}
                  onChange={(e) => setSelectedBranch(e.target.value)}
                  label="Branch"
                >
                  {branches.map(branch => (
                    <MenuItem key={branch.name} value={branch.name}>
                      {branch.name}
                      {branch.name === selectedRepo.default_branch && ' (default)'}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              
              {/* Action Buttons */}
              <Box display="flex" gap={2}>
                <Button
                  variant="contained"
                  startIcon={<CloneIcon />}
                  onClick={handleClone}
                  disabled={cloning}
                  fullWidth
                >
                  {cloning ? 'Cloning...' : 'Clone Repository'}
                </Button>
                <Button
                  variant="outlined"
                  onClick={() => setSelectedRepo(null)}
                  fullWidth
                >
                  Cancel
                </Button>
              </Box>
            </CardContent>
          </Card>
        </Box>
      )}
    </Box>
  );
};

// Debounce utility function
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

export default GitHubRepositorySearch;