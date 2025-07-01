# Repository Health Check and Auto-Recovery

This document describes the repository health checking and automatic recovery features that ensure repository data integrity and availability.

## Overview

The system now includes comprehensive health checking and automatic recovery capabilities to handle scenarios where repository files become missing, corrupted, or inaccessible. This prevents the "No functionalities found" issue that can occur when repository metadata exists but the actual files are missing.

## Features

### 🔍 Health Checking
- **File Existence Verification**: Checks if repository files are accessible
- **File Count Validation**: Compares actual vs expected file counts
- **Directory Integrity**: Verifies repository directory structure
- **Access Permission Testing**: Ensures files can be read
- **Detailed Diagnostics**: Provides specific error information and recommendations

### 🔄 Auto-Recovery
- **Automatic Re-cloning**: Re-clones repositories from source when files are missing
- **GitHub Integration**: Uses enhanced GitHub cloning for GitHub repositories
- **Metadata Preservation**: Maintains repository IDs and metadata during recovery
- **Cache Invalidation**: Clears analysis cache after recovery to force re-parsing
- **Progress Tracking**: Detailed logging of recovery actions

### 🛡️ Automatic Integration
- **Transparent Operation**: Health checks happen automatically before analysis
- **Graceful Degradation**: Provides helpful error messages when recovery fails
- **Configurable Behavior**: Can disable auto-recovery if needed
- **Performance Optimized**: Minimal overhead for healthy repositories

## API Endpoints

### Health Check Endpoint

```http
GET /kenobi/repositories/{repository_id}/health
```

**Response Example:**
```json
{
  "repository_id": "49fb6de0-79bd-4f51-a601-53b1d842086c",
  "health_check": {
    "healthy": true,
    "status": "healthy",
    "message": "Repository is healthy and accessible",
    "accessible_files": 79,
    "expected_files": 79,
    "missing_files": [],
    "recommendations": []
  },
  "timestamp": "2025-07-01T23:10:12.643493"
}
```

**Health Status Values:**
- `healthy`: Repository is fully accessible
- `repository_not_found`: Repository metadata missing
- `local_path_missing`: Repository directory doesn't exist
- `empty_directory`: Repository directory is empty
- `no_accessible_files`: No code files can be accessed
- `file_count_mismatch`: Significant difference in file count
- `directory_access_error`: Cannot access repository directory
- `health_check_failed`: Health check system error

### Manual Recovery Endpoint

```http
POST /kenobi/repositories/{repository_id}/recover?force=false
```

**Parameters:**
- `force` (boolean): Force recovery even if repository appears healthy

**Response Example:**
```json
{
  "success": true,
  "repository_id": "49fb6de0-79bd-4f51-a601-53b1d842086c",
  "recovery_result": {
    "success": true,
    "status": "recovery_successful",
    "message": "Repository astropy successfully recovered",
    "actions_taken": [
      "initiated_recovery",
      "backed_up_metadata",
      "re_cloned_from_github",
      "updated_repository_id",
      "recovery_verified",
      "cleared_analysis_cache"
    ],
    "new_file_count": 79,
    "new_line_count": 33792
  },
  "message": "Repository recovery completed successfully",
  "timestamp": "2025-07-01T23:11:00.620079"
}
```

### Enhanced Functionalities Endpoint

```http
GET /kenobi/repositories/{repository_id}/functionalities?auto_recover=true&include_health_info=false
```

**Parameters:**
- `auto_recover` (boolean): Enable automatic recovery if files are missing (default: true)
- `include_health_info` (boolean): Include health check information in response (default: false)

**Automatic Behavior:**
1. Checks repository health before analysis
2. If unhealthy and auto-recovery is enabled, attempts recovery
3. If recovery succeeds, proceeds with normal analysis
4. If recovery fails, returns detailed error information

### Enhanced Analysis Endpoint

```http
GET /kenobi/repositories/{repository_id}/analysis?auto_recover=true&force_refresh=false
```

**Parameters:**
- `auto_recover` (boolean): Enable automatic recovery if files are missing (default: true)
- `force_refresh` (boolean): Force regeneration of analysis even if cached (default: false)

## Error Handling

### Auto-Recovery Failed (HTTP 503)
```json
{
  "error": "Repository files are missing and auto-recovery failed",
  "message": "Repository repo-id is unhealthy and auto-recovery failed: Recovery failed: network error",
  "health_status": {
    "healthy": false,
    "status": "local_path_missing",
    "recommendations": ["Repository files are completely missing", "Auto-recovery available: re-clone from source"]
  },
  "suggestions": [
    "Repository files may be corrupted or source URL may be inaccessible",
    "Try manual re-indexing of the repository",
    "Check if the source repository is still available"
  ]
}
```

