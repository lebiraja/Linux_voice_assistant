#!/bin/bash
# One-time setup for X11 permissions
# Run this once after system boot or when X11 permissions are reset

echo "🔓 Setting up X11 permissions for Docker..."
xhost +local:docker

echo "✅ X11 permissions configured!"
echo ""
echo "You can now run the voice assistant with:"
echo "  docker compose up"
echo ""
echo "Note: These permissions persist until you log out or reboot."
echo "If you reboot, run this script again before using docker compose up."
