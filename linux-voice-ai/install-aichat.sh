#!/bin/bash
# Installation script for aichat CLI

set -e

echo "🤖 Installing aichat CLI for AI-powered script generation..."

# Check if aichat is already installed
if command -v aichat &> /dev/null; then
    echo "✅ aichat is already installed"
    aichat --version
    exit 0
fi

# Install aichat
echo "📦 Downloading and installing aichat..."
curl -fsSL https://raw.githubusercontent.com/sigoden/aichat/main/scripts/install.sh | bash

# Verify installation
if command -v aichat &> /dev/null; then
    echo "✅ aichat successfully installed!"
    aichat --version
    
    echo ""
    echo "📝 Configuration Notes:"
    echo "   - aichat supports multiple AI providers (OpenAI, Claude, Ollama, etc.)"
    echo "   - To configure, run: aichat --setup"
    echo "   - Or create ~/.config/aichat/config.yaml manually"
    echo ""
    echo "🔧 For local AI with Ollama (recommended):"
    echo "   aichat --model ollama:deepseek-r1:1.5b"
    echo ""
    echo "📖 More info: https://github.com/sigoden/aichat"
else
    echo "❌ Installation failed. Please install manually:"
    echo "   curl -fsSL https://raw.githubusercontent.com/sigoden/aichat/main/scripts/install.sh | bash"
    exit 1
fi
