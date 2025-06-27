/**
 * Clone Progress Component
 * Displays real-time progress for repository cloning operations
 */

import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Button,
  Alert,
  Chip,
  IconButton,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon
} from '@mui/material';
import {
  Download as CloneIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Cancel as CancelIcon,
  Refresh as RetryIcon,
  ExpandMore as ExpandIcon,
  ExpandLess as CollapseIcon,
  Schedule as PendingIcon,
  CloudDownload as DownloadingIcon
} from '@mui/icons-material';
import { githubService } from '../../services/github';

const CloneProgress = ({ 
  cloneOperations = [], 
  onRetryClone, 
  onCancelClone,
  onRemoveOperation 
}) => {
  const [expandedOperations, setExpandedOperations] = useState(new Set());
  const [operations, setOperations] = useState(cloneOperations);

  // Update operations when prop changes
  useEffect(() => {
    setOperations(cloneOperations);
  }, [cloneOperations]);

  // Poll for status updates
  useEffect(() => {
    const pollInterval = setInterval(async () => {
      const updatedOperations = await Promise.all(
        operations.map(async (op) => {
          if (op.status === 'cloning' || op.status === 'pending') {
            try {
              const status = await githubService.getCloneStatus(op.repository_id);
              return { ...op, ...status };
            } catch (error) {
              console.error('Failed to get clone status:', error);
              return op;
            }
          }
          return op;
        })
      );
      
      setOperations(updatedOperations);
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [operations]);

  // Toggle operation details
  const toggleExpanded = (operationId) => {
    const newExpanded = new Set(expandedOperations);
    if (newExpanded.has(operationId)) {
      newExpanded.delete(operationId);
    } else {
      newExpanded.add(operationId);
    }
    setExpandedOperations(newExpanded);
  };

  // Handle cancel clone
  const handleCancel = async (operation) => {
    try {
      await githubService.cancelClone(operation.repository_id);
      if (onCancelClone) {
        onCancelClone(operation);
      }
    } catch (error) {
      console.error('Failed to cancel clone:', error);
    }
  };

  // Handle retry clone
  const handleRetry = (operation) => {
    if (onRetryClone) {
      onRetryClone(operation);
    }
  };

  // Handle remove operation
  const handleRemove = (operation) => {
    if (onRemoveOperation) {
      onRemoveOperation(operation);
    }
  };

  // Get status icon
  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <PendingIcon color="info" />;
      case 'cloning':
        return <DownloadingIcon color="primary" />;
      case 'completed':
        return <SuccessIcon color="success" />;
      case 'failed':
        return <ErrorIcon color="error" />;
      default:
        return <CloneIcon />;
    }
  };

  // Get status color
  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'info';
      case 'cloning':
        return 'primary';
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'default';
    }
  };

  // Get progress color
  const getProgressColor = (status) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      default:
        return 'primary';
    }
  };

  if (operations.length === 0) {
    return null;
  }

  return (
    <Box sx={{ mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Clone Operations
      </Typography>
      
      {operations.map((operation) => (
        <Card key={operation.repository_id} sx={{ mb: 2 }}>
          <CardContent>
            {/* Operation Header */}
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Box display="flex" alignItems="center" gap={1}>
                {getStatusIcon(operation.status)}
                <Typography variant="h6">
                  {operation.owner}/{operation.repo}
                </Typography>
                <Chip
                  label={operation.status}
                  color={getStatusColor(operation.status)}
                  size="small"
                />
                {operation.branch && operation.branch !== 'main' && (
                  <Chip
                    label={`branch: ${operation.branch}`}
                    variant="outlined"
                    size="small"
                  />
                )}
              </Box>
              
              <Box display="flex" alignItems="center" gap={1}>
                {/* Action Buttons */}
                {operation.status === 'cloning' && (
                  <Button
                    size="small"
                    startIcon={<CancelIcon />}
                    onClick={() => handleCancel(operation)}
                    color="error"
                  >
                    Cancel
                  </Button>
                )}
                
                {operation.status === 'failed' && (
                  <Button
                    size="small"
                    startIcon={<RetryIcon />}
                    onClick={() => handleRetry(operation)}
                    color="primary"
                  >
                    Retry
                  </Button>
                )}
                
                {(operation.status === 'completed' || operation.status === 'failed') && (
                  <Button
                    size="small"
                    onClick={() => handleRemove(operation)}
                    color="secondary"
                  >
                    Remove
                  </Button>
                )}
                
                {/* Expand/Collapse Button */}
                <IconButton
                  size="small"
                  onClick={() => toggleExpanded(operation.repository_id)}
                >
                  {expandedOperations.has(operation.repository_id) ? 
                    <CollapseIcon /> : <ExpandIcon />
                  }
                </IconButton>
              </Box>
            </Box>
            
            {/* Progress Bar */}
            <Box mb={2}>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                <Typography variant="body2" color="text.secondary">
                  {operation.message || 'Processing...'}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {Math.round(operation.progress || 0)}%
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={operation.progress || 0}
                color={getProgressColor(operation.status)}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>
            
            {/* Error Message */}
            {operation.status === 'failed' && operation.error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {operation.error}
              </Alert>
            )}
            
            {/* Success Message */}
            {operation.status === 'completed' && (
              <Alert severity="success" sx={{ mb: 2 }}>
                Repository cloned successfully! Ready for analysis.
              </Alert>
            )}
            
            {/* Expanded Details */}
            <Collapse in={expandedOperations.has(operation.repository_id)}>
              <Box sx={{ mt: 2, pt: 2, borderTop: 1, borderColor: 'divider' }}>
                <Typography variant="subtitle2" gutterBottom>
                  Operation Details
                </Typography>
                
                <List dense>
                  <ListItem>
                    <ListItemIcon>
                      <CloneIcon fontSize="small" />
                    </ListItemIcon>
                    <ListItemText
                      primary="Repository"
                      secondary={`${operation.owner}/${operation.repo}`}
                    />
                  </ListItem>
                  
                  {operation.branch && (
                    <ListItem>
                      <ListItemIcon>
                        <span style={{ fontSize: '1rem' }}>🌿</span>
                      </ListItemIcon>
                      <ListItemText
                        primary="Branch"
                        secondary={operation.branch}
                      />
                    </ListItem>
                  )}
                  
                  {operation.local_path && (
                    <ListItem>
                      <ListItemIcon>
                        <span style={{ fontSize: '1rem' }}>📁</span>
                      </ListItemIcon>
                      <ListItemText
                        primary="Local Path"
                        secondary={operation.local_path}
                      />
                    </ListItem>
                  )}
                  
                  {operation.started_at && (
                    <ListItem>
                      <ListItemIcon>
                        <span style={{ fontSize: '1rem' }}>⏰</span>
                      </ListItemIcon>
                      <ListItemText
                        primary="Started"
                        secondary={new Date(operation.started_at).toLocaleString()}
                      />
                    </ListItem>
                  )}
                  
                  {operation.completed_at && (
                    <ListItem>
                      <ListItemIcon>
                        <span style={{ fontSize: '1rem' }}>✅</span>
                      </ListItemIcon>
                      <ListItemText
                        primary="Completed"
                        secondary={new Date(operation.completed_at).toLocaleString()}
                      />
                    </ListItem>
                  )}
                  
                  {operation.file_count && (
                    <ListItem>
                      <ListItemIcon>
                        <span style={{ fontSize: '1rem' }}>📄</span>
                      </ListItemIcon>
                      <ListItemText
                        primary="Files"
                        secondary={`${operation.file_count.toLocaleString()} files`}
                      />
                    </ListItem>
                  )}
                  
                  {operation.size_bytes && (
                    <ListItem>
                      <ListItemIcon>
                        <span style={{ fontSize: '1rem' }}>💾</span>
                      </ListItemIcon>
                      <ListItemText
                        primary="Size"
                        secondary={githubService.formatRepositorySize(operation.size_bytes / 1024)}
                      />
                    </ListItem>
                  )}
                </List>
                
                {/* Progress History */}
                {operation.progress_history && operation.progress_history.length > 0 && (
                  <Box sx={{ mt: 2 }}>
                    <Typography variant="subtitle2" gutterBottom>
                      Progress History
                    </Typography>
                    <List dense>
                      {operation.progress_history.slice(-5).map((entry, index) => (
                        <ListItem key={index}>
                          <ListItemText
                            primary={entry.message}
                            secondary={`${entry.progress}% - ${new Date(entry.timestamp).toLocaleTimeString()}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </Box>
            </Collapse>
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};

export default CloneProgress;