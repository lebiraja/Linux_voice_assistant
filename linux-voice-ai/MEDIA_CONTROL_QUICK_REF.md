# 🎵 JARVIS Media Control - Quick Reference

## Installation

```bash
./install-playerctl.sh
```

## Voice Commands

### Playback Control
```
✓ "Play music"
✓ "Pause"
✓ "Stop"
✓ "Resume"
✓ "Play pause" (toggle)
```

### Track Navigation
```
✓ "Next song"
✓ "Skip track"
✓ "Previous song"
✓ "Go back"
```

### Volume Control
```
✓ "Volume up"
✓ "Volume down"
✓ "Set volume to 50"
✓ "Mute"
✓ "Unmute"
```

### Media Info
```
✓ "What's playing?"
✓ "What song is this?"
✓ "Tell me the track"
```

### Seek Controls
```
✓ "Seek forward 30 seconds"
✓ "Go back 10 seconds"
```

## Supported Players

✅ Spotify
✅ VLC
✅ Rhythmbox
✅ Firefox/Chrome (web players)
✅ YouTube
✅ Any MPRIS-compatible player

## Quick Test

```bash
# Check available players
playerctl -l

# Test playback
playerctl play-pause

# Get now playing
playerctl metadata

# Test with Python
python3 tests/test_media_control.py
```

## Common Actions

| Command | Action |
|---------|--------|
| Play | `control_media(action="play")` |
| Pause | `control_media(action="pause")` |
| Next | `control_media(action="next")` |
| Previous | `control_media(action="previous")` |
| Volume +10% | `control_media(action="volume-up")` |
| Volume -10% | `control_media(action="volume-down")` |
| Set Volume | `control_media(action="set-volume", value="75")` |
| Now Playing | `get_now_playing()` |

## Troubleshooting

### No players detected
```bash
# Start a media player (Spotify, VLC, browser with music)
# Then check:
playerctl -l
```

### playerctl not found
```bash
./install-playerctl.sh
```

### Can't control player
```bash
# Check if player supports MPRIS:
playerctl -l

# If listed, try:
playerctl -p spotify play-pause
```

## Examples

### Example 1: Basic Control
```
User: "Hey JARVIS, pause the music"
JARVIS: *pauses playback* "Playback paused"
```

### Example 2: Track Info
```
User: "Hey JARVIS, what's playing?"
JARVIS: "Now playing: Song Name by Artist from Album"
```

### Example 3: Volume
```
User: "Hey JARVIS, set volume to 75"
JARVIS: "Volume set to 75%"
```

### Example 4: Navigation
```
User: "Hey JARVIS, next song"
JARVIS: "Skipped to next track: New Song by Artist"
```

## Full Documentation

See [MEDIA_CONTROL.md](MEDIA_CONTROL.md) for complete guide.

---

**Enjoy hands-free media control! 🎵**