### Repository Not Accessible (HTTP 422)
```json
{
  "error": "Repository is not accessible",
  "message": "Repository repo-id is unhealthy: File count mismatch. Health status: file_count_mismatch",
  "health_status": {
    "healthy": false,
    "status": "file_count_mismatch",
    "accessible_files": 45,
    "expected_files": 79,
    "recommendations": ["Significant file count difference detected", "Consider re-cloning to ensure completeness"]
  },
  "auto_recovery_available": false,
  "suggestions": ["Significant file count difference detected", "Consider re-cloning to ensure completeness"]
}
```

## Usage Examples

### Basic Health Check
```bash
curl -X GET "http://localhost:12000/kenobi/repositories/{repo_id}/health"
```

### Manual Recovery
```bash
curl -X POST "http://localhost:12000/kenobi/repositories/{repo_id}/recover"
```

### Force Recovery
```bash
curl -X POST "http://localhost:12000/kenobi/repositories/{repo_id}/recover?force=true"
```

### Get Functionalities with Health Info
```bash
curl -X GET "http://localhost:12000/kenobi/repositories/{repo_id}/functionalities?include_health_info=true"
```

### Disable Auto-Recovery
```bash
curl -X GET "http://localhost:12000/kenobi/repositories/{repo_id}/functionalities?auto_recover=false"
```

## Implementation Details

### Health Check Process
1. **Repository Metadata Check**: Verify repository exists in database
2. **Path Existence Check**: Ensure local repository path exists
3. **Directory Validation**: Check if directory contains repository content
4. **File Accessibility Test**: Attempt to read code files
5. **File Count Comparison**: Compare actual vs expected file counts
6. **Recommendation Generation**: Provide specific recovery suggestions

### Auto-Recovery Process
1. **Health Assessment**: Check if recovery is needed
2. **Source URL Validation**: Ensure repository has a source URL
3. **Metadata Backup**: Preserve original repository metadata
4. **Directory Cleanup**: Remove corrupted/incomplete files
5. **Repository Re-cloning**: Clone from source using appropriate method
6. **ID Consistency**: Maintain original repository ID
7. **Verification**: Confirm recovery success with health check
8. **Cache Invalidation**: Clear analysis cache to force re-parsing

### Recovery Methods
- **GitHub Repositories**: Uses enhanced GitHub cloning with progress tracking
- **Generic Git Repositories**: Uses standard git clone
- **Fallback Handling**: Attempts multiple recovery methods if first fails

## Best Practices

### For Users
1. **Monitor Health**: Regularly check repository health for critical repositories
2. **Manual Recovery**: Use manual recovery for immediate fixes
3. **Source URLs**: Ensure repositories have accessible source URLs
4. **Network Connectivity**: Verify network access for recovery operations

### For Developers
1. **Error Handling**: Always handle health check and recovery errors
2. **Progress Monitoring**: Use health endpoints to monitor system status
3. **Cache Management**: Clear caches after manual repository operations
4. **Testing**: Test recovery scenarios in development environments

## Configuration

### Environment Variables
- Repository storage path: `/tmp/kenobi_repos/` (configurable)
- Auto-recovery timeout: 300 seconds
- Health check cache: 60 seconds

### Recovery Triggers
Auto-recovery is triggered for these health status values:
- `local_path_missing`
- `empty_directory`
- `no_accessible_files`

### Excluded from Auto-Recovery
- `file_count_mismatch` (requires manual intervention)
- `directory_access_error` (permission issues)
- `health_check_failed` (system errors)

## Monitoring and Logging

### Log Messages
- Health check results are logged at INFO level
- Recovery operations are logged at INFO level
- Errors are logged at ERROR level with full context

### Metrics
- Health check success/failure rates
- Recovery success/failure rates
- Repository availability statistics
- Performance metrics for health checks and recovery

## Troubleshooting

### Common Issues

**Repository Not Found**
- Check if repository ID is correct
- Verify repository was properly indexed

**Recovery Fails**
- Check network connectivity
- Verify source repository URL is accessible
- Check disk space for cloning
- Review logs for specific error details

**Permission Errors**
- Check file system permissions
- Verify write access to repository storage directory

**Network Timeouts**
- Check firewall settings
- Verify DNS resolution
- Consider using manual recovery with longer timeout

### Recovery Status Codes
- `recovery_successful`: Recovery completed successfully
- `recovery_not_needed`: Repository is healthy
- `no_source_url`: Cannot recover without source URL
- `clone_failed`: Git clone operation failed
- `recovery_verification_failed`: Recovery completed but health check still fails
- `recovery_system_error`: Internal recovery system error

## Future Enhancements

### Planned Features
1. **Incremental Recovery**: Recover only missing/corrupted files
2. **Multiple Source URLs**: Fallback sources for recovery
3. **Scheduled Health Checks**: Automatic periodic health monitoring
4. **Recovery Analytics**: Detailed recovery success metrics
5. **Custom Recovery Strategies**: Configurable recovery behavior per repository
6. **Backup Integration**: Integration with backup systems for faster recovery 