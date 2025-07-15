#!/bin/bash
# Wrapper script for backwards compatibility
# Calls the actual verify_application.sh in utils/ folder
exec "$(dirname "$0")/utils/verify_application.sh" "$@" 