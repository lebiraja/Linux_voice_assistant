# Docker Setup Guide - Phase 1 LLM Integration

## Quick Start (Docker)

### Prerequisites
- Docker and Docker Compose installed
- X11 display server running
- PulseAudio running

### One-Command Setup

```bash
cd /home/lebi/projects/VFL/linux-voice-ai
./docker-setup.sh
```

This script will:
1. Allow X11 connections
2. Build and start Ollama + Voice Assistant containers
3. Pull the functiongemma:270m model
4. Verify everything is running

---

## Manual Setup

### Step 1: Start Services

```bash
# Allow X11 connections
xhost +local:docker

# Start all services
docker-compose up -d
```

### Step 2: Pull LLM Model

```bash
# Pull functiongemma:270m into Ollama container
docker exec ollama ollama pull functiongemma:270m

# Verify model is available
docker exec ollama ollama list
```

### Step 3: Verify

```bash
# Check services are running
docker-compose ps

# Should show:
# - ollama (running on port 11434)
# - linux-voice-ai (running)

# Check Ollama API
curl http://localhost:11434/api/tags
```

---

## Architecture

### Container Setup

```
┌─────────────────────────────────────┐
│         Host Machine                │
│                                     │
│  ┌──────────────┐  ┌─────────────┐ │
│  │   Ollama     │  │ Voice       │ │
│  │  Container   │  │ Assistant   │ │
│  │              │  │ Container   │ │
│  │ Port: 11434  │◄─┤             │ │
│  │              │  │ network:    │ │
│  │ Model:       │  │ host        │ │
│  │ functiongemma│  │             │ │
│  └──────────────┘  └─────────────┘ │
│         │                  │        │
│         │                  │        │
│    ┌────▼──────────────────▼────┐   │
│    │   Shared Volumes:          │   │
│    │   - ollama_models          │   │
│    │   - ./config               │   │
│    │   - ./logs                 │   │
│    └────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Network Configuration

- **Ollama**: Exposed on `localhost:11434`
- **Voice Assistant**: Uses `network_mode: host` for X11/PulseAudio access
- **Communication**: Voice assistant connects to Ollama via `http://localhost:11434`

### Volume Mounts

| Volume | Purpose | Persistence |
|--------|---------|-------------|
| `ollama_models` | LLM model storage | Persistent (Docker volume) |
| `./config` | Configuration files | Host directory |
| `./logs` | Application logs | Host directory |
| `./models` | Whisper models cache | Host directory |
| `/tmp/.X11-unix` | X11 display socket | Host socket |
| `/run/user/1000/pulse` | PulseAudio socket | Host socket |

---

## Usage

### Start the Assistant

```bash
# Start in foreground (see logs)
docker-compose up

# Start in background
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Voice assistant only
docker-compose logs -f voice-assistant

# Ollama only
docker-compose logs -f ollama
```

### Stop Services

```bash
# Stop all
docker-compose down

# Stop but keep volumes
docker-compose stop
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart voice assistant only
docker-compose restart voice-assistant
```

---

## Testing

### Test 1: Ollama Connection

```bash
# From host
curl http://localhost:11434/api/tags

# Should return JSON with models list
```

### Test 2: Model Availability

```bash
# Check model is pulled
docker exec ollama ollama list

# Should show functiongemma:270m
```

### Test 3: Voice Assistant

```bash
# View assistant logs
docker-compose logs -f voice-assistant

# Should see:
# "LLM ready: functiongemma:270m"
# "Smart router initialized (hybrid mode)"
```

### Test 4: End-to-End

1. Ensure services are running: `docker-compose ps`
2. Press `Ctrl+Space` (hotkey)
3. Say: "tell me about my system"
4. Check logs: Should show "🧠 Using: LLM"

---

## Configuration

### Change Ollama Model

```bash
# Pull different model
docker exec ollama ollama pull llama3.2:3b

# Update config/config.yaml
llm:
  model: "llama3.2:3b"

# Restart assistant
docker-compose restart voice-assistant
```

### Enable GPU Support (NVIDIA)

Uncomment in `docker-compose.yml`:

