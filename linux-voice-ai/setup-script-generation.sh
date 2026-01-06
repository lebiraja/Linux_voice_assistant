#!/bin/bash
# Quick setup script for AI Script Generation feature

set -e

echo "🚀 Setting up AI Script Generation for JARVIS..."
echo ""

# 1. Install aichat
echo "📦 Step 1: Installing aichat..."
if command -v aichat &> /dev/null; then
    echo "   ✅ aichat already installed"
else
    ./install-aichat.sh
fi
echo ""

# 2. Configure aichat for Ollama
echo "🔧 Step 2: Configuring aichat to use Ollama..."
mkdir -p ~/.config/aichat

if [ -f ~/.config/aichat/config.yaml ]; then
    echo "   ⚠️  aichat config already exists at ~/.config/aichat/config.yaml"
    echo "   📝 Review config/aichat-config.yaml for recommended settings"
else
    cp config/aichat-config.yaml ~/.config/aichat/config.yaml
    echo "   ✅ Installed aichat config from config/aichat-config.yaml"
fi
echo ""

# 3. Test aichat
echo "🧪 Step 3: Testing aichat..."
if aichat "echo hello" &> /dev/null; then
    echo "   ✅ aichat is working correctly"
else
    echo "   ⚠️  aichat test failed. You may need to configure it:"
    echo "      Run: aichat --setup"
    echo "      Or use Ollama: aichat --model ollama:deepseek-r1:1.5b"
fi
echo ""

# 4. Verify Ollama is running
echo "🤖 Step 4: Checking Ollama..."
if curl -s http://localhost:11434/api/tags &> /dev/null; then
    echo "   ✅ Ollama is running"
    
    # Check if deepseek-r1:1.5b is available
    if ollama list | grep -q "deepseek-r1:1.5b"; then
        echo "   ✅ Model deepseek-r1:1.5b is ready"
    else
        echo "   ⚠️  Model deepseek-r1:1.5b not found"
        echo "   📥 Pulling model (this may take a few minutes)..."
        ollama pull deepseek-r1:1.5b
    fi
else
    echo "   ⚠️  Ollama is not running"
    echo "      Start it with: ollama serve"
fi
echo ""

# 5. Done!
echo "✨ Setup Complete!"
echo ""
echo "📖 Next Steps:"
echo ""
echo "1. Start JARVIS:"
echo "   python3 main.py"
echo ""
echo "2. Try these voice commands:"
echo "   • 'Write a script to list all files larger than 100MB'"
echo "   • 'Create a Python script to organize my Downloads folder'"
echo "   • 'Generate a script to back up my Documents with timestamp'"
echo ""
echo "3. Read the full documentation:"
echo "   cat SCRIPT_GENERATION.md"
echo ""
echo "🎯 Pro Tip: You can also use aichat from command line:"
echo "   aichat 'write a script to monitor disk space'"
echo ""
