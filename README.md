# Linux Voice AI Assistant (JARVIS)

<div align="center">

**A powerful, intelligent voice assistant for Linux with hands-free wake word detection, advanced LLM integration, and comprehensive system control capabilities.**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-supported-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

</div>

---

## 🌟 Overview

Linux Voice AI Assistant (JARVIS) is a sophisticated, voice-controlled AI assistant designed specifically for Linux systems. It combines cutting-edge speech recognition, natural language understanding with LLM integration, and powerful tool-calling capabilities to provide an intelligent, hands-free computing experience.

### Key Highlights

- 🎙️ **Dual Activation Modes**: Hotkey (Ctrl+Space) or hands-free wake word ("Hey JARVIS")
- 🧠 **Hybrid Intelligence**: Smart routing between fast rule-based parsing and advanced LLM reasoning
- 🛠️ **10+ Built-in Tools**: Filesystem operations, system monitoring, web access, and application control
- 🎨 **Beautiful Visual UI**: Siri-like animated overlay with real-time state feedback
- 🗣️ **Natural Speech**: High-quality Google TTS for natural-sounding responses
- 🐳 **Production Ready**: Fully containerized with Docker Compose
- 🔒 **Privacy First**: Offline speech recognition with local Whisper model

---

## 🚀 Features

### 🎤 Voice Interaction

#### Input Methods
- **Hotkey Activation**: Press `Ctrl+Space` to start listening (works everywhere)
- **Wake Word Detection**: Say "Hey JARVIS" for hands-free activation
- **Smart Recording**: Automatic 5-second recording window with audio buffering

#### Speech Recognition (STT)
- **Engine**: Faster Whisper (OpenAI Whisper optimized)
- **Model**: Base model for accuracy (configurable: tiny/base/small/medium)
- **Device**: CPU with INT8 quantization for efficiency
- **Speed**: ~1-2 seconds transcription time
- **Offline**: Fully local processing, no internet required

#### Text-to-Speech (TTS)
- **Engine**: Google TTS (gTTS)
- **Quality**: Natural-sounding voice
- **Language**: English (US) - configurable
- **Streaming**: Direct audio playback

### 🎨 Visual Feedback

#### Siri-like Animated UI
- **Position**: Top-right corner overlay (always on top)
- **States**:
  - 🟢 **Idle**: Gray pulsing dot (ready state)
  - 🔵 **Listening**: Blue expanding circles (recording)
  - 🟦 **Processing**: Cyan spinning arcs (thinking)
- **Transparency**: 90% opacity, non-intrusive
- **Performance**: 30 FPS smooth animations, minimal resource usage

### 🧠 Intelligence System

#### Hybrid Processing Architecture
The assistant uses an intelligent routing system that chooses the best processing method:

1. **Rule-Based Parser** (Fast Lane)
   - Instant response for simple commands
   - Pattern matching with fuzzy search
   - App control, basic queries
   - Zero latency

2. **LLM Processing** (Smart Lane)
   - Complex natural language understanding
   - Tool calling with text-based format
   - Context-aware responses
   - Conversational personality (JARVIS)
   - Graceful fallback to rules if unavailable

#### Smart Router Logic
```
User Command → Is it simple? → Yes → Rule Parser → Execute
                    ↓ No
            → LLM Available? → Yes → LLM + Tools → Execute
                    ↓ No
            → Fallback to Rules
```

### 🛠️ Comprehensive Tool System

The assistant includes **10 powerful built-in tools** organized into 4 categories:

#### 1. 📁 Filesystem Operations

**`list_files`** - List files and directories
```
✓ "list all files in the current directory"
✓ "show me all Python files"
✓ "list files in /home/user/Documents recursively"
```
- Pattern matching (*.py, *.txt, etc.)
- Recursive search option
- Returns: name, path, type, size

**`read_file`** - Read file contents
```
✓ "read the contents of config.yaml"
✓ "show me what's in README.md"
✓ "read the first 50 lines of main.py"
```
- UTF-8 text file support
- Configurable line limits
- Safe file access

**`search_files`** - Find files by name/pattern
```
✓ "find all files named config.yaml"
✓ "search for Python files in my home directory"
✓ "locate all README files"
```
- Recursive directory search
- Pattern-based matching
- Up to 20 results

#### 2. 🖥️ System Information & Control

