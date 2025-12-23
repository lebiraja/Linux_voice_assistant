# Local Setup Guide - Run Everything on Your Computer

## Quick Start (Local Development)

### Step 1: Install System Dependencies

```bash
# Install system packages
sudo apt-get update
sudo apt-get install -y \
    portaudio19-dev \
    libsndfile1 \
    ffmpeg \
    python3-tk \
    python3-pip \
    python3-venv
```

### Step 2: Create Python Virtual Environment

```bash
cd /home/lebi/projects/VFL/linux-voice-ai

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Install and Start Ollama

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve &

# Pull the model
ollama pull functiongemma:270m

# Verify it's running
curl http://localhost:11434/api/tags
```

### Step 4: Run the Voice Assistant

```bash
# Make sure you're in the project directory with venv activated
cd /home/lebi/projects/VFL/linux-voice-ai
source venv/bin/activate

# Run the assistant
python main.py
```

---

## Complete Setup Steps

### 1. System Dependencies

```bash
# Audio libraries
sudo apt-get install -y portaudio19-dev libsndfile1

# FFmpeg for audio processing
sudo apt-get install -y ffmpeg

# Tkinter for UI
sudo apt-get install -y python3-tk

# Python development tools
sudo apt-get install -y python3-pip python3-venv
```

### 2. Python Environment

```bash
# Navigate to project
cd /home/lebi/projects/VFL/linux-voice-ai

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed faster-whisper sounddevice pynput psutil PyYAML numpy gTTS rapidfuzz scipy soundfile python-dotenv colorama requests
```

### 3. Ollama Setup

#### Install Ollama

```bash
# Download and install
curl -fsSL https://ollama.com/install.sh | sh

# Verify installation
ollama --version
```

#### Start Ollama Server

```bash
# Option 1: Run in background
ollama serve &

# Option 2: Run in separate terminal
# Open new terminal and run:
ollama serve
```

#### Pull the Model

```bash
# Pull functiongemma:270m (optimized for tool calling)
ollama pull functiongemma:270m

# This will download ~270MB
# Wait for completion...

# Verify model is available
ollama list
```

**Expected output:**
```
NAME                    ID              SIZE      MODIFIED
functiongemma:270m      abc123def456    270 MB    2 minutes ago
```

### 4. Verify Configuration

```bash
# Check config file
cat config/config.yaml | grep -A 8 "llm:"
```

**Should show:**
```yaml
llm:
  enabled: true
  provider: "ollama"
  base_url: "http://localhost:11434"
  model: "functiongemma:270m"
  temperature: 0.7
  max_tokens: 512
  timeout: 30
  fallback_to_rules: true
```

### 5. Run the Assistant

```bash
# Activate virtual environment (if not already)
source venv/bin/activate

# Run
python main.py
```

**Expected output:**
```
============================================================
🎙️  Linux Voice AI Assistant v1 (LLM-Powered)
============================================================
🧠 LLM: functiongemma:270m (Hybrid Mode)

Press CTRL+SPACE to speak
Press Ctrl+C to exit
```

---

## Testing

### Test 1: Simple Command (Rules)

1. Press `Ctrl+Space`
2. Say: **"open firefox"**
3. Expected output:
   ```
   🎤 Listening...
   🔄 Transcribing...
   📝 You said: "open firefox"
   🧠 Using: RULES
   ⚙️  Executing: open_app - firefox
   💬 Response: Firefox is now open.
   🔊 Speaking...
   ```

### Test 2: Complex Query (LLM)

1. Press `Ctrl+Space`
2. Say: **"tell me about my system"**
3. Expected output:
   ```
   🎤 Listening...
   🔄 Transcribing...
   📝 You said: "tell me about my system"
   🧠 Using: LLM
   💬 Response: [LLM-generated response about your system]
   🔊 Speaking...
   ```

### Test 3: System Info

1. Press `Ctrl+Space`
2. Say: **"what's my CPU usage"**
3. Should respond with current CPU percentage

---

## Troubleshooting

### Issue: "ModuleNotFoundError"

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: "Ollama not running"

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve &

# Wait a few seconds, then test again
```

### Issue: "Model not found"

```bash
# Pull the model
ollama pull functiongemma:270m

# Verify
ollama list | grep functiongemma
```

### Issue: "No audio input"

```bash
# Test microphone
arecord -d 3 test.wav
aplay test.wav

# Check PulseAudio
pulseaudio --check
```

### Issue: "Hotkey not working"

```bash
# Make sure you have X11 permissions
# Run as your user (not root)
whoami  # Should show your username, not root
```

---

## Daily Usage

### Starting the Assistant

```bash
# Terminal 1: Start Ollama (if not running)
ollama serve

# Terminal 2: Start Voice Assistant
cd /home/lebi/projects/VFL/linux-voice-ai
source venv/bin/activate
python main.py
```

### Stopping the Assistant

```bash
# In the assistant terminal, press Ctrl+C
# Or close the terminal
```

### Updating Dependencies

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

---

## Development Tips

### Enable Debug Logging

Edit `config/config.yaml`:
```yaml
logging:
  level: "DEBUG"  # Change from INFO
```

### View Logs

```bash
# Real-time logs
tail -f logs/lva.log

# All logs
cat logs/lva.log
```

### Test Without Voice

You can test the LLM integration directly:

```python
# In Python shell
source venv/bin/activate
python

>>> from llm import OllamaClient
>>> client = OllamaClient()
>>> result = client.generate("Hello, how are you?", system="You are JARVIS")
>>> print(result['response'])
```

---

## Quick Reference

```bash
# Activate environment
source venv/bin/activate

# Start Ollama
ollama serve &

# Run assistant
python main.py

# View logs
tail -f logs/lva.log

# Stop assistant
Ctrl+C

# Deactivate environment
deactivate
```

---

## Next Steps

Once everything is working:
1. ✅ Test simple commands (rules)
2. ✅ Test complex queries (LLM)
3. ✅ Verify hybrid routing works
4. ➡️ Ready for Phase 2: Tool Calling Framework
