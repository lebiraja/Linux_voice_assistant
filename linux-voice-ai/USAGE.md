# Linux Voice AI Assistant - Usage Guide

## Quick Start

### Option 1: Using the Start Script (Recommended)

```bash
cd /home/lebi/projects/VFL/linux-voice-ai
./start.sh
```

This script will:
- Check for Docker and Docker Compose
- Allow X11 connections for hotkey support
- Build and start the assistant
- Clean up on exit

### Option 2: Manual Docker Commands

```bash
cd /home/lebi/projects/VFL/linux-voice-ai

# Allow X11 connections
xhost +local:docker

# Build and run
docker-compose up --build

# In another terminal, to stop:
docker-compose down

# Clean up X11 permissions
xhost -local:docker
```

---

## Using the Assistant

1. **Wait for startup**: The assistant will load models (takes ~30 seconds first time)

2. **Look for this message**:
   ```
   🎙️  Linux Voice AI Assistant v0
   ============================================================
   Press CTRL+SPACE to speak
   Press Ctrl+C to exit
   ```

3. **Press Ctrl+Space** to activate voice input

4. **Speak your command** within 5 seconds:
   - "Open Firefox"
   - "Close Firefox"  
   - "What's my CPU usage?"
   - "How much RAM do I have?"
   - "What's my disk space?"

5. **Listen to the response** - the assistant will speak back to you

---

## Example Session

```
🎙️  Linux Voice AI Assistant v0
============================================================
Press CTRL+SPACE to speak
Press Ctrl+C to exit

[You press Ctrl+Space]

🎤 Listening...
🔄 Transcribing...
📝 You said: "open firefox"
⚙️  Executing: open_app - firefox
💬 Response: Firefox is now open.
🔊 Speaking...

[Firefox opens, assistant speaks the response]
```

---

## Supported Commands

### Application Control

| Command | Action |
|---------|--------|
| "Open Firefox" | Launches Firefox browser |
| "Launch Chrome" | Launches Chrome/Chromium |
| "Start Terminal" | Opens terminal emulator |
| "Open VS Code" | Launches Visual Studio Code |
| "Open Files" | Opens file manager |
| "Close [app name]" | Closes the specified app |

### System Information

| Command | Response |
|---------|----------|
| "What's my CPU usage?" | Reports current CPU percentage |
| "How much RAM do I have?" | Reports total and available RAM |
| "What's my disk space?" | Reports disk usage percentage |

---

## Customization

### Change Hotkey

Edit `config/config.yaml`:

```yaml
hotkey:
  combination: "ctrl+alt+space"  # Change to your preference
```

### Add New Applications

Edit `config/commands.yaml`:

```yaml
applications:
  spotify:
    executables:
      - "spotify"
    synonyms:
      - "music"
      - "spotify"
```

### Adjust Recording Duration

Edit `config/config.yaml`:

```yaml
audio:
  max_recording_seconds: 10  # Increase for longer commands
```

### Change TTS Voice

Edit `config/config.yaml`:

```yaml
tts:
  model_name: "en_US-amy-medium"  # Different voice
```

Available voices: https://github.com/rhasspy/piper/blob/master/VOICES.md

---

## Troubleshooting

### Hotkey Not Working

**Problem**: Pressing Ctrl+Space does nothing

**Solutions**:
1. Check X11 permissions: `xhost +local:docker`
2. Verify DISPLAY variable: `echo $DISPLAY`
3. Check Docker logs: `docker-compose logs -f`

### No Audio Input

**Problem**: "No audio recorded" error

**Solutions**:
1. Check microphone permissions
2. Verify PulseAudio is running: `pulseaudio --check`
3. Test microphone: `arecord -d 5 test.wav`
4. Check PulseAudio socket path in `docker-compose.yml`

### No Audio Output

**Problem**: No voice response heard

**Solutions**:
1. Check speaker volume
2. Verify audio device: `aplay -l`
3. Test playback: `speaker-test -t wav -c 2`
4. Check PulseAudio connection in Docker

### Piper TTS Not Found

**Problem**: "Piper TTS not found" error

**Solutions**:
1. Rebuild Docker image: `docker-compose build --no-cache`
2. Check Piper installation in container: `docker-compose exec voice-assistant which piper`

### Whisper Model Download Fails

**Problem**: STT initialization fails

**Solutions**:
1. Check internet connection
2. Manually download model: The Dockerfile pre-downloads it
3. Check disk space

### Application Not Opening

**Problem**: "I couldn't find [app]" error

**Solutions**:
1. Check if app is installed: `which firefox`
2. Add executable to `config/commands.yaml`
3. Check Docker has access to X11: `xhost +local:docker`

---

## Performance Tips

### Faster Startup

- Use smaller Whisper model (already using `tiny`)
- Pre-build Docker image: `./build.sh`

### Better Accuracy

- Speak clearly and at normal pace
- Reduce background noise
- Use a good quality microphone

### Lower Latency

- Use CPU with AVX2 support for Whisper
- Reduce recording duration to 3 seconds
- Use smaller TTS model

---

## Development Mode

### Run Without Docker

```bash
# Install dependencies
pip install -r requirements.txt

# Install Piper TTS separately
# See: https://github.com/rhasspy/piper

# Run
python main.py
```

### View Logs

```bash
# Real-time logs
docker-compose logs -f

# Application logs
tail -f logs/lva.log
```

### Debug Mode

Edit `config/config.yaml`:

```yaml
logging:
  level: "DEBUG"  # More verbose logging
```

---

## Stopping the Assistant

### Graceful Shutdown

Press `Ctrl+C` in the terminal running the assistant

### Force Stop

```bash
docker-compose down
```

### Remove Everything

```bash
docker-compose down -v  # Removes volumes too
```

---

## Next Steps

1. **Test all commands** to verify functionality
2. **Customize commands** for your workflow
3. **Add new applications** you frequently use
4. **Experiment with voices** to find your favorite
5. **Provide feedback** for improvements

---

## Getting Help

- Check logs: `docker-compose logs -f`
- Enable debug logging in `config/config.yaml`
- Review the [README.md](file:///home/lebi/projects/VFL/linux-voice-ai/README.md)
- Check the [architecture document](file:///home/lebi/projects/VFL/linux_voice_ai_assistant_architecture_implementation_report.md)