**`get_system_info`** - System statistics
```
✓ "what's my CPU usage?"
✓ "how much RAM do I have?"
✓ "show me disk usage"
✓ "tell me about my system"
```
Returns:
- CPU: usage %, core count, frequency
- Memory: total, used, available
- Disk: total, used, free space

**`get_processes`** - Process management
```
✓ "show me running processes"
✓ "list all Firefox processes"
✓ "what processes are using the most CPU?"
```
- Filter by process name
- Shows: PID, CPU%, memory%
- Top 10 by default

**`execute_command`** - Safe command execution
```
✓ "run ls command"
✓ "execute df -h"
✓ "run ps aux"
```
- **Whitelist only**: ls, cat, grep, find, head, tail, wc, echo, pwd, whoami, date, df, du, ps, top, free
- 5-second timeout
- Captures stdout/stderr
- **Security**: No destructive commands allowed

#### 3. 🌐 Web Access

**`search_web`** - Web search via DuckDuckGo
```
✓ "search the web for Python tutorials"
✓ "look up Linux commands"
✓ "find information about Docker"
```
- No API key required
- Returns: titles, snippets, URLs
- Up to 5 results

**`fetch_url`** - Fetch webpage content
```
✓ "fetch the content from example.com"
✓ "get the text from this URL"
```
- HTTP/HTTPS support
- Text extraction
- 10-second timeout

#### 4. 🚀 Application Control

**`open_app`** - Launch any application
```
✓ "open Firefox"
✓ "launch terminal"
✓ "start VS Code"
✓ "open file manager"
```

**Supported Applications** (40+ apps):
- **Browsers**: Firefox, Chrome, Chromium, Brave
- **Editors**: VS Code, Sublime Text, Gedit, Vim
- **Terminals**: GNOME Terminal, Konsole, Alacritty, Kitty
- **File Managers**: Nautilus, Dolphin, Thunar, Nemo
- **Media**: VLC, Spotify, Rhythmbox
- **Communication**: Slack, Discord
- **Office**: LibreOffice, Writer, Calc
- **System**: Settings, Calculator
- And more... (fully configurable)

**`close_app`** - Close running applications
```
✓ "close Firefox"
✓ "quit Chrome"
✓ "kill Spotify"
```

**`run_script`** - Execute shell scripts
```
✓ "run the backup script"
✓ "execute my build script"
```

---

## 📋 Prerequisites

### For Docker Setup (Recommended)
- Docker 20.10+
- Docker Compose 2.0+
- X11 display server (for hotkey support)
- PulseAudio (for audio)

### For Local Setup
- Python 3.11+
- PortAudio
- FFmpeg
- libsndfile1
- Tkinter (usually comes with Python)
- Ollama (for LLM features)

---

## 🐳 Quick Start with Docker (Recommended)

### One-Command Setup

```bash
cd linux-voice-ai
./docker-setup.sh
```

This automated script will:
1. ✅ Allow X11 connections for hotkey support
2. ✅ Build and start Ollama + Voice Assistant containers
3. ✅ Pull the functiongemma:270m LLM model
4. ✅ Verify all services are running
5. ✅ Show you the logs

### Manual Docker Setup

```bash
# 1. Allow X11 connections
xhost +local:docker

# 2. Build and start services
docker-compose up -d

# 3. Pull LLM model
docker exec ollama ollama pull functiongemma:270m

# 4. View logs
docker-compose logs -f voice-assistant

# 5. Stop services
docker-compose down

# 6. Clean up X11 permissions (optional)
xhost -local:docker
```

### Verify Installation

```bash
# Check services are running
docker-compose ps

# Should show:
#   ollama          running  0.0.0.0:11434->11434/tcp
#   linux-voice-ai  running

# Test Ollama API
curl http://localhost:11434/api/tags
```

**📖 See [DOCKER_SETUP.md](DOCKER_SETUP.md) for detailed Docker documentation.**

---

## 💻 Local Development Setup

### Step 1: Install System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    python3-tk
```

#### Fedora
```bash
sudo dnf install -y \
    portaudio-devel \
    libsndfile \
    ffmpeg \
    python3-tkinter
```

#### Arch Linux
```bash
sudo pacman -S \
    portaudio \
    libsndfile \
    ffmpeg \
    tk
```

### Step 2: Install Ollama (for LLM features)

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Pull the model
ollama pull functiongemma:270m
```

### Step 3: Python Environment

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 4: Run the Assistant

```bash
python main.py
```

**📖 See [LOCAL_SETUP.md](LOCAL_SETUP.md) for detailed local setup guide.**