```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

Requires: `nvidia-docker2` installed

### Adjust Resource Limits

Add to `docker-compose.yml`:

```yaml
voice-assistant:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 4G
```

---

## Troubleshooting

### Issue: "Ollama not running"

```bash
# Check Ollama container
docker-compose ps ollama

# If not running, start it
docker-compose up -d ollama

# Check logs
docker-compose logs ollama
```

### Issue: "Model not found"

```bash
# Pull model manually
docker exec ollama ollama pull functiongemma:270m

# Verify
docker exec ollama ollama list
```

### Issue: "Connection refused to Ollama"

```bash
# Check Ollama is listening
docker exec ollama netstat -tuln | grep 11434

# Check from voice-assistant container
docker exec linux-voice-ai curl http://localhost:11434/api/tags
```

### Issue: "X11 connection failed"

```bash
# Re-allow X11
xhost +local:docker

# Check DISPLAY variable
echo $DISPLAY

# Verify in docker-compose.yml:
# environment:
#   - DISPLAY=${DISPLAY}
```

### Issue: "No audio input/output"

```bash
# Check PulseAudio is running
pulseaudio --check

# Check socket path
ls -la /run/user/1000/pulse/native

# Verify volume mount in docker-compose.yml
```

### Issue: "Slow LLM responses"

```bash
# Check Ollama resource usage
docker stats ollama

# Consider:
# 1. Reduce max_tokens in config.yaml
# 2. Use smaller model (functiongemma:270m is already small)
# 3. Enable GPU support if available
```

---

## Maintenance

### Update Ollama

```bash
# Pull latest Ollama image
docker-compose pull ollama

# Restart
docker-compose up -d ollama
```

### Update Voice Assistant

```bash
# Rebuild container
docker-compose build voice-assistant

# Restart
docker-compose up -d voice-assistant
```

### Clean Up

```bash
# Remove all containers and volumes
docker-compose down -v

# Remove unused images
docker image prune -a

# Remove Ollama models (frees space)
docker volume rm linux-voice-ai_ollama_models
```

### Backup Models

```bash
# Backup Ollama models volume
docker run --rm -v linux-voice-ai_ollama_models:/data \
  -v $(pwd):/backup alpine \
  tar czf /backup/ollama_models_backup.tar.gz -C /data .

# Restore
docker run --rm -v linux-voice-ai_ollama_models:/data \
  -v $(pwd):/backup alpine \
  tar xzf /backup/ollama_models_backup.tar.gz -C /data
```

---

## Development Mode

### Live Code Reload

The application code is mounted as a volume, so changes are reflected immediately:

```bash
# Edit code on host
vim llm/prompts.py

# Restart assistant to apply changes
docker-compose restart voice-assistant
```

### Interactive Shell

```bash
# Access voice-assistant container
docker exec -it linux-voice-ai bash

# Access Ollama container
docker exec -it ollama bash

# Run Python interactively
docker exec -it linux-voice-ai python
```

### Debug Mode

```bash
# Enable debug logging
# Edit config/config.yaml:
logging:
  level: "DEBUG"

# Restart
docker-compose restart voice-assistant

# View detailed logs
docker-compose logs -f voice-assistant
```

---

## Performance Tips

### Optimize Ollama

```bash
# Set Ollama environment variables in docker-compose.yml
ollama:
  environment:
    - OLLAMA_NUM_PARALLEL=2
    - OLLAMA_MAX_LOADED_MODELS=1
```

### Reduce Memory Usage

```yaml
llm:
  max_tokens: 256  # Reduce from 512
  timeout: 15      # Reduce timeout
```

### Pre-load Model

```bash
# Keep model in memory
docker exec ollama ollama run functiongemma:270m "hello"
```

---

## Next Steps

1. ✅ Run `./docker-setup.sh`
2. ✅ Verify services with `docker-compose ps`
3. ✅ Test with voice commands
4. ✅ Check logs for any errors
5. ➡️ Proceed to Phase 2: Tool Calling Framework

---

## Quick Reference

```bash
# Start everything
./docker-setup.sh

# View logs
docker-compose logs -f

# Stop everything
docker-compose down

# Restart assistant
docker-compose restart voice-assistant

# Check status
docker-compose ps

# Pull new model
docker exec ollama ollama pull MODEL_NAME

# Interactive shell
docker exec -it linux-voice-ai bash
```
