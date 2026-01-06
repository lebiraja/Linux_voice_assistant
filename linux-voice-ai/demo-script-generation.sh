#!/bin/bash
# Quick demo of JARVIS Script Generation feature
# Run this to see the feature in action!

echo "🎬 JARVIS Script Generation - Interactive Demo"
echo "================================================"
echo ""
echo "This demo will show you how JARVIS can generate and run scripts."
echo ""

# Check if aichat is installed
if ! command -v aichat &> /dev/null; then
    echo "❌ aichat is not installed yet!"
    echo ""
    echo "Would you like to install it now? (y/n)"
    read -r answer
    if [ "$answer" = "y" ]; then
        ./install-aichat.sh
    else
        echo "Please run ./install-aichat.sh first"
        exit 1
    fi
fi

echo "✅ aichat is installed!"
echo ""

# Demo 1: Simple script generation
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Demo 1: Generate a Hello World script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Command: aichat \"Write a bash script that prints 'Hello from JARVIS!' with current date\""
echo ""
echo "Generating script..."
aichat --no-stream "Write a short bash script that prints 'Hello from JARVIS!' and the current date. Output ONLY the script code, no explanations." > /tmp/demo_script.sh

echo ""
echo "Generated script:"
echo "────────────────────────────────────────────────"
cat /tmp/demo_script.sh
echo "────────────────────────────────────────────────"
echo ""

echo "Press Enter to execute this script..."
read -r

chmod +x /tmp/demo_script.sh
/tmp/demo_script.sh

echo ""
echo "✅ Script executed successfully!"
echo ""

# Demo 2: System info script
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Demo 2: Generate a system info script"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "This will create a script that shows hostname, user, and uptime"
echo ""
echo "Press Enter to continue..."
read -r

aichat --no-stream "Write a bash script that displays: hostname, current user, and system uptime in a nicely formatted way. Output ONLY the script code." > /tmp/demo_sysinfo.sh

echo ""
echo "Generated script:"
echo "────────────────────────────────────────────────"
cat /tmp/demo_sysinfo.sh
echo "────────────────────────────────────────────────"
echo ""

echo "Executing..."
chmod +x /tmp/demo_sysinfo.sh
/tmp/demo_sysinfo.sh

echo ""
echo "✅ Demo complete!"
echo ""

# Summary
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Script Generation Feature Demo Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "What you just saw:"
echo "  1. ✅ AI-generated bash scripts"
echo "  2. ✅ Automatic execution"
echo "  3. ✅ Clean output"
echo ""
echo "Now try with JARVIS voice commands:"
echo ""
echo "  Say: 'Hey JARVIS' (or press Ctrl+Space)"
echo "  Then: 'Write a script to [describe your task]'"
echo ""
echo "Examples:"
echo "  • 'Write a script to back up my Documents folder'"
echo "  • 'Create a Python script to organize Downloads'"
echo "  • 'Generate a script to find files larger than 100MB'"
echo "  • 'Make a script to monitor CPU usage for 1 minute'"
echo ""
echo "📚 Documentation:"
echo "  • Full guide: SCRIPT_GENERATION.md"
echo "  • Quick ref: SCRIPT_GENERATION_QUICK_REF.md"
echo ""
echo "🧪 Run tests:"
echo "  python3 tests/test_script_generation.py"
echo ""
echo "Happy scripting! 🚀"
echo ""

# Cleanup
rm -f /tmp/demo_script.sh /tmp/demo_sysinfo.sh
