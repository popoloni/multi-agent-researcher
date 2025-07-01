#!/bin/bash

# Multi-Agent Research System Setup Script

echo "🤖 Setting up Multi-Agent Research System..."

# Check if Python 3.8+ is installed
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+' | head -1)
if [[ $(echo "$python_version >= 3.8" | bc -l) -eq 0 ]]; then
    echo "❌ Python 3.8 or higher is required. Current version: $python_version"
    exit 1
fi

echo "✅ Python version check passed: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv researcher-venv

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source researcher-venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy environment template
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file and add your API keys"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "⚠️  IMPORTANT: Configure your AI provider in .env file"
echo ""
echo "For Anthropic Claude (recommended):"
echo "1. Get API key from: https://console.anthropic.com/"
echo "2. Edit .env file: ANTHROPIC_API_KEY=your_actual_api_key"
echo "3. Ensure AI_PROVIDER=anthropic"
echo ""
echo "For Ollama (local models):"
echo "1. Install Ollama: https://ollama.com/download"
echo "2. Pull a model: ollama pull llama3.2:1b"
echo "3. Edit .env file: AI_PROVIDER=ollama"
echo ""
echo "Next steps:"
echo "1. Configure .env file with your API keys"
echo "2. Run the server: python run.py"
echo "3. Visit http://localhost:12000/docs for API documentation"
echo ""
echo "📖 See README.md for detailed instructions"