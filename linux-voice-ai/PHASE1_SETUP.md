# Phase 1 Setup Guide - LLM Integration

## Prerequisites

1. **Install Ollama**
   ```bash
   # Download and install Ollama
   curl -fsSL https://ollama.com/install.sh | sh
   
   # Verify installation
   ollama --version
   ```

2. **Start Ollama Service**
   ```bash
   # Start Ollama server
   ollama serve
   ```

3. **Pull the Model**
   ```bash
   # Pull functiongemma:270m (optimized for tool calling)
   ollama pull functiongemma:270m
   
   # Verify model is available
   ollama list
   ```

## Installation

1. **Update Dependencies**
   ```bash
   cd /home/lebi/projects/VFL/linux-voice-ai
   pip install -r requirements.txt
   ```

2. **Verify Configuration**
   ```bash
   # Check that config/config.yaml has LLM section
   cat config/config.yaml | grep -A 8 "llm:"
   ```

## Testing

### Test 1: Ollama Connection
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Should return JSON with available models
```

### Test 2: Simple Commands (Should Use Rules)
```bash
python main.py
# Press Ctrl+Space and say:
# - "open firefox"
# - "close firefox"
# - "what's my CPU usage"

# Expected: "🧠 Using: RULES" in output
```

### Test 3: Complex Queries (Should Use LLM)
```bash
python main.py
# Press Ctrl+Space and say:
# - "tell me about my system"
# - "what can you do for me"
# - "how many CPU cores do I have"

# Expected: "🧠 Using: LLM" in output
```

### Test 4: LLM Fallback
```bash
# Stop Ollama
pkill ollama

# Run assistant
python main.py

# Expected: "⚙️  Mode: Rule-based only (LLM unavailable)"
# Simple commands should still work via rules
```

## Verification Checklist

- [ ] Ollama installed and running
- [ ] functiongemma:270m model downloaded
- [ ] Dependencies installed (requests>=2.31.0)
- [ ] LLM config present in config.yaml
- [ ] Simple commands use rule-based parser
- [ ] Complex queries use LLM
- [ ] Graceful fallback when Ollama unavailable
- [ ] No crashes or errors

## Troubleshooting

### "Ollama not running"
```bash
# Start Ollama in background
ollama serve &

# Or in separate terminal
ollama serve
```

### "Model not found"
```bash
# Pull the model
ollama pull functiongemma:270m

# Check available models
ollama list
```

### "Connection refused"
```bash
# Check if Ollama is listening on correct port
netstat -tuln | grep 11434

# If different port, update config.yaml:
# llm:
#   base_url: "http://localhost:YOUR_PORT"
```

### "LLM responses are slow"
```bash
# functiongemma:270m is optimized for speed
# If still slow, check:
# 1. CPU usage (top)
# 2. Available RAM (free -h)
# 3. Reduce max_tokens in config.yaml
```

## Next Steps

Once Phase 1 is verified:
1. Test with various command types
2. Monitor LLM response quality
3. Adjust temperature/max_tokens if needed
4. Proceed to Phase 2: Tool Calling Framework
