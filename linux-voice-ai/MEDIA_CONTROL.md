# 🎵 JARVIS Media Control Feature

## 🌟 Overview

JARVIS now has **full media playback control**! Control your music and videos using voice commands - play, pause, skip tracks, adjust volume, and more. Works with Spotify, VLC, browsers, and most media players on Linux.

## ✨ Features

- **🎮 Playback Control**: Play, pause, stop, play-pause toggle
- **⏭️ Track Navigation**: Next track, previous track
- **🔊 Volume Management**: Increase, decrease, set specific volume, mute/unmute
- **⏩ Seek Controls**: Skip forward/backward in tracks
- **📊 Media Info**: Get currently playing track, artist, album
- **🎯 Multi-Player**: Control specific players (Spotify, VLC, etc.)
- **🔌 MPRIS Integration**: Works with any MPRIS-compatible media player

## 📦 Installation

### Quick Install

```bash
cd linux-voice-ai
./install-playerctl.sh
```

This will automatically install `playerctl` for your Linux distribution.

### Manual Installation

**Ubuntu/Debian:**
```bash
sudo apt install playerctl
```

**Fedora:**
```bash
sudo dnf install playerctl
```

**Arch Linux:**
```bash
sudo pacman -S playerctl
```

### Verify Installation

```bash
playerctl --version
```

## 🎙️ Voice Commands

### Playback Control

```
✓ "Play music"
✓ "Pause"
✓ "Stop the music"
✓ "Resume playback"
✓ "Play pause" (toggle)
```

### Track Navigation

```
✓ "Next song"
✓ "Skip this track"
✓ "Play next"
✓ "Previous song"
✓ "Go back"
✓ "Play previous track"
```

### Volume Control

```
✓ "Volume up"
✓ "Increase volume"
✓ "Volume down"
✓ "Decrease volume"
✓ "Set volume to 50"
✓ "Mute"
✓ "Unmute"
```

### Media Information

```
✓ "What's playing?"
✓ "What song is this?"
✓ "Tell me the current track"
✓ "Show now playing"
✓ "What am I listening to?"
```

### Advanced Controls

```
✓ "Seek forward 30 seconds"
✓ "Go back 10 seconds"
✓ "Check media status"
```

## 🎯 Supported Media Players

Works with any MPRIS-compatible player:

### Music Players
- **Spotify** ✅
- **VLC** ✅
- **Rhythmbox** ✅
- **Audacious** ✅
- **Clementine** ✅
- **Strawberry** ✅
- **DeaDBeeF** ✅

### Video Players
- **VLC** ✅
- **MPV** ✅
- **Celluloid** ✅

### Web Players
- **YouTube (in browser)** ✅
- **Spotify Web Player** ✅
- **SoundCloud** ✅
- **Any web player in Firefox/Chrome** ✅

### Others
- **Chromium** ✅
- **Firefox** ✅
- And many more!

## 🔧 Tool Details

### `control_media`

The main media control tool with comprehensive functionality.

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | string | Yes | Action to perform |
| `value` | string | No | Value for actions like set-volume |
| `player` | string | No | Specific player to control |

**Actions:**

| Action | Description | Example |
|--------|-------------|---------|
| `play` | Start playback | "Play music" |
| `pause` | Pause playback | "Pause" |
| `play-pause` | Toggle play/pause | "Play pause" |
| `stop` | Stop playback | "Stop music" |
| `next` | Next track | "Next song" |
| `previous` | Previous track | "Previous song" |
| `volume-up` | Increase volume 10% | "Volume up" |
| `volume-down` | Decrease volume 10% | "Volume down" |
| `set-volume` | Set specific volume (0-100) | "Set volume to 50" |
| `mute` | Mute audio | "Mute" |
| `unmute` | Unmute to 50% | "Unmute" |
| `seek-forward` | Skip forward (default 10s) | "Seek forward" |
| `seek-backward` | Skip backward (default 10s) | "Seek backward" |
| `status` | Get playback status | "Check status" |
| `info` | Get full media info | "What's playing?" |

### `get_now_playing`

Get information about currently playing media.

**Returns:**
- Track title
- Artist name
- Album name
- Playback position/duration
- Playback status
- Current volume

## 📚 Usage Examples

### Example 1: Basic Playback

**You say:** "Hey JARVIS, play music"

**JARVIS does:**
1. Calls `control_media(action="play")`
2. Starts playback on active player
3. Responds: "Playback started"

### Example 2: Skip Track

**You say:** "Hey JARVIS, next song"

**JARVIS does:**
1. Calls `control_media(action="next")`
2. Skips to next track
3. Reads out: "Skipped to next track: Song Name by Artist"

### Example 3: Volume Control

**You say:** "Hey JARVIS, set volume to 75"

**JARVIS does:**
1. Calls `control_media(action="set-volume", value="75")`
2. Sets volume to 75%
3. Responds: "Volume set to 75%"

### Example 4: Get Track Info

**You say:** "Hey JARVIS, what's playing?"

**JARVIS does:**
1. Calls `get_now_playing()`
2. Retrieves metadata
3. Responds: "Now playing: Song Name by Artist from Album"

### Example 5: Control Specific Player

**You say:** "Hey JARVIS, pause Spotify"

**JARVIS does:**
1. Calls `control_media(action="pause", player="spotify")`
2. Pauses Spotify specifically
3. Responds: "Spotify paused"

## 🎨 How It Works

```
Voice Input
    ↓
Speech Recognition (Whisper)
    ↓
LLM Processing (Ollama)
    ↓
Tool Selection: control_media
    ↓
playerctl Command (MPRIS D-Bus)
    ↓
Media Player Action
    ↓
Voice Response (TTS)
```

### MPRIS Protocol

