#!/bin/bash
# Installation script for playerctl - media player controller

set -e

echo "🎵 Installing playerctl for media control..."

# Check if playerctl is already installed
if command -v playerctl &> /dev/null; then
    echo "✅ playerctl is already installed"
    playerctl --version
    exit 0
fi

# Detect Linux distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Cannot detect Linux distribution"
    exit 1
fi

echo "📦 Detected OS: $OS"

# Install based on distribution
case $OS in
    ubuntu|debian|linuxmint|pop)
        echo "Installing via apt..."
        sudo apt update
        sudo apt install -y playerctl
        ;;
    fedora)
        echo "Installing via dnf..."
        sudo dnf install -y playerctl
        ;;
    arch|manjaro)
        echo "Installing via pacman..."
        sudo pacman -S --noconfirm playerctl
        ;;
    opensuse*)
        echo "Installing via zypper..."
        sudo zypper install -y playerctl
        ;;
    *)
        echo "⚠️  Unsupported distribution: $OS"
        echo "Please install playerctl manually:"
        echo "  https://github.com/altdesktop/playerctl"
        exit 1
        ;;
esac

# Verify installation
if command -v playerctl &> /dev/null; then
    echo "✅ playerctl successfully installed!"
    playerctl --version
    
    echo ""
    echo "📝 playerctl is now ready!"
    echo ""
    echo "🎮 Media control capabilities:"
    echo "   • Play/Pause/Stop media"
    echo "   • Next/Previous track"
    echo "   • Volume control"
    echo "   • Seek forward/backward"
    echo "   • Get now playing info"
    echo ""
    echo "🎯 Works with:"
    echo "   • Spotify"
    echo "   • VLC"
    echo "   • Firefox/Chrome (web players)"
    echo "   • Rhythmbox, Audacious, and more!"
    echo ""
    echo "🧪 Test it:"
    echo "   playerctl status          # Check playback status"
    echo "   playerctl play-pause      # Toggle playback"
    echo "   playerctl next            # Next track"
    echo "   playerctl metadata        # Show track info"
    echo ""
    echo "🎙️ Now try with JARVIS:"
    echo "   'Hey JARVIS, pause the music'"
    echo "   'Hey JARVIS, play next song'"
    echo "   'Hey JARVIS, what's playing?'"
else
    echo "❌ Installation failed. Please install manually:"
    echo "   https://github.com/altdesktop/playerctl"
    exit 1
fi