---

## 📖 Usage

### Starting the Assistant

**With Docker:**
```bash
docker-compose up
```

**Locally:**
```bash
python main.py
```

### Activation Methods

#### Method 1: Hotkey (Always Available)
1. Press **Ctrl+Space** anywhere on your system
2. Speak your command (you have 5 seconds)
3. Wait for the visual UI to show "listening" state
4. Listen to the response

#### Method 2: Wake Word (Hands-Free)
1. Say **"Hey JARVIS"**
2. Wait for the activation sound/visual feedback
3. Speak your command
4. Listen to the response

### Visual States

Watch the top-right corner overlay:
- 🟢 **Gray pulsing dot**: Ready/Idle
- 🔵 **Blue pulsing circles**: Listening to you
- 🟦 **Cyan spinning arcs**: Processing your request

### Example Commands

#### Application Control
```
"Open Firefox"
"Launch terminal"
"Start VS Code"
"Close Chrome"
"Quit Spotify"
```

#### System Information
```
"What's my CPU usage?"
"How much RAM do I have?"
"Show me disk space"
"Tell me about my system"
"Show running processes"
```

#### Filesystem Operations
```
"List all files in the current directory"
"Show me all Python files"
"Read the contents of config.yaml"
"Find all README files"
"Search for PDF files in Documents"
```

#### Web Access
```
"Search the web for Python tutorials"
"Look up Docker documentation"
"Find information about Linux"
"Fetch the content from example.com"
```

#### Complex Queries (LLM-powered)
```
"What processes are using the most memory?"
"How much free disk space do I have left?"
"Show me all log files and tell me their sizes"
```

**📖 See [USAGE.md](USAGE.md) for comprehensive usage guide and more examples.**

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interaction Layer                    │
│  ┌──────────────┐          ┌──────────────┐                 │
│  │  Hotkey      │          │  Wake Word   │                 │
│  │  Ctrl+Space  │          │  "Hey JARVIS"│                 │
│  └──────┬───────┘          └──────┬───────┘                 │
└─────────┼──────────────────────────┼─────────────────────────┘
          │                          │
          └───────────┬──────────────┘
                      ▼
          ┌───────────────────────┐
          │   Voice Assistant     │
          │     (main.py)         │
          └───────────┬───────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼              ▼
    ┌───────┐   ┌─────────┐   ┌──────────┐
    │  STT  │   │   UI    │   │   TTS    │
    │Whisper│   │ Siri-UI │   │  gTTS    │
    └───┬───┘   └─────────┘   └────▲─────┘
        │                           │
        ▼                           │
┌───────────────────┐              │
│   Smart Router    │              │
│  (Hybrid System)  │              │
└───────┬───────────┘              │
        │                           │
   ┌────┴────┐                     │
   ▼         ▼                     │
┌──────┐ ┌────────┐               │
│Rules │ │  LLM   │               │
│Parser│ │Ollama  │               │
└──┬───┘ └───┬────┘               │
   │         │                     │
   │    ┌────▼─────┐              │
   │    │ Tool     │              │
   │    │ Executor │              │
   │    └────┬─────┘              │
   │         │                     │
   └────┬────┴──────┬──────┐      │
        ▼           ▼      ▼      │
    ┌───────┐  ┌───────┐ ┌────┐  │
    │  App  │  │System │ │Web │  │
    │Control│  │ Tools │ │API │  │
    └───────┘  └───────┘ └────┘  │
        │          │       │      │
        └──────────┴───────┴──────┘
                   │
                   ▼
            ┌────────────┐
            │  Response  │────────────────┘
            └────────────┘
