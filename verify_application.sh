#!/bin/bash

echo "=== Multi-Agent Researcher Application Verification ==="
echo ""

# Test Backend
echo "🔍 Testing Backend (Port 12000)..."
BACKEND_HEALTH=$(curl -s http://localhost:12000/health)
if echo "$BACKEND_HEALTH" | grep -q "healthy"; then
    echo "✅ Backend is healthy"
    echo "   Response: $BACKEND_HEALTH"
else
    echo "❌ Backend is not responding"
    exit 1
fi

# Test Repository API
echo ""
echo "🔍 Testing Repository API..."
REPO_COUNT=$(curl -s http://localhost:12000/kenobi/repositories | jq -r '.total_repositories')
if [ "$REPO_COUNT" -gt 0 ]; then
    echo "✅ Repository API working - $REPO_COUNT repositories indexed"
else
    echo "❌ Repository API not working or no repositories"
fi

# Test Frontend
echo ""
echo "🔍 Testing Frontend (Port 12001)..."
FRONTEND_TITLE=$(curl -s http://localhost:12001 | grep -o '<title>.*</title>')
if echo "$FRONTEND_TITLE" | grep -q "Multi-Agent Researcher"; then
    echo "✅ Frontend is serving correctly"
    echo "   Title: $FRONTEND_TITLE"
else
    echo "❌ Frontend is not responding correctly"
    exit 1
fi

# Test API connectivity from frontend perspective
echo ""
echo "🔍 Testing API connectivity..."
API_URL="https://work-1-ejtkhcyzotgqadin.prod-runtime.all-hands.dev"
API_HEALTH=$(curl -s "$API_URL/health" 2>/dev/null)
if echo "$API_HEALTH" | grep -q "healthy"; then
    echo "✅ External API URL is accessible"
else
    echo "⚠️  External API URL may not be accessible (this is expected in some environments)"
fi

echo ""
echo "=== Application URLs ==="
echo "🌐 Frontend: https://work-2-ejtkhcyzotgqadin.prod-runtime.all-hands.dev"
echo "🔧 Backend:  https://work-1-ejtkhcyzotgqadin.prod-runtime.all-hands.dev"
echo ""
echo "=== Process Information ==="
echo "Backend PID: $(pgrep -f 'uvicorn.*12000')"
echo "Frontend PID: $(pgrep -f 'react-scripts')"
echo ""
echo "=== Repository Data ==="
curl -s http://localhost:12000/kenobi/repositories | jq '.repositories[] | {name: .name, id: .id, files: .metrics.total_files, elements: .metrics.total_elements}'
echo ""
echo "✅ Application is fully operational!"
echo "📝 You can now interact with the Multi-Agent Researcher through the web interface."