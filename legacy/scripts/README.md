# Legacy Scripts

This folder contains scripts that have been moved from the root directory during the startup script consolidation process.

## Scripts Moved Here

### start_services.sh
- **Reason**: Legacy script with hardcoded paths (`/workspace/multi-agent-researcher`) and outdated configuration
- **Replaced by**: `start_all.sh` (main script) and `start_dev.sh` (backend only)
- **Issues**: Used workspace-specific URLs and paths that don't match the current setup

### restart_backend.sh
- **Reason**: Redundant functionality - similar to `start_dev.sh` but with restart capability
- **Replaced by**: `start_all.sh restart` or `start_all.sh stop` followed by `start_dev.sh`
- **Issues**: Duplicated logic available in the main script

### stop_all.sh
- **Reason**: Simple wrapper script that only called `start_all.sh stop`
- **Replaced by**: `start_all.sh stop` (direct usage)
- **Issues**: Unnecessary indirection for a single command

### stop_services.sh
- **Reason**: Basic stop functionality without proper error handling or service verification
- **Replaced by**: `start_all.sh stop` (more comprehensive)
- **Issues**: Limited functionality, inconsistent with other scripts

## Current Script Structure

After consolidation, the following scripts remain in the root directory:

- **start_all.sh**: Main comprehensive script with all functionality (start, stop, restart, status, pull-models, help)
- **start_dev.sh**: Backend-only startup (API + Ollama)
- **start_ui.sh**: Frontend-only startup
- **start_all.bat**: Windows batch file with native Windows support and WSL/Git Bash detection

## Migration Guide

If you were using any of the legacy scripts, here are the replacements:

| Old Script | New Command |
|------------|-------------|
| `./start_services.sh` | `./start_all.sh` |
| `./restart_backend.sh` | `./start_all.sh restart` |
| `./stop_all.sh` | `./start_all.sh stop` |
| `./stop_services.sh` | `./start_all.sh stop` |

## Why These Scripts Were Moved

1. **Reduce complexity**: Having multiple scripts with overlapping functionality made maintenance difficult
2. **Improve consistency**: The main script provides consistent error handling and logging
3. **Better user experience**: Single entry point with multiple commands is more intuitive
4. **Eliminate redundancy**: Multiple scripts doing similar things with different approaches
5. **Fix outdated configurations**: Some scripts had hardcoded paths and outdated URLs

## Restoration

If you need to restore any of these scripts for specific use cases, they are preserved here. However, we recommend using the consolidated script structure for better maintainability. 