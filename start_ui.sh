#!/bin/bash

# Multi-Agent Researcher UI Startup Script
echo "🚀 Starting Multi-Agent Researcher UI..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

# Navigate to frontend directory
cd frontend

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Build the frontend for production
echo "🔨 Building frontend for production..."
npm run build

# Go back to root directory
cd ..

# Start the FastAPI server
echo "🌐 Starting FastAPI server with UI..."
python -m uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

echo "✅ Multi-Agent Researcher UI is now running at http://localhost:8080"