```

### Component Breakdown

| Component | Purpose | Technology |
|-----------|---------|------------|
| **Audio Recorder** | Capture voice input | sounddevice, scipy |
| **Audio Player** | Play TTS responses | sounddevice |
| **Wake Word Detector** | Hands-free activation | OpenWakeWord, ONNX |
| **STT Engine** | Speech-to-text | Faster Whisper (OpenAI) |
| **TTS Engine** | Text-to-speech | Google TTS |
| **Smart Router** | Command routing logic | Custom Python |
| **Rule Parser** | Fast command parsing | Regex + fuzzy matching |
| **LLM Client** | AI understanding | Ollama API |
| **Tool Registry** | Tool management | Custom framework |
| **Tool Executor** | Execute tool calls | Custom framework |
| **Visual UI** | Real-time feedback | Tkinter |
| **App Controller** | Launch/close apps | subprocess |
| **System Info** | Monitor system | psutil |

### Docker Architecture

```
┌─────────────────────────────────────────┐
│          Host Machine (Linux)            │
│                                          │
│  ┌────────────────┐  ┌────────────────┐ │
│  │ Ollama         │  │ Voice          │ │
│  │ Container      │  │ Assistant      │ │
│  │                │  │ Container      │ │
│  │ Port: 11434    │◄─┤ network: host  │ │
│  │                │  │                │ │
│  │ Model:         │  │ Volumes:       │ │
│  │ functiongemma  │  │ - X11 socket   │ │
│  │ :270m          │  │ - PulseAudio   │ │
│  └────────────────┘  │ - Config       │ │
│         │            │ - Logs         │ │
│         │            └────────────────┘ │
│    ┌────▼────────────────────┐          │
│    │ Shared Volumes:         │          │
│    │ - ollama_models         │          │
│    │ - ./config              │          │
│    │ - ./logs                │          │
│    │ - ./models              │          │
│    └─────────────────────────┘          │
└─────────────────────────────────────────┘
```

---

## 📁 Project Structure

```linux-voice-ai/
├── main.py                   # Main application entry point
├── requirements.txt          # Python dependencies
├── Dockerfile               # Container image definition
├── docker-compose.yml       # Multi-container orchestration
├── docker-setup.sh          # Automated Docker setup script
├── start.sh                 # Quick start script
│
├── config/                  # Configuration files
│   ├── config.yaml         # Main configuration
│   └── commands.yaml       # Command mappings
│
├── audio/                   # Audio I/O modules
│   ├── recorder.py         # Audio recording
│   └── player.py           # Audio playback
│
├── stt/                     # Speech-to-Text
│   ├── whisper_engine.py   # Whisper STT engine
│   └── wake_word.py        # Wake word detection
│
├── tts/                     # Text-to-Speech
│   ├── google_tts.py       # Google TTS implementation
│   └── piper_tts.py        # Piper TTS (alternative)
│
├── llm/                     # LLM Integration
│   ├── ollama_client.py    # Ollama API client
│   ├── router.py           # Smart routing logic
│   └── prompts.py          # System prompts
│
├── parser/                  # Command parsing
│   └── command_parser.py   # Rule-based parser
│
├── tools/                   # Tool system
│   ├── base.py             # Tool base class
│   ├── registry.py         # Tool registry
│   ├── executor.py         # Tool executor
│   └── builtin/            # Built-in tools
│       ├── filesystem.py   # File operations
│       ├── system.py       # System info
│       ├── web.py          # Web access
│       └── apps.py         # App control
│
├── actions/                 # Action handlers
│   ├── apps.py             # App control
│   └── system.py           # System actions
│
├── ui/                      # Visual interface
│   └── siri_ui.py          # Siri-like UI overlay
│
├── utils/                   # Utilities
│   ├── logger.py           # Logging setup
│   └── responses.py        # Response generation
│
├── logs/                    # Log files (generated)
├── temp/                    # Temporary audio files
├── models/                  # Downloaded models
│
└── docs/                    # Documentation
    ├── CAPABILITIES.md      # Feature documentation
    ├── DOCKER_SETUP.md      # Docker guide
    ├── LOCAL_SETUP.md       # Local setup guide
    ├── USAGE.md             # Usage guide
    ├── UI_FEATURE.md        # UI documentation
    └── TEXT_TOOL_CALLING.md # Tool calling docs
```

---

## ⚙️ Configuration

### Main Configuration (`config/config.yaml`)

```yaml
# Audio Settings
audio:
  sample_rate: 16000
  channels: 1
  max_recording_seconds: 10

# Speech-to-Text (Whisper)
stt:
  model_name: "base"        # tiny/base/small/medium
  device: "cpu"             # cpu/cuda
  compute_type: "int8"      # int8/float16/float32
  language: "en"

# Text-to-Speech
tts:
  lang: "en"
  tld: "com"

# LLM Configuration (Ollama)
llm:
  enabled: true
  base_url: "http://localhost:11434"
  model: "functiongemma:270m"
  temperature: 0.7
  max_tokens: 512
  timeout: 30
  fallback_to_rules: true

# Hotkey
hotkey:
  combination: "<ctrl>+<space>"