JARVIS uses the **MPRIS (Media Player Remote Interfacing Specification)** D-Bus interface, which is the standard for media player control on Linux. This ensures compatibility with virtually all modern media players.

## 🧪 Testing

### Test via Command Line

```bash
# Check available players
playerctl -l

# Check status
playerctl status

# Get metadata
playerctl metadata

# Control playback
playerctl play-pause
playerctl next
playerctl previous

# Volume
playerctl volume 0.5  # 50%
```

### Test with Python

```bash
cd linux-voice-ai
python3 -c "
from tools.builtin.media_control import MediaControlTool

tool = MediaControlTool()

# Play
print(tool.execute(action='play'))

# Get info
print(tool.execute(action='info'))
"
```

### Comprehensive Test Suite

Create `tests/test_media_control.py`:

```python
from tools.builtin.media_control import MediaControlTool

tool = MediaControlTool()

# Test play
result = tool.execute(action="play")
print(f"Play: {result}")

# Test info
result = tool.execute(action="info")
print(f"Now playing: {result}")

# Test next
result = tool.execute(action="next")
print(f"Next: {result}")
```

## 🔍 Troubleshooting

### playerctl not found

```bash
./install-playerctl.sh
```

### No player detected

Make sure a media player is running:
```bash
playerctl -l  # List available players
```

If no players are listed, start one (Spotify, VLC, etc.) and try again.

### Can't control specific player

List players and use exact name:
```bash
playerctl -l
# Output: spotify, vlc, firefox

# Then use in voice command:
"Control spotify: pause"
```

### Permission issues

Ensure you're in the required groups:
```bash
groups
# Should include: audio
```

If not:
```bash
sudo usermod -aG audio $USER
# Log out and back in
```

## 🎯 Common Use Cases

### Music Control

```
"Play music"
"Pause"
"Next song"
"Previous track"
"Volume up"
"What's playing?"
```

### Spotify Control

```
"Play Spotify"
"Pause Spotify"
"Skip this song"
"Volume to 80"
```

### YouTube Control (in browser)

```
"Pause the video"
"Play"
"Skip forward 30 seconds"
```

### VLC Control

```
"Play VLC"
"Stop VLC"
"Volume down"
```

## 🚀 Advanced Features

### Multi-Player Scenarios

If you have multiple players running:

```
"Pause Spotify"          # Controls only Spotify
"Play VLC"               # Controls only VLC
"Next song in Firefox"   # Controls Firefox player
```

### Volume Precision

```
"Set volume to 25"       # 25%
"Set volume to 100"      # Max volume
"Set volume to 0"        # Mute
```

### Seeking

```
"Seek forward 30 seconds"
"Go back 15 seconds"
"Skip ahead 1 minute"
```

## 📊 Response Examples

### Successful Play
```json
{
  "success": true,
  "message": "Playback started",
  "action": "play"
}
```

### Track Skip with Info
```json
{
  "success": true,
  "message": "Skipped to next track",
  "action": "next",
  "now_playing": {
    "title": "Song Name",
    "artist": "Artist Name",
    "album": "Album Name"
  }
}
```

### Volume Change
```json
{
  "success": true,
  "message": "Volume set to 75%",
  "action": "set-volume",
  "volume": 75
}
```

### Now Playing Info
```json
{
  "success": true,
  "metadata": {
    "title": "Song Name",
    "artist": "Artist Name",
    "album": "Album Name",
    "duration": "2:34 / 4:12"
  },
  "status": "Playing",
  "volume": 65
}
```

## 🎓 Tips & Tricks

1. **Natural Commands**: JARVIS understands variations
   - "Next song" = "Skip track" = "Play next"
   - "Pause" = "Stop music" = "Pause playback"

2. **Quick Toggle**: Use "play pause" to toggle
   - If playing → pauses
   - If paused → plays

3. **Multiple Players**: Be specific when needed
   - "Pause" → controls active player
   - "Pause Spotify" → controls Spotify only

4. **Volume Control**: Quick adjustments
   - "Volume up" → +10%
   - "Volume down" → -10%
   - Can be repeated

5. **Track Info**: Get details anytime
   - "What's playing?" → full track info
   - Works even when paused

## 🔐 Privacy & Security

- **Local Control**: All media control is local (no cloud)
- **D-Bus Interface**: Standard Linux IPC mechanism
- **No Data Collection**: No tracking of what you listen to
- **Safe Operations**: Can't delete or modify files

## 📝 Configuration

Media control works out of the box with default settings. Optional configuration in `config/config.yaml`:

```yaml
media:
  default_player: null  # Auto-detect, or specify: "spotify", "vlc", etc.
  volume_step: 10       # Volume change amount (%)
  seek_amount: 10       # Seek time in seconds
```

## 🚧 Limitations

- **MPRIS Required**: Players must support MPRIS (most modern ones do)
- **Player Must Be Running**: Can't start a closed player (use open_app for that)
- **Local Only**: Can't control remote/network players
- **Single Active Player**: Some commands default to currently active player

## 🎯 Future Enhancements

Planned improvements:

- [ ] Playlist management
- [ ] Search and play specific songs
- [ ] Queue management
- [ ] Lyrics display
- [ ] Radio station control
- [ ] Smart playlists
- [ ] Integration with music streaming APIs

## 📚 Resources

- [playerctl GitHub](https://github.com/altdesktop/playerctl)
- [MPRIS Specification](https://specifications.freedesktop.org/mpris-spec/latest/)
- [D-Bus Documentation](https://www.freedesktop.org/wiki/Software/dbus/)

## 🤝 Contributing

Ideas for better media control? Open an issue or PR!

## 📄 License

Same as parent project (MIT)

---

**Enjoy hands-free media control with JARVIS! 🎵**
