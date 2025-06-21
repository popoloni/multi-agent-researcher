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
echo "Next steps:"
echo "1. Edit .env file and add your Anthropic API key"
echo "2. Run the server: python run.py"
echo "3. Visit http://localhost:12000/docs for API documentation"
echo "4. Test with: python test_client.py"
echo ""
echo "For demo without API key: python demo_with_api_key.py"
echo ""
echo "📖 See README.md for detailed instructions"