# Wake Word Detection
wake_word:
  enabled: true
  model: "hey_jarvis"       # hey_jarvis/alexa/hey_mycroft
  threshold: 0.35           # 0.0-1.0 (lower = more sensitive)
  chunk_size: 1280
  
# Logging
logging:
  level: "INFO"             # DEBUG/INFO/WARNING/ERROR
  file: "logs/lva.log"
  max_bytes: 10485760       # 10MB
  backup_count: 5
```

### Application Mappings (`config/commands.yaml`)

Define custom app names and executables:

```yaml
applications:
  myapp:
    executables:
      - "myapp-binary"
      - "alternative-binary"
    synonyms:
      - "my application"
      - "myapp"
```

---

## 🔧 Advanced Features

### Text-Based Tool Calling

The LLM uses a simple, reliable text-based format for tool calls:

**LLM Response:**
```
TOOL: get_system_info(info_type="all")
```

**Parsing:**
- Tool name: `get_system_info`
- Parameters: `{"info_type": "all"}`

**Benefits:**
- ✅ Simple and reliable
- ✅ Works with any LLM
- ✅ No complex function schemas

### Tool Development

Create custom tools by extending the `Tool` base class:

```python
from tools.base import Tool, ToolParameter

class MyCustomTool(Tool):
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "Description of what my tool does"
    
    @property
    def parameters(self) -> List[ToolParameter]:
        return [
            ToolParameter(
                name="param1",
                type="string",
                description="Parameter description",
                required=True
            )
        ]
    
    def execute(self, param1: str, **kwargs) -> Dict[str, Any]:
        # Implementation
        return {"success": True, "result": "..."}
```

Register in `main.py`:
```python
self.tool_registry.register(MyCustomTool())
```

### Wake Word Customization

Change the wake word model in `config/config.yaml`:

```yaml
wake_word:
  model: "alexa"          # Options: hey_jarvis, alexa, hey_mycroft
  threshold: 0.35         # Adjust sensitivity
```

Lower threshold = more sensitive (may have false positives)
Higher threshold = less sensitive (may miss activations)

---

## 🧪 Testing

### Test LLM Integration

```bash
cd tests
python test_llm_integration.py
```

### Test Individual Components

```python
# Test STT
from stt import WhisperEngine
stt = WhisperEngine()
text = stt.transcribe("path/to/audio.wav")

# Test TTS
from tts.google_tts import GoogleTTS
tts = GoogleTTS()
tts.speak("Hello world")

# Test Tools
from tools.builtin import GetSystemInfoTool
tool = GetSystemInfoTool()
result = tool.execute(info_type="cpu")
```

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Hotkey Not Working (Docker)

**Problem:** Ctrl+Space doesn't activate the assistant

**Solutions:**
```bash
# Allow X11 connections
xhost +local:docker

# Check DISPLAY variable
echo $DISPLAY

# Restart with proper X11 mount
docker-compose down
docker-compose up
```

#### 2. No Audio Output

**Problem:** Assistant processes but no voice response

**Solutions:**
```bash
# Check PulseAudio
pulseaudio --check
pulseaudio --start

# Verify PulseAudio socket
ls -la /run/user/$(id -u)/pulse/native

# Check volume
pactl list sinks
```

#### 3. Ollama Connection Failed

**Problem:** LLM features not working

**Solutions:**
```bash
# Check Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama (local)
ollama serve

# Check Ollama container (Docker)
docker logs ollama

# Pull model
ollama pull functiongemma:270m
```

#### 4. Wake Word Not Detecting

**Problem:** "Hey JARVIS" doesn't activate

**Solutions:**
1. Lower threshold in `config/config.yaml`:
   ```yaml
   wake_word:
     threshold: 0.25  # Lower = more sensitive
   ```

2. Check logs:
   ```bash
   tail -f logs/lva.log | grep -i wake
   ```

3. Test microphone:
   ```bash
   arecord -d 5 test.wav
   aplay test.wav
   ```

#### 5. Import Errors

**Problem:** ModuleNotFoundError

**Solutions:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Check Python version
python --version  # Should be 3.11+
```

### Debug Mode

Enable detailed logging in `config/config.yaml`:

```yaml
logging:
  level: "DEBUG"
```

View logs:
```bash
tail -f logs/lva.log
```

---

## 🚀 Performance Tips

### Faster STT

Use the tiny Whisper model for speed (trade-off: less accuracy):

```yaml
stt:
  model_name: "tiny"  # Fastest option
```

### GPU Acceleration

