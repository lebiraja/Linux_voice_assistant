# Linux Voice AI Assistant

A voice-first AI assistant for Linux that can control applications and query system information through natural speech.

## Features

- 🎤 **Voice Input**: Push-to-talk with global hotkey (Ctrl+Space)
- 🗣️ **Speech Recognition**: Local Whisper (tiny model) for fast, offline STT
- 🤖 **Command Understanding**: Rule-based parser with fuzzy matching
- 🚀 **Application Control**: Open and close applications
- 📊 **System Queries**: Get CPU, RAM, and disk usage
- 🔊 **Voice Output**: Natural speech with Piper TTS
- 🐳 **Docker Support**: Fully containerized with docker-compose

## Quick Start with Docker (Recommended)

### Prerequisites

- Docker and Docker Compose installed
- PulseAudio running (for audio)
- X11 display server (for hotkey support)

### One-Command Setup

```bash
# Automated setup (starts Ollama + Voice Assistant)
./docker-setup.sh
```

### Manual Setup

```bash
# Allow X11 connections
xhost +local:docker

# Build and start services
docker-compose up -d

# Pull LLM model
docker exec ollama ollama pull functiongemma:270m

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed Docker documentation.**

## Local Development

### Prerequisites

- Python 3.11+
- PortAudio
- FFmpeg
- Piper TTS

### Installation

```bash
# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y portaudio19-dev libsndfile1 ffmpeg

# Install Piper TTS
# Follow instructions at: https://github.com/rhasspy/piper

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

## Usage

1. **Start the assistant** (via Docker or locally)
2. **Press Ctrl+Space** to activate voice input
3. **Speak your command** (you have 5 seconds)
4. **Listen to the response**

### Example Commands

- "Open Firefox"
- "Close Firefox"
- "What's my CPU usage?"
- "How much RAM do I have?"
- "What's my disk space?"

## Project Structure

```
linux-voice-ai/
├── audio/              # Audio recording and playback
├── stt/                # Speech-to-text (Whisper)
├── parser/             # Command parsing
├── actions/            # Action executors (apps, system)
├── tts/                # Text-to-speech (Piper)
├── utils/              # Utilities (logging, responses)
├── config/             # Configuration files
├── logs/               # Log files (generated)
├── temp/               # Temporary audio files (generated)
├── models/             # Model cache (generated)
├── main.py             # Main application
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker image definition
└── docker-compose.yml  # Docker Compose configuration
```

## Configuration

Edit `config/config.yaml` to customize:

- Audio settings (sample rate, recording duration)
- STT model (Whisper model size)
- TTS voice (Piper voice model)
- Hotkey combination
- Logging level

Edit `config/commands.yaml` to:

- Add new intents and keywords
- Map application names to executables
- Customize response templates

## Troubleshooting

### Audio Issues

- **No audio recorded**: Check microphone permissions and PulseAudio
- **No audio playback**: Verify speaker output and volume

### Docker Issues

- **Hotkey not working**: Ensure X11 socket is mounted correctly
- **Audio not working**: Check PulseAudio socket path (`/run/user/1000/pulse`)

### TTS Issues

- **Piper not found**: Install Piper TTS or check PATH
- **Voice quality**: Try different voice models in config

## Roadmap

See the [architecture document](../linux_voice_ai_assistant_architecture_implementation_report.md) for the full vision.

### v0 (Current)
- ✅ Voice input with hotkey
- ✅ Whisper STT
- ✅ Rule-based command parsing
- ✅ App control (open/close)
- ✅ System info queries
- ✅ Piper TTS
- ✅ Docker support

### v1 (Future)
- LLM-based intent parsing
- Context awareness
- Error handling improvements

### v2+ (Future)
- Multi-step task planning
- Deep OS integration (D-Bus)
- Long-term memory
- Background monitoring

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please open an issue or PR.
