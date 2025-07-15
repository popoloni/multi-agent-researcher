#!/bin/bash
# Wrapper script for backwards compatibility
# Calls the actual start_all.sh in utils/ folder
exec "$(dirname "$0")/utils/start_all.sh" "$@" 