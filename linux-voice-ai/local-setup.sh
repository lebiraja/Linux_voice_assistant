#!/bin/bash
# Local Setup Script - Run Everything Locally

set -e

echo "=========================================="
echo "Linux Voice AI - Local Setup"
echo "=========================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment exists"
fi

# Activate venv
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
echo "✅ Dependencies installed"

# Check Ollama
echo ""
echo "🔍 Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Ollama not found"
    echo ""
    echo "   Install Ollama:"
    echo "   curl -fsSL https://ollama.com/install.sh | sh"
    echo ""
    exit 1
fi

echo "✅ Ollama found: $(ollama --version)"

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running"
    echo ""
    echo "   Starting Ollama..."
    ollama serve > /dev/null 2>&1 &
    sleep 3
    
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo "✅ Ollama started"
    else
        echo "❌ Failed to start Ollama"
        echo "   Try manually: ollama serve"
        exit 1
    fi
else
    echo "✅ Ollama is running"
fi

# Check model
echo ""
echo "🔍 Checking for functiongemma:270m model..."
if ollama list | grep -q "functiongemma:270m"; then
    echo "✅ Model found"
else
    echo "📥 Pulling functiongemma:270m (this may take a few minutes)..."
    ollama pull functiongemma:270m
    echo "✅ Model downloaded"
fi

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "🎙️  To start the voice assistant:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "📚 See LOCAL_SETUP.md for detailed documentation"
echo ""
