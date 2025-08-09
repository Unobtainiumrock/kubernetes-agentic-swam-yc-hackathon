#!/bin/bash

# MorphLLM Integration Setup Script
# This script helps you set up the MorphLLM integration for your Kubernetes agentic system

set -e

echo "🚀 Setting up MorphLLM Integration for Kubernetes Agentic System"
echo "================================================================"
echo

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo
    echo "⚠️  IMPORTANT: Please edit the .env file and add your MorphLLM API key:"
    echo "   MORPH_API_KEY=your_actual_api_key_here"
    echo
    echo "📖 To get a MorphLLM API key:"
    echo "   1. Visit https://morphllm.com"
    echo "   2. Sign up for an account"
    echo "   3. Generate an API key"
    echo "   4. Add it to the .env file"
    echo
else
    echo "✅ .env file already exists"
    
    # Check if API key is set
    if grep -q "your_morph_api_key_here" .env; then
        echo "⚠️  Please update your MORPH_API_KEY in the .env file"
    else
        echo "✅ API key appears to be configured"
    fi
fi

# Check if python3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ python3 is required but not installed"
    echo "Please install Python 3.8+ to continue"
    exit 1
else
    echo "✅ python3 found: $(python3 --version)"
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed"
    echo "Please install pip to continue"
    exit 1
else
    echo "✅ pip3 found"
fi

# Install requirements
echo
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

echo
echo "🧪 Testing configuration..."
python3 -c "
from config import morph_config
print('✅ Configuration loaded successfully')
if morph_config.api_key and morph_config.api_key != 'your_morph_api_key_here':
    print('✅ API key is configured')
else:
    print('⚠️  API key needs to be set in .env file')
"

echo
echo "🎯 Setup complete! Next steps:"
echo "1. If you haven't already, add your MorphLLM API key to .env"
echo "2. Start your Kubernetes cluster: cd .. && ./setup-cluster.sh"
echo "3. Deploy demo apps: ./deploy-demo-apps.sh"
echo "4. Test the MorphLLM agent: python3 example_usage.py"
echo
echo "📚 Documentation:"
echo "   • MorphLLM docs: https://docs.morphllm.com/guides/agent-tools"
echo "   • README.md: Overview of the integration"
echo "   • example_usage.py: Demonstration of capabilities"
