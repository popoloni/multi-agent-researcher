#!/bin/bash
echo "🚀 Starting Multi-Agent Researcher Frontend..."

# Change to project root directory first
cd "$(dirname "$0")/.."

# Navigate to frontend directory
cd frontend

# Check if package.json has correct proxy setting
if ! grep -q '"proxy": "http://localhost:12000"' package.json; then
    echo "📝 Updating API proxy configuration..."
    sed -i 's|"proxy": "http://localhost:[0-9]*"|"proxy": "http://localhost:12000"|g' package.json
fi

# Check if node_modules exists and install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
    
    # Install MUI dependencies that might be missing
    echo "📦 Installing additional UI dependencies..."
    npm install @mui/material @mui/icons-material @emotion/react @emotion/styled
fi

# Start development server
echo "🔄 Starting React development server on port 12001..."
# Kill any existing processes on port 12001
fuser -k 12001/tcp 2>/dev/null || true
# Set environment variables to allow external access
export HOST=0.0.0.0
export PORT=12001
export DANGEROUSLY_DISABLE_HOST_CHECK=true
npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo "✅ Frontend started successfully with PID: $FRONTEND_PID"
echo "📊 Status:"
echo "  - Frontend: Running on port 12001"
echo "  - Frontend URL: http://localhost:12001"
echo "  - Logs: frontend.log"
echo ""
echo "💡 To stop frontend: kill $FRONTEND_PID"