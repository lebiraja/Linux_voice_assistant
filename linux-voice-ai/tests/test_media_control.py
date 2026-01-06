#!/usr/bin/env python3
"""
Test script for Media Control feature
Tests the control_media and get_now_playing tools
"""

import sys
import os
import time

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.builtin.media_control import MediaControlTool, GetNowPlayingTool
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def check_playerctl():
    """Check if playerctl is installed"""
    tool = MediaControlTool()
    if not tool._check_playerctl_installed():
        print("❌ playerctl is NOT installed!")
        print("   Please run: ./install-playerctl.sh")
        return False
    print("✅ playerctl is installed")
    return True


def check_players():
    """Check for available media players"""
    print("\n" + "="*60)
    print("Checking for Available Media Players")
    print("="*60)
    
    tool = MediaControlTool()
    result = tool._list_players()
    
    if result["success"] and result["count"] > 0:
        print(f"\n✅ Found {result['count']} player(s):")
        for player in result["players"]:
            print(f"   • {player}")
        return True
    else:
        print("\n⚠️  No media players detected!")
        print("\nTo test media control, start a media player:")
        print("   • Spotify")
        print("   • VLC")
        print("   • Firefox/Chrome with music/video")
        print("   • Any MPRIS-compatible player")
        return False


def test_status():
    """Test getting playback status"""
    print("\n" + "="*60)
    print("TEST 1: Get Playback Status")
    print("="*60)
    
    tool = MediaControlTool()
    result = tool.execute(action="status")
    
    if result["success"]:
        print(f"\n✅ Status: {result['status']}")
        if result.get('available_players'):
            print(f"Available players: {', '.join(result['available_players'])}")
    else:
        print(f"\n❌ Failed: {result.get('error')}")


def test_now_playing():
    """Test getting now playing info"""
    print("\n" + "="*60)
    print("TEST 2: Get Now Playing Info")
    print("="*60)
    
    tool = GetNowPlayingTool()
    result = tool.execute()
    
    if result["success"]:
        print("\n✅ Now Playing:")
        metadata = result.get("metadata", {})
        for key, value in metadata.items():
            if value and value != "":
                print(f"   {key.title()}: {value}")
        print(f"   Status: {result.get('status', 'unknown')}")
        print(f"   Volume: {result.get('volume', 'unknown')}%")
    else:
        print(f"\n❌ Failed: {result.get('error')}")


def test_playback_controls():
    """Test playback controls (interactive)"""
    print("\n" + "="*60)
    print("TEST 3: Playback Controls (Interactive)")
    print("="*60)
    
    print("\nThis test will control your media playback.")
    print("Make sure you have a media player running with content.")
    print("\nPress Enter to continue, or Ctrl+C to skip...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n⏭️  Skipped")
        return
    
    tool = MediaControlTool()
    
    # Test play-pause
    print("\n📝 Test: Toggle play-pause")
    result = tool.execute(action="play-pause")
    if result["success"]:
        print(f"✅ {result['message']} - Status: {result.get('status', 'unknown')}")
    else:
        print(f"❌ {result.get('error')}")
    
    time.sleep(1)
    
    # Test next
    print("\n📝 Test: Next track")
    result = tool.execute(action="next")
    if result["success"]:
        print(f"✅ {result['message']}")
        if result.get('now_playing'):
            print(f"   Now: {result['now_playing'].get('title', 'Unknown')}")
    else:
        print(f"❌ {result.get('error')}")
    
    time.sleep(1)
    
    # Test volume
    print("\n📝 Test: Volume control")
    result = tool.execute(action="volume-up")
    if result["success"]:
        print(f"✅ {result['message']} - Volume: {result.get('volume', '?')}%")
    else:
        print(f"❌ {result.get('error')}")


def test_volume_control():
    """Test volume control"""
    print("\n" + "="*60)
    print("TEST 4: Volume Control")
    print("="*60)
    
    tool = MediaControlTool()
    
    # Get current volume
    print("\n📝 Getting current volume...")
    result = tool._get_volume()
    if result["success"]:
        original_volume = result["volume"]
        print(f"   Current volume: {original_volume}%")
        
        # Set to 50%
        print("\n📝 Setting volume to 50%...")
        result = tool.execute(action="set-volume", value="50")
        if result["success"]:
            print(f"✅ {result['message']}")
        else:
            print(f"❌ {result.get('error')}")
    else:
        print(f"❌ {result.get('error')}")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🎵 Media Control Feature Tests")
    print("="*60)
    
    try:
        # Check prerequisites
        if not check_playerctl():
            return
        
        has_players = check_players()
        
        if not has_players:
            print("\n⚠️  Cannot run tests without media players")
            print("Start a media player and try again!")
            return
        
        # Run tests
        test_status()
        test_now_playing()
        test_playback_controls()
        test_volume_control()
        
        print("\n" + "="*60)
        print("✅ All Tests Completed!")
        print("="*60)
        print("\n🎙️ Now try with JARVIS:")
        print("   Say: 'Hey JARVIS, pause the music'")
        print("   Say: 'Hey JARVIS, next song'")
        print("   Say: 'Hey JARVIS, what's playing?'")
        print("")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