For NVIDIA GPUs:

1. **Docker:**
   ```yaml
   # Uncomment in docker-compose.yml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: 1
             capabilities: [gpu]
   ```

2. **Local:**
   ```yaml
   stt:
     device: "cuda"
     compute_type: "float16"
   ```

### Reduce Memory Usage

```yaml
llm:
  model: "functiongemma:270m"  # Smallest model
  
stt:
  model_name: "tiny"           # Smallest Whisper
  compute_type: "int8"         # Quantized
```

---

## 📊 System Requirements

### Minimum (Docker)
- **CPU**: 2 cores
- **RAM**: 4 GB
- **Disk**: 5 GB free
- **OS**: Linux (any distro with Docker support)

### Recommended
- **CPU**: 4+ cores
- **RAM**: 8 GB
- **Disk**: 10 GB free
- **GPU**: NVIDIA (optional, for acceleration)

### Tested On
- ✅ Ubuntu 20.04, 22.04, 24.04
- ✅ Fedora 38, 39
- ✅ Arch Linux
- ✅ Pop!_OS 22.04
- ✅ Linux Mint 21

---

## 🗺️ Roadmap

### Completed ✅
- [x] Hotkey activation
- [x] Wake word detection ("Hey JARVIS")
- [x] LLM integration (Ollama)
- [x] Tool calling system (10+ tools)
- [x] Visual UI overlay
- [x] Docker containerization
- [x] Hybrid routing (rules + LLM)
- [x] Application control
- [x] System monitoring
- [x] Web access
- [x] Filesystem operations

### Planned 🚧
- [ ] Multi-language support
- [ ] Voice customization
- [ ] Conversation history
- [ ] Custom tool marketplace
- [ ] Mobile app companion
- [ ] Cloud sync (optional)
- [ ] Multi-user support
- [ ] Plugin system
- [ ] Web dashboard

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

### Reporting Bugs
1. Check existing issues
2. Create detailed bug report with:
   - OS and version
   - Python version
   - Docker version (if applicable)
   - Steps to reproduce
   - Error logs

### Suggesting Features
1. Open an issue with `[Feature Request]` tag
2. Describe the feature and use case
3. Provide examples if possible

### Submitting Pull Requests
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests if applicable
5. Commit: `git commit -m 'Add amazing feature'`
6. Push: `git push origin feature/amazing-feature`
7. Open a Pull Request

### Development Setup
```bash
# Clone your fork
git clone https://github.com/yourusername/linux-voice-ai.git

# Create branch
git checkout -b feature/my-feature

# Install in development mode
pip install -e .

# Make changes and test
python main.py

# Run tests
python -m pytest tests/
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

### Technologies & Libraries
- **OpenAI Whisper** - Speech recognition
- **Ollama** - LLM inference
- **Google TTS** - Text-to-speech
- **OpenWakeWord** - Wake word detection
- **psutil** - System monitoring
- **pynput** - Keyboard control
- **sounddevice** - Audio I/O
- **Faster Whisper** - Optimized Whisper

### Inspiration
- Apple Siri - UI design inspiration
- J.A.R.V.I.S. (Iron Man) - Conversational personality
- Mycroft AI - Open source voice assistant
- Home Assistant - Smart home integration ideas

---

## 📞 Support

### Documentation
- [Docker Setup Guide](DOCKER_SETUP.md)
- [Local Setup Guide](LOCAL_SETUP.md)
- [Usage Guide](USAGE.md)
- [Capabilities Reference](CAPABILITIES.md)
- [Tool Calling Documentation](TEXT_TOOL_CALLING.md)
- [UI Feature Guide](UI_FEATURE.md)

### Getting Help
1. Check the [documentation](#documentation)
2. Search [existing issues](https://github.com/yourusername/linux-voice-ai/issues)
3. Create a new issue with details
4. Join our community discussions

---

## 📈 Stats

- **Lines of Code**: ~3,500+
- **Built-in Tools**: 10
- **Supported Apps**: 40+
- **Documentation Pages**: 8
- **Dependencies**: 15+
- **Supported Platforms**: Linux (all major distros)

---

<div align="center">

**Made with ❤️ for the Linux community**

⭐ Star this repo if you find it useful!

[Report Bug](https://github.com/yourusername/linux-voice-ai/issues) · [Request Feature](https://github.com/yourusername/linux-voice-ai/issues) · [Documentation](USAGE.md)

</div>
```linux-voice-ai/
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
