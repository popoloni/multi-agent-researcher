#!/bin/bash
# Wrapper script for backwards compatibility
# Calls the actual cleanup.sh in utils/ folder
exec "$(dirname "$0")/utils/cleanup.sh" "$@